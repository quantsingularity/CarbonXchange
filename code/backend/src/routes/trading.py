"""
Trading routes for CarbonXchange Backend
Implements comprehensive trading functionality with financial industry standards
"""

from typing import Any
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import and_, asc, desc, or_
from ..models import db
from ..models.trading import (
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Portfolio,
    PortfolioHolding,
    Trade,
    TradeStatus,
)
from ..models.user import User
from ..services.audit_service import AuditService
from ..services.compliance_service import ComplianceService
from ..services.risk_service import RiskService
from ..services.trading_service import TradingService
from ..utils import handle_api_error, paginate_query, validate_request_data

logger = logging.getLogger(__name__)
trading_bp = Blueprint("trading", __name__)
trading_service = TradingService()
risk_service = RiskService()
compliance_service = ComplianceService()
audit_service = AuditService()


@trading_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order() -> Any:
    """Create a new trading order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        required_fields = ["order_type", "side", "quantity", "credit_type"]
        if not validate_request_data(data, required_fields):
            return (jsonify({"error": "Missing required fields"}), 400)
        try:
            order_type = OrderType(data["order_type"])
            side = OrderSide(data["side"])
        except ValueError:
            return (jsonify({"error": "Invalid order type or side"}), 400)
        try:
            quantity = Decimal(str(data["quantity"]))
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except (InvalidOperation, ValueError):
            return (jsonify({"error": "Invalid quantity"}), 400)
        price = None
        if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            if "price" not in data:
                return (jsonify({"error": "Price required for limit orders"}), 400)
            try:
                price = Decimal(str(data["price"]))
                if price <= 0:
                    raise ValueError("Price must be positive")
            except (InvalidOperation, ValueError):
                return (jsonify({"error": "Invalid price"}), 400)
        user = User.query.get(user_id)
        if not user:
            return (jsonify({"error": "User not found"}), 404)
        if not user.is_verified or user.status.value not in ["active"]:
            return (jsonify({"error": "Account not authorized for trading"}), 403)
        risk_check = risk_service.check_order_risk(
            user_id,
            {
                "order_type": order_type.value,
                "side": side.value,
                "quantity": float(quantity),
                "price": float(price) if price else None,
                "credit_type": data["credit_type"],
            },
        )
        if not risk_check["approved"]:
            audit_service.log_event(
                user_id=user_id,
                event_type="order_rejected",
                event_category="trading",
                event_description=f"Order rejected due to risk: {risk_check['reason']}",
                success=False,
            )
            return (jsonify({"error": f"Order rejected: {risk_check['reason']}"}), 400)
        compliance_check = compliance_service.check_order_compliance(
            user_id,
            {
                "order_type": order_type.value,
                "side": side.value,
                "quantity": float(quantity),
                "credit_type": data["credit_type"],
            },
        )
        if not compliance_check["approved"]:
            audit_service.log_event(
                user_id=user_id,
                event_type="order_rejected",
                event_category="compliance",
                event_description=f"Order rejected due to compliance: {compliance_check['reason']}",
                success=False,
            )
            return (
                jsonify({"error": f"Order rejected: {compliance_check['reason']}"}),
                400,
            )
        order_data = {
            "user_id": user_id,
            "order_type": order_type,
            "side": side,
            "quantity": quantity,
            "credit_type": data["credit_type"],
            "price": price,
            "time_in_force": data.get("time_in_force", "GTC"),
            "client_order_id": data.get("client_order_id"),
            "notes": data.get("notes"),
            "risk_limit_checked": True,
            "compliance_checked": True,
        }
        if "vintage_year" in data:
            order_data["vintage_year"] = data["vintage_year"]
        if "project_id" in data:
            order_data["project_id"] = data["project_id"]
        if "stop_price" in data:
            try:
                order_data["stop_price"] = Decimal(str(data["stop_price"]))
            except (InvalidOperation, ValueError):
                return (jsonify({"error": "Invalid stop price"}), 400)
        if "expires_at" in data:
            try:
                order_data["expires_at"] = datetime.fromisoformat(
                    data["expires_at"].replace("Z", "+00:00")
                )
            except ValueError:
                return (jsonify({"error": "Invalid expiry date format"}), 400)
        order = Order(**order_data)
        db.session.add(order)
        db.session.commit()
        try:
            trading_service.submit_order(order)
            order.status = OrderStatus.OPEN
            order.submitted_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to submit order {order.order_id}: {str(e)}")
            order.status = OrderStatus.REJECTED
            order.notes = f"{order.notes or ''}\nRejected: {str(e)}".strip()
            db.session.commit()
        audit_service.log_event(
            user_id=user_id,
            event_type="order_created",
            event_category="trading",
            event_description=f"Order created: {order.order_id}",
            metadata={
                "order_id": order.order_id,
                "side": side.value,
                "quantity": float(quantity),
            },
            success=True,
        )
        return (
            jsonify(
                {"message": "Order created successfully", "order": order.to_dict()}
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_orders() -> Any:
    """Get user's trading orders with filtering and pagination"""
    try:
        user_id = get_jwt_identity()
        query = Order.query.filter_by(user_id=user_id)
        if request.args.get("status"):
            try:
                status = OrderStatus(request.args.get("status"))
                query = query.filter(Order.status == status)
            except ValueError:
                return (jsonify({"error": "Invalid status filter"}), 400)
        if request.args.get("side"):
            try:
                side = OrderSide(request.args.get("side"))
                query = query.filter(Order.side == side)
            except ValueError:
                return (jsonify({"error": "Invalid side filter"}), 400)
        if request.args.get("order_type"):
            try:
                order_type = OrderType(request.args.get("order_type"))
                query = query.filter(Order.order_type == order_type)
            except ValueError:
                return (jsonify({"error": "Invalid order type filter"}), 400)
        if request.args.get("credit_type"):
            query = query.filter(Order.credit_type == request.args.get("credit_type"))
        if request.args.get("vintage_year"):
            try:
                vintage_year = int(request.args.get("vintage_year"))
                query = query.filter(Order.vintage_year == vintage_year)
            except ValueError:
                return (jsonify({"error": "Invalid vintage year"}), 400)
        if request.args.get("start_date"):
            try:
                start_date = datetime.fromisoformat(
                    request.args.get("start_date").replace("Z", "+00:00")
                )
                query = query.filter(Order.created_at >= start_date)
            except ValueError:
                return (jsonify({"error": "Invalid start date format"}), 400)
        if request.args.get("end_date"):
            try:
                end_date = datetime.fromisoformat(
                    request.args.get("end_date").replace("Z", "+00:00")
                )
                query = query.filter(Order.created_at <= end_date)
            except ValueError:
                return (jsonify({"error": "Invalid end date format"}), 400)
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")
        if hasattr(Order, sort_by):
            if sort_order == "asc":
                query = query.order_by(asc(getattr(Order, sort_by)))
            else:
                query = query.order_by(desc(getattr(Order, sort_by)))
        else:
            query = query.order_by(desc(Order.created_at))
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 50)), 100)
        paginated_orders = paginate_query(query, page, per_page)
        return (
            jsonify(
                {
                    "orders": [order.to_dict() for order in paginated_orders.items],
                    "pagination": {
                        "page": paginated_orders.page,
                        "pages": paginated_orders.pages,
                        "per_page": paginated_orders.per_page,
                        "total": paginated_orders.total,
                        "has_next": paginated_orders.has_next,
                        "has_prev": paginated_orders.has_prev,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/orders/<order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id: Any) -> Any:
    """Get specific order details"""
    try:
        user_id = get_jwt_identity()
        order = Order.query.filter_by(order_id=order_id, user_id=user_id).first()
        if not order:
            return (jsonify({"error": "Order not found"}), 404)
        order_dict = order.to_dict(include_sensitive=True)
        order_dict["trades"] = [trade.to_dict() for trade in order.trades]
        return (jsonify({"order": order_dict}), 200)
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/orders/<order_id>", methods=["PUT"])
@jwt_required()
def modify_order(order_id: Any) -> Any:
    """Modify an existing order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        order = Order.query.filter_by(order_id=order_id, user_id=user_id).first()
        if not order:
            return (jsonify({"error": "Order not found"}), 404)
        if not order.is_active:
            return (jsonify({"error": "Cannot modify inactive order"}), 400)
        modifiable_fields = [
            "quantity",
            "price",
            "stop_price",
            "time_in_force",
            "expires_at",
            "notes",
        ]
        for field in modifiable_fields:
            if field in data:
                if field in ["quantity", "price", "stop_price"]:
                    try:
                        value = Decimal(str(data[field]))
                        if value <= 0:
                            return (jsonify({"error": f"Invalid {field}"}), 400)
                        setattr(order, field, value)
                    except (InvalidOperation, ValueError):
                        return (jsonify({"error": f"Invalid {field} format"}), 400)
                elif field == "expires_at":
                    try:
                        value = datetime.fromisoformat(
                            data[field].replace("Z", "+00:00")
                        )
                        setattr(order, field, value)
                    except ValueError:
                        return (jsonify({"error": "Invalid expiry date format"}), 400)
                else:
                    setattr(order, field, data[field])
        if "quantity" in data:
            order.remaining_quantity = order.quantity - order.filled_quantity
            if order.remaining_quantity <= 0:
                return (
                    jsonify(
                        {"error": "New quantity must be greater than filled quantity"}
                    ),
                    400,
                )
        db.session.commit()
        audit_service.log_event(
            user_id=user_id,
            event_type="order_modified",
            event_category="trading",
            event_description=f"Order modified: {order.order_id}",
            metadata={"order_id": order.order_id, "modified_fields": list(data.keys())},
            success=True,
        )
        return (
            jsonify(
                {"message": "Order modified successfully", "order": order.to_dict()}
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error modifying order {order_id}: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/orders/<order_id>", methods=["DELETE"])
@jwt_required()
def cancel_order(order_id: Any) -> Any:
    """Cancel an existing order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        order = Order.query.filter_by(order_id=order_id, user_id=user_id).first()
        if not order:
            return (jsonify({"error": "Order not found"}), 404)
        if not order.is_active:
            return (jsonify({"error": "Cannot cancel inactive order"}), 400)
        reason = data.get("reason", "User requested cancellation")
        order.cancel(reason)
        try:
            trading_service.cancel_order(order)
        except Exception as e:
            logger.warning(f"Failed to notify trading engine of cancellation: {str(e)}")
        db.session.commit()
        audit_service.log_event(
            user_id=user_id,
            event_type="order_cancelled",
            event_category="trading",
            event_description=f"Order cancelled: {order.order_id}",
            metadata={"order_id": order.order_id, "reason": reason},
            success=True,
        )
        return (
            jsonify(
                {"message": "Order cancelled successfully", "order": order.to_dict()}
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/trades", methods=["GET"])
@jwt_required()
def get_trades() -> Any:
    """Get user's trade history with filtering and pagination"""
    try:
        user_id = get_jwt_identity()
        query = db.session.query(Trade).join(
            Order,
            or_(
                and_(Trade.buy_order_id == Order.id, Order.user_id == user_id),
                and_(Trade.sell_order_id == Order.id, Order.user_id == user_id),
            ),
        )
        if request.args.get("status"):
            try:
                status = TradeStatus(request.args.get("status"))
                query = query.filter(Trade.status == status)
            except ValueError:
                return (jsonify({"error": "Invalid status filter"}), 400)
        if request.args.get("vintage_year"):
            try:
                vintage_year = int(request.args.get("vintage_year"))
                query = query.filter(Trade.vintage_year == vintage_year)
            except ValueError:
                return (jsonify({"error": "Invalid vintage year"}), 400)
        if request.args.get("start_date"):
            try:
                start_date = datetime.fromisoformat(
                    request.args.get("start_date").replace("Z", "+00:00")
                )
                query = query.filter(Trade.executed_at >= start_date)
            except ValueError:
                return (jsonify({"error": "Invalid start date format"}), 400)
        if request.args.get("end_date"):
            try:
                end_date = datetime.fromisoformat(
                    request.args.get("end_date").replace("Z", "+00:00")
                )
                query = query.filter(Trade.executed_at <= end_date)
            except ValueError:
                return (jsonify({"error": "Invalid end date format"}), 400)
        sort_by = request.args.get("sort_by", "executed_at")
        sort_order = request.args.get("sort_order", "desc")
        if hasattr(Trade, sort_by):
            if sort_order == "asc":
                query = query.order_by(asc(getattr(Trade, sort_by)))
            else:
                query = query.order_by(desc(getattr(Trade, sort_by)))
        else:
            query = query.order_by(desc(Trade.executed_at))
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 50)), 100)
        paginated_trades = paginate_query(query, page, per_page)
        trades_data = []
        for trade in paginated_trades.items:
            trade_dict = trade.to_dict(include_sensitive=True)
            if trade.buyer_id == user_id:
                trade_dict["user_side"] = "buy"
                trade_dict["user_fee"] = float(trade.buyer_fee)
            else:
                trade_dict["user_side"] = "sell"
                trade_dict["user_fee"] = float(trade.seller_fee)
            trades_data.append(trade_dict)
        return (
            jsonify(
                {
                    "trades": trades_data,
                    "pagination": {
                        "page": paginated_trades.page,
                        "pages": paginated_trades.pages,
                        "per_page": paginated_trades.per_page,
                        "total": paginated_trades.total,
                        "has_next": paginated_trades.has_next,
                        "has_prev": paginated_trades.has_prev,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error fetching trades: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/portfolio", methods=["GET"])
@jwt_required()
def get_portfolio() -> Any:
    """Get user's portfolio summary"""
    try:
        user_id = get_jwt_identity()
        portfolio = Portfolio.query.filter_by(
            user_id=user_id, portfolio_type=PortfolioType.TRADING, is_active=True
        ).first()
        if not portfolio:
            portfolio = Portfolio(
                user_id=user_id,
                name="Trading Portfolio",
                portfolio_type=PortfolioType.TRADING,
            )
            db.session.add(portfolio)
            db.session.commit()
        portfolio.update_valuation()
        db.session.commit()
        holdings = (
            PortfolioHolding.query.filter_by(portfolio_id=portfolio.id)
            .filter(PortfolioHolding.quantity > 0)
            .all()
        )
        portfolio_dict = portfolio.to_dict(include_sensitive=True)
        portfolio_dict["holdings"] = [holding.to_dict() for holding in holdings]
        portfolio_dict["metrics"] = {
            "total_holdings": len(holdings),
            "diversification_score": trading_service.calculate_diversification_score(
                holdings
            ),
            "performance_metrics": trading_service.calculate_performance_metrics(
                user_id, portfolio.id
            ),
        }
        return (jsonify({"portfolio": portfolio_dict}), 200)
    except Exception as e:
        logger.error(f"Error fetching portfolio: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/market-data", methods=["GET"])
@jwt_required()
def get_market_data() -> Any:
    """Get market data and statistics"""
    try:
        market_stats = trading_service.get_market_statistics()
        recent_trades = (
            db.session.query(Trade)
            .filter(Trade.status == TradeStatus.SETTLED)
            .order_by(desc(Trade.executed_at))
            .limit(50)
            .all()
        )
        order_book = trading_service.get_order_book_summary()
        return (
            jsonify(
                {
                    "market_stats": market_stats,
                    "recent_trades": [trade.to_dict() for trade in recent_trades],
                    "order_book": order_book,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/price-history", methods=["GET"])
@jwt_required()
def get_price_history() -> Any:
    """Get price history for carbon credits"""
    try:
        credit_type = request.args.get("credit_type")
        vintage_year = request.args.get("vintage_year")
        period = request.args.get("period", "30d")
        valid_periods = ["1d", "7d", "30d", "90d", "1y"]
        if period not in valid_periods:
            return (jsonify({"error": "Invalid period"}), 400)
        price_history = trading_service.get_price_history(
            credit_type=credit_type,
            vintage_year=int(vintage_year) if vintage_year else None,
            period=period,
        )
        return (
            jsonify(
                {
                    "price_history": price_history,
                    "credit_type": credit_type,
                    "vintage_year": vintage_year,
                    "period": period,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error fetching price history: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/risk-metrics", methods=["GET"])
@jwt_required()
def get_risk_metrics() -> Any:
    """Get user's risk metrics and limits"""
    try:
        user_id = get_jwt_identity()
        risk_metrics = risk_service.get_user_risk_metrics(user_id)
        return (jsonify({"risk_metrics": risk_metrics}), 200)
    except Exception as e:
        logger.error(f"Error fetching risk metrics: {str(e)}")
        return handle_api_error(e)


@trading_bp.route("/compliance-status", methods=["GET"])
@jwt_required()
def get_compliance_status() -> Any:
    """Get user's compliance status"""
    try:
        user_id = get_jwt_identity()
        compliance_status = compliance_service.get_user_compliance_status(user_id)
        return (jsonify({"compliance_status": compliance_status}), 200)
    except Exception as e:
        logger.error(f"Error fetching compliance status: {str(e)}")
        return handle_api_error(e)
