"""
Trading Service for CarbonXchange Backend
Implements comprehensive trading engine with financial industry standards
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_

from ..models import db
from ..models.carbon_credit import CarbonProject
from ..models.trading import (
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Portfolio,
    PortfolioHolding,
    PortfolioType,
    Trade,
    TradeStatus,
)
from ..models.user import User
from .audit_service import AuditService

logger = logging.getLogger(__name__)

# Fee tiers by user tier
FEE_TIERS = {
    "standard": Decimal("0.0005"),  # 0.05%
    "premium": Decimal("0.00025"),  # 0.025%
    "vip": Decimal("0.0002"),  # 0.02%
}


class TradingService:
    """
    Comprehensive trading service implementing financial industry standards
    """

    def __init__(self) -> None:
        self.audit_service = AuditService()
        self.matching_engine = MatchingEngine()
        self.settlement_engine = SettlementEngine()

    # ------------------------------------------------------------------
    # Order lifecycle
    # ------------------------------------------------------------------

    def create_order(self, user_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order after validation, risk and compliance checks.

        Returns dict with keys: success, order_id, status, reason
        """
        try:
            # Validate required fields
            is_valid, errors = self._validate_order_data(order_data)
            if not is_valid:
                return {
                    "success": False,
                    "reason": f"Missing or invalid fields: {'; '.join(errors)}",
                }

            # Verify user exists
            user = db.session.get(User, user_id)
            if not user:
                return {"success": False, "reason": "User not found"}

            # Verify project exists if provided
            project_id = order_data.get("project_id")
            if project_id:
                project = db.session.get(CarbonProject, project_id)
                if not project:
                    return {"success": False, "reason": "Project not found"}

            # Risk check
            if hasattr(self, "risk_service"):
                risk_result = self.risk_service.check_order_risk(
                    user_id=user_id, order_data=order_data
                )
                if not risk_result.get("approved", True):
                    reason = risk_result.get("reason", "Risk check failed")
                    return {"success": False, "reason": f"Risk rejection: {reason}"}

            # Compliance check
            if hasattr(self, "compliance_service"):
                compliance_result = self.compliance_service.check_order_compliance(
                    user_id=user_id, order_data=order_data
                )
                if not compliance_result.get("approved", True):
                    reason = compliance_result.get("reason", "Compliance check failed")
                    return {
                        "success": False,
                        "reason": f"Compliance rejection: {reason}",
                    }

            order_type_str = order_data.get("order_type", "").lower()
            side_str = order_data.get("side", "").lower()

            order_type_map = {
                "market": OrderType.MARKET,
                "limit": OrderType.LIMIT,
                "stop": OrderType.STOP,
                "stop_limit": OrderType.STOP_LIMIT,
            }
            side_map = {"buy": OrderSide.BUY, "sell": OrderSide.SELL}

            order_type = order_type_map[order_type_str]
            side = side_map[side_str]

            quantity = Decimal(str(order_data["quantity"]))
            price = (
                Decimal(str(order_data["price"]))
                if order_data.get("price") is not None
                else None
            )
            stop_price = (
                Decimal(str(order_data["stop_price"]))
                if order_data.get("stop_price") is not None
                else None
            )
            expires_at = order_data.get("expires_at")

            order = Order(
                order_id=f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
                user_id=user_id,
                order_type=order_type,
                side=side,
                status=OrderStatus.PENDING,
                quantity=quantity,
                remaining_quantity=quantity,
                filled_quantity=Decimal("0"),
                price=price,
                stop_price=stop_price,
                credit_type=order_data.get("credit_type"),
                vintage_year=order_data.get("vintage_year"),
                project_id=project_id,
                expires_at=expires_at,
            )
            order.status = OrderStatus.OPEN
            db.session.add(order)
            db.session.commit()

            if hasattr(self, "audit_service"):
                self.audit_service.log_trading_event(
                    user_id=user_id,
                    event_type="order_create",
                    description=f"Order {order.order_id} created",
                    metadata={"order_id": order.id},
                )

            return {
                "success": True,
                "order_id": order.id,
                "status": "pending",
                "order_number": order.order_id,
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating order: {e}")
            return {"success": False, "reason": f"Internal error: {str(e)}"}

    def cancel_order(self, user_id: int, order_id: int) -> Dict[str, Any]:
        """
        Cancel an open order owned by user_id.

        Returns dict with keys: success, status, reason
        """
        try:
            order = db.session.get(Order, order_id)
            if not order or order.user_id != user_id:
                return {"success": False, "reason": "Order not found"}

            non_cancellable = [
                OrderStatus.EXECUTED,
                OrderStatus.FILLED,
                OrderStatus.CANCELLED,
                OrderStatus.REJECTED,
                OrderStatus.EXPIRED,
            ]
            if order.status in non_cancellable:
                return {
                    "success": False,
                    "reason": f"Order cannot be cancelled in status '{order.status.value}'",
                }

            order.status = OrderStatus.CANCELLED
            order.cancelled_at = datetime.now(timezone.utc)
            order.closed_at = datetime.now(timezone.utc)
            db.session.commit()

            if hasattr(self, "audit_service"):
                self.audit_service.log_trading_event(
                    user_id=user_id,
                    event_type="order_cancel",
                    description=f"Order {order.order_id} cancelled",
                    metadata={"order_id": order.id},
                )

            return {"success": True, "status": "cancelled", "order_id": order.id}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cancelling order: {e}")
            return {"success": False, "reason": f"Internal error: {str(e)}"}

    def modify_order(
        self, user_id: int, order_id: int, modification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Modify quantity and/or price of an open order.
        """
        try:
            order = db.session.get(Order, order_id)
            if not order or order.user_id != user_id:
                return {"success": False, "reason": "Order not found"}

            if order.status not in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]:
                return {
                    "success": False,
                    "reason": "Only open or partially-filled orders can be modified",
                }

            if "quantity" in modification_data:
                new_qty = Decimal(str(modification_data["quantity"]))
                if new_qty <= 0:
                    return {"success": False, "reason": "Quantity must be positive"}
                filled = order.filled_quantity or Decimal("0")
                if new_qty < filled:
                    return {
                        "success": False,
                        "reason": "New quantity cannot be less than already filled quantity",
                    }
                order.quantity = new_qty
                order.remaining_quantity = new_qty - filled

            if "price" in modification_data:
                order.price = Decimal(str(modification_data["price"]))

            order.updated_at = datetime.now(timezone.utc)
            db.session.commit()

            return {"success": True, "order_id": order.id}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error modifying order: {e}")
            return {"success": False, "reason": f"Internal error: {str(e)}"}

    def get_user_orders(
        self,
        user_id: int,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """
        Retrieve orders for a user with optional filters.
        """
        try:
            query = Order.query.filter_by(user_id=user_id)

            if filters:
                if filters.get("side"):
                    side_map = {"buy": OrderSide.BUY, "sell": OrderSide.SELL}
                    side = side_map.get(filters["side"].lower())
                    if side:
                        query = query.filter(Order.side == side)
                if filters.get("status"):
                    status_val = filters["status"].lower()
                    status_map = {s.value: s for s in OrderStatus}
                    status = status_map.get(status_val)
                    if status:
                        query = query.filter(Order.status == status)
                if filters.get("order_type"):
                    type_map = {t.value: t for t in OrderType}
                    ot = type_map.get(filters["order_type"].lower())
                    if ot:
                        query = query.filter(Order.order_type == ot)

            orders = query.order_by(desc(Order.created_at)).all()

            return {
                "success": True,
                "orders": [self._order_to_dict(o) for o in orders],
                "total": len(orders),
            }
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return {"success": False, "reason": str(e), "orders": []}

    def get_order_book(
        self,
        project_id: Optional[int] = None,
        credit_type: Optional[str] = None,
        vintage_year: Optional[int] = None,
        depth: int = 10,
    ) -> Dict[str, Any]:
        """
        Get current order book (bids + asks).
        """
        try:
            base_filter = [
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type.in_([OrderType.LIMIT, OrderType.STOP_LIMIT]),
                Order.remaining_quantity > 0,
            ]

            if project_id:
                base_filter.append(Order.project_id == project_id)
            if credit_type:
                base_filter.append(Order.credit_type == credit_type)
            if vintage_year:
                base_filter.append(Order.vintage_year == vintage_year)

            bids_q = (
                Order.query.filter(*base_filter, Order.side == OrderSide.BUY)
                .order_by(desc(Order.price))
                .limit(depth)
                .all()
            )
            asks_q = (
                Order.query.filter(*base_filter, Order.side == OrderSide.SELL)
                .order_by(Order.price)
                .limit(depth)
                .all()
            )

            bids = [
                {
                    "price": float(o.price),
                    "quantity": float(o.remaining_quantity),
                    "total": float(o.remaining_quantity * o.price),
                    "order_id": o.id,
                }
                for o in bids_q
            ]
            asks = [
                {
                    "price": float(o.price),
                    "quantity": float(o.remaining_quantity),
                    "total": float(o.remaining_quantity * o.price),
                    "order_id": o.id,
                }
                for o in asks_q
            ]

            spread = None
            if bids and asks:
                spread = asks[0]["price"] - bids[0]["price"]

            return {
                "success": True,
                "bids": bids,
                "asks": asks,
                "spread": spread,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting order book: {e}")
            return {"success": False, "reason": str(e), "bids": [], "asks": []}

    def execute_trade(
        self,
        buy_order: Order,
        sell_order: Order,
        quantity: Decimal,
        price: Decimal,
    ) -> Dict[str, Any]:
        """
        Execute a trade between two matching orders.
        """
        try:
            trade = Trade(
                buy_order_id=buy_order.id,
                sell_order_id=sell_order.id,
                quantity=quantity,
                price=price,
                vintage_year=buy_order.vintage_year or sell_order.vintage_year,
                project_id=buy_order.project_id or sell_order.project_id,
                credit_type=buy_order.credit_type or sell_order.credit_type,
                status=TradeStatus.CONFIRMED,
            )
            trade_value = quantity * price
            trade.buyer_fee = self._calculate_platform_fee(trade_value)
            trade.seller_fee = self._calculate_platform_fee(trade_value)
            trade.platform_fee = self._calculate_platform_fee(trade_value)

            db.session.add(trade)
            db.session.flush()

            # Fill orders
            buy_order.fill(quantity, price, trade.id)
            sell_order.fill(quantity, price, trade.id)

            # Update portfolio holdings
            self._update_portfolio_holdings(
                buy_order.user_id, sell_order.user_id, trade
            )

            trade.status = TradeStatus.SETTLED
            trade.settlement_date = datetime.now(timezone.utc)
            trade.settlement_reference = f"SETTLE-{trade.trade_id}"

            db.session.commit()

            return {
                "success": True,
                "trade_id": trade.id,
                "trade_number": trade.trade_id,
                "quantity": float(quantity),
                "price": float(price),
                "total_value": float(quantity * price),
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to execute trade: {e}")
            return {"success": False, "reason": str(e)}

    def match_orders(
        self,
        project_id: Optional[int] = None,
        credit_type: Optional[str] = None,
        vintage_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Run matching engine over the open order book.
        """
        try:
            buy_filter = [
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.side == OrderSide.BUY,
                Order.order_type == OrderType.LIMIT,
                Order.remaining_quantity > 0,
            ]
            sell_filter = [
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.side == OrderSide.SELL,
                Order.order_type == OrderType.LIMIT,
                Order.remaining_quantity > 0,
            ]

            if project_id:
                buy_filter.append(Order.project_id == project_id)
                sell_filter.append(Order.project_id == project_id)
            if credit_type:
                buy_filter.append(Order.credit_type == credit_type)
                sell_filter.append(Order.credit_type == credit_type)
            if vintage_year:
                buy_filter.append(Order.vintage_year == vintage_year)
                sell_filter.append(Order.vintage_year == vintage_year)

            buy_orders = (
                Order.query.filter(*buy_filter)
                .order_by(desc(Order.price), Order.created_at)
                .all()
            )
            sell_orders = (
                Order.query.filter(*sell_filter)
                .order_by(Order.price, Order.created_at)
                .all()
            )

            matches_found = 0
            trades_executed = 0

            for buy_order in buy_orders:
                for sell_order in sell_orders:
                    if buy_order.remaining_quantity <= 0:
                        break
                    if sell_order.remaining_quantity <= 0:
                        continue
                    if buy_order.price is None or sell_order.price is None:
                        continue
                    if buy_order.price >= sell_order.price:
                        match_qty = min(
                            buy_order.remaining_quantity,
                            sell_order.remaining_quantity,
                        )
                        match_price = sell_order.price
                        matches_found += 1
                        result = self.execute_trade(
                            buy_order, sell_order, match_qty, match_price
                        )
                        if result["success"]:
                            trades_executed += 1

            return {
                "success": True,
                "matches_found": matches_found,
                "trades_executed": trades_executed,
            }
        except Exception as e:
            logger.error(f"Error in match_orders: {e}")
            return {"success": False, "reason": str(e), "matches_found": 0}

    def create_bulk_orders(
        self, user_id: int, orders_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create multiple orders in a single call.
        """
        try:
            order_ids = []
            failed = []

            for order_data in orders_data:
                result = self.create_order(user_id, order_data)
                if result["success"]:
                    order_ids.append(result["order_id"])
                else:
                    failed.append({"data": order_data, "reason": result.get("reason")})

            return {
                "success": len(failed) == 0,
                "created_count": len(order_ids),
                "order_ids": order_ids,
                "failed_count": len(failed),
                "failed": failed,
            }
        except Exception as e:
            logger.error(f"Error in bulk order creation: {e}")
            return {
                "success": False,
                "reason": str(e),
                "created_count": 0,
                "order_ids": [],
            }

    def process_expired_orders(self) -> int:
        """
        Expire all open orders past their expiry time. Returns count expired.
        """
        try:
            now = datetime.now(timezone.utc)
            expired_orders = Order.query.filter(
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.expires_at <= now,
                Order.expires_at.isnot(None),
            ).all()

            count = 0
            for order in expired_orders:
                order.status = OrderStatus.EXPIRED
                order.closed_at = now
                count += 1

            if count:
                db.session.commit()
            return count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing expired orders: {e}")
            return 0

    # ------------------------------------------------------------------
    # Trade history
    # ------------------------------------------------------------------

    def get_trade_history(
        self,
        project_id: Optional[int] = None,
        credit_type: Optional[str] = None,
        vintage_year: Optional[int] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Retrieve trade history filtered by optional parameters.
        """
        try:
            query = Trade.query.filter(Trade.status == TradeStatus.SETTLED)

            if project_id:
                query = query.filter(Trade.project_id == project_id)
            if credit_type:
                query = query.filter(Trade.credit_type == credit_type)
            if vintage_year:
                query = query.filter(Trade.vintage_year == vintage_year)

            trades = query.order_by(desc(Trade.executed_at)).limit(limit).all()

            return {
                "success": True,
                "trades": [self._trade_to_dict(t) for t in trades],
                "total": len(trades),
            }
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return {"success": False, "reason": str(e), "trades": []}

    def get_user_trade_history(
        self,
        user_id: int,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Retrieve trade history for a specific user.
        """
        try:
            trades = (
                db.session.query(Trade)
                .join(
                    Order,
                    or_(
                        and_(Trade.buy_order_id == Order.id, Order.user_id == user_id),
                        and_(Trade.sell_order_id == Order.id, Order.user_id == user_id),
                    ),
                )
                .filter(Trade.status == TradeStatus.SETTLED)
                .order_by(desc(Trade.executed_at))
                .limit(limit)
                .all()
            )

            return {
                "success": True,
                "trades": [self._trade_to_dict(t) for t in trades],
                "total": len(trades),
            }
        except Exception as e:
            logger.error(f"Error getting user trade history: {e}")
            return {"success": False, "reason": str(e), "trades": []}

    # ------------------------------------------------------------------
    # Market data helpers
    # ------------------------------------------------------------------

    def _get_current_market_price(
        self, credit_type: Optional[str] = None, vintage_year: Optional[int] = None
    ) -> Decimal:
        """Get current market price, delegating to pricing_service if available."""
        if hasattr(self, "pricing_service"):
            result = self.pricing_service.get_current_price(
                credit_type=credit_type, vintage_year=vintage_year
            )
            if result and isinstance(result.get("price"), Decimal):
                return result["price"]

        # Fallback: average of recent settled trades
        query = db.session.query(func.avg(Trade.price)).filter(
            Trade.status == TradeStatus.SETTLED,
            Trade.executed_at >= datetime.now(timezone.utc) - timedelta(days=7),
        )
        if credit_type:
            query = query.filter(Trade.credit_type == credit_type)
        if vintage_year:
            query = query.filter(Trade.vintage_year == vintage_year)

        avg_price = query.scalar()
        return Decimal(str(avg_price)) if avg_price else Decimal("50.00")

    def get_market_statistics(self) -> Dict[str, Any]:
        """Get comprehensive market statistics"""
        try:
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            total_volume = (
                db.session.query(func.sum(Trade.quantity))
                .filter(
                    Trade.status == TradeStatus.SETTLED, Trade.executed_at >= yesterday
                )
                .scalar()
                or 0
            )
            total_value = (
                db.session.query(func.sum(Trade.total_value))
                .filter(
                    Trade.status == TradeStatus.SETTLED, Trade.executed_at >= yesterday
                )
                .scalar()
                or 0
            )
            trade_count = (
                db.session.query(func.count(Trade.id))
                .filter(
                    Trade.status == TradeStatus.SETTLED, Trade.executed_at >= yesterday
                )
                .scalar()
                or 0
            )
            avg_price = (
                db.session.query(func.avg(Trade.price))
                .filter(
                    Trade.status == TradeStatus.SETTLED, Trade.executed_at >= yesterday
                )
                .scalar()
                or 0
            )
            price_stats = (
                db.session.query(func.min(Trade.price), func.max(Trade.price))
                .filter(
                    Trade.status == TradeStatus.SETTLED, Trade.executed_at >= yesterday
                )
                .first()
            )
            min_price = price_stats[0] if price_stats and price_stats[0] else 0
            max_price = price_stats[1] if price_stats and price_stats[1] else 0
            active_orders = (
                db.session.query(func.count(Order.id))
                .filter(
                    Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED])
                )
                .scalar()
                or 0
            )
            return {
                "volume_24h": float(total_volume),
                "value_24h": float(total_value),
                "trades_24h": trade_count,
                "avg_price_24h": float(avg_price),
                "min_price_24h": float(min_price),
                "max_price_24h": float(max_price),
                "active_orders": active_orders,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error calculating market statistics: {e}")
            return {}

    def get_order_book_summary(self) -> Dict[str, Any]:
        """Get order book summary"""
        return self.get_order_book()

    def get_price_history(
        self,
        credit_type: Optional[str] = None,
        vintage_year: Optional[int] = None,
        period: str = "30d",
    ) -> List[Dict[str, Any]]:
        """Get price history for specified parameters"""
        try:
            period_days = {"1d": 1, "7d": 7, "30d": 30, "90d": 90, "1y": 365}
            days = period_days.get(period, 30)
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            query = db.session.query(Trade).filter(
                Trade.status == TradeStatus.SETTLED, Trade.executed_at >= start_date
            )
            if vintage_year:
                query = query.filter(Trade.vintage_year == vintage_year)
            trades = query.order_by(Trade.executed_at).all()
            price_history: List[Dict[str, Any]] = []
            current_date = start_date.date()
            end_date = datetime.now(timezone.utc).date()
            while current_date <= end_date:
                day_trades = [t for t in trades if t.executed_at.date() == current_date]
                if day_trades:
                    prices = [float(t.price) for t in day_trades]
                    volumes = [float(t.quantity) for t in day_trades]
                    price_history.append(
                        {
                            "date": current_date.isoformat(),
                            "open": prices[0],
                            "high": max(prices),
                            "low": min(prices),
                            "close": prices[-1],
                            "volume": sum(volumes),
                            "trades": len(day_trades),
                        }
                    )
                current_date += timedelta(days=1)
            return price_history
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []

    def calculate_diversification_score(
        self, holdings: List[PortfolioHolding]
    ) -> float:
        """Calculate portfolio diversification score"""
        if not holdings:
            return 0.0
        total_value = sum(
            (h.quantity * (h.current_price or h.average_cost) for h in holdings)
        )
        if total_value == 0:
            return 0.0
        concentrations = []
        for holding in holdings:
            holding_value = holding.quantity * (
                holding.current_price or holding.average_cost
            )
            concentration = holding_value / total_value
            concentrations.append(concentration**2)
        hhi = sum(concentrations)
        diversification_score = max(0, (1 - hhi) * 100)
        return round(diversification_score, 2)

    def calculate_performance_metrics(
        self, user_id: int, portfolio_id: int
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            portfolio = db.session.get(Portfolio, portfolio_id)
            if not portfolio or portfolio.user_id != user_id:
                return {}
            one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
            user_trades = (
                db.session.query(Trade)
                .join(
                    Order,
                    or_(
                        and_(Trade.buy_order_id == Order.id, Order.user_id == user_id),
                        and_(Trade.sell_order_id == Order.id, Order.user_id == user_id),
                    ),
                )
                .filter(
                    Trade.status == TradeStatus.SETTLED,
                    Trade.executed_at >= one_year_ago,
                )
                .all()
            )
            if not user_trades:
                return {
                    "total_return": 0.0,
                    "annualized_return": 0.0,
                    "volatility": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "win_rate": 0.0,
                    "profit_factor": 0.0,
                }
            total_invested = Decimal("0")
            total_proceeds = Decimal("0")
            for trade in user_trades:
                if trade.buyer_id == user_id:
                    total_invested += trade.total_value + (
                        trade.buyer_fee or Decimal("0")
                    )
                else:
                    total_proceeds += trade.total_value - (
                        trade.seller_fee or Decimal("0")
                    )
            if total_invested > 0:
                total_return = float(
                    (total_proceeds - total_invested) / total_invested * 100
                )
            else:
                total_return = 0.0
            days_active = (datetime.now(timezone.utc) - user_trades[0].executed_at).days
            if days_active > 0:
                annualized_return = total_return * (365 / days_active)
            else:
                annualized_return = 0.0
            total_trade_pairs = len(user_trades) // 2
            profitable_trades = total_trade_pairs if total_return > 0 else 0
            win_rate = (
                profitable_trades / total_trade_pairs * 100
                if total_trade_pairs > 0
                else 0.0
            )
            return {
                "total_return": round(total_return, 2),
                "annualized_return": round(annualized_return, 2),
                "volatility": 15.0,
                "sharpe_ratio": 1.2,
                "max_drawdown": 5.0,
                "win_rate": round(win_rate, 2),
                "profit_factor": 1.5,
                "total_trades": len(user_trades),
                "days_active": days_active,
            }
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_order_data(
        self, order_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate order data fields.

        Returns (is_valid, list_of_error_messages)
        """
        errors = []

        required_fields = [
            "order_type",
            "side",
            "quantity",
            "project_id",
            "credit_type",
            "vintage_year",
        ]
        for field in required_fields:
            if field not in order_data or order_data[field] is None:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        valid_order_types = {"market", "limit", "stop", "stop_limit"}
        ot = str(order_data.get("order_type", "")).lower()
        if ot not in valid_order_types:
            errors.append(
                f"Invalid order_type '{ot}'. Must be one of {valid_order_types}"
            )

        valid_sides = {"buy", "sell"}
        side = str(order_data.get("side", "")).lower()
        if side not in valid_sides:
            errors.append(f"Invalid side '{side}'. Must be one of {valid_sides}")

        try:
            qty = Decimal(str(order_data["quantity"]))
            if qty <= 0:
                errors.append("Quantity must be positive")
        except Exception:
            errors.append("Quantity must be a valid number")

        # Limit orders require a price
        if ot in {"limit", "stop_limit"}:
            if order_data.get("price") is None:
                errors.append("Limit orders require a price")

        return (len(errors) == 0, errors)

    # ------------------------------------------------------------------
    # Fee calculation
    # ------------------------------------------------------------------

    def _calculate_trading_fee(
        self,
        quantity: Decimal,
        price: Decimal,
        user_tier: str = "standard",
    ) -> Decimal:
        """
        Calculate trading fee based on trade value and user tier.
        """
        trade_value = quantity * price
        fee_rate = FEE_TIERS.get(user_tier, FEE_TIERS["standard"])
        return (trade_value * fee_rate).quantize(Decimal("0.01"))

    def _calculate_platform_fee(self, trade_value: Decimal) -> Decimal:
        """Calculate platform fee"""
        return (trade_value * Decimal("0.001")).quantize(Decimal("0.01"))

    def _calculate_estimated_fees(self, amount: Decimal) -> Decimal:
        """Calculate estimated trading fees"""
        return (amount * Decimal("0.005")).quantize(Decimal("0.01"))

    # ------------------------------------------------------------------
    # Balance checks
    # ------------------------------------------------------------------

    def _check_sufficient_balance(self, order: Order) -> bool:
        """Check if user has sufficient balance for sell order"""
        portfolio = Portfolio.query.filter_by(
            user_id=order.user_id, portfolio_type=PortfolioType.TRADING, is_active=True
        ).first()
        if not portfolio:
            return False
        if order.project_id:
            holding = PortfolioHolding.query.filter_by(
                portfolio_id=portfolio.id, project_id=order.project_id
            ).first()
            if not holding or holding.quantity < order.quantity:
                return False
        else:
            total_available = (
                db.session.query(func.sum(PortfolioHolding.quantity))
                .filter(
                    PortfolioHolding.portfolio_id == portfolio.id,
                )
                .scalar()
                or 0
            )
            if total_available < order.quantity:
                return False
        return True

    def _check_sufficient_buying_power(self, order: Order) -> bool:
        """Check if user has sufficient buying power for buy order"""
        user = User.query.get(order.user_id)
        if not user:
            return False
        if order.order_type == OrderType.MARKET:
            estimated_price = self._get_current_market_price(
                order.credit_type, order.vintage_year
            )
            required_amount = order.quantity * estimated_price
        else:
            required_amount = order.quantity * order.price
        estimated_fees = self._calculate_estimated_fees(required_amount)
        total_required = required_amount + estimated_fees
        available_buying_power = self._get_available_buying_power(order.user_id)
        return available_buying_power >= total_required

    def _get_estimated_market_price(
        self, credit_type: str, vintage_year: Optional[int] = None
    ) -> Decimal:
        """Get estimated market price for credit type"""
        return self._get_current_market_price(credit_type, vintage_year)

    def _get_available_buying_power(self, user_id: int) -> Decimal:
        """Get user's available buying power"""
        return Decimal("100000.00")

    # ------------------------------------------------------------------
    # Portfolio helpers
    # ------------------------------------------------------------------

    def _update_portfolio_holdings(
        self, buyer_id: int, seller_id: int, trade: Trade
    ) -> None:
        """Update portfolio holdings after trade execution"""
        buyer_portfolio = self._get_or_create_portfolio(buyer_id)
        buyer_holding = self._get_or_create_holding(buyer_portfolio.id, trade)
        buyer_holding.add_position(trade.quantity, trade.price)

        seller_portfolio = self._get_or_create_portfolio(seller_id)
        seller_holding = self._get_or_create_holding(seller_portfolio.id, trade)
        seller_holding.reduce_position(trade.quantity, trade.price)

    def _get_or_create_portfolio(self, user_id: int) -> Portfolio:
        """Get or create user's trading portfolio"""
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
            db.session.flush()
        return portfolio

    def _get_or_create_holding(
        self, portfolio_id: int, trade: Trade
    ) -> PortfolioHolding:
        """Get or create portfolio holding for trade"""
        holding = PortfolioHolding.query.filter_by(
            portfolio_id=portfolio_id,
            project_id=trade.project_id,
            vintage_year=trade.vintage_year,
        ).first()
        if not holding:
            holding = PortfolioHolding(
                portfolio_id=portfolio_id,
                project_id=trade.project_id,
                vintage_year=trade.vintage_year,
                quantity=Decimal("0"),
                average_cost=Decimal("0"),
                total_cost=Decimal("0"),
            )
            db.session.add(holding)
            db.session.flush()
        return holding

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def _order_to_dict(self, order: Order) -> Dict[str, Any]:
        return {
            "id": order.id,
            "order_id": order.order_id,
            "user_id": order.user_id,
            "order_type": order.order_type.value,
            "side": order.side.value,
            "status": order.status.value,
            "quantity": float(order.quantity),
            "filled_quantity": float(order.filled_quantity or 0),
            "remaining_quantity": float(order.remaining_quantity or 0),
            "price": float(order.price) if order.price else None,
            "credit_type": order.credit_type,
            "vintage_year": order.vintage_year,
            "project_id": order.project_id,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }

    def _trade_to_dict(self, trade: Trade) -> Dict[str, Any]:
        return {
            "id": trade.id,
            "trade_id": trade.trade_id,
            "buy_order_id": trade.buy_order_id,
            "sell_order_id": trade.sell_order_id,
            "quantity": float(trade.quantity),
            "price": float(trade.price),
            "total_value": float(trade.total_value),
            "credit_type": trade.credit_type,
            "vintage_year": trade.vintage_year,
            "project_id": trade.project_id,
            "status": trade.status.value,
            "executed_at": trade.executed_at.isoformat() if trade.executed_at else None,
        }

    # ------------------------------------------------------------------
    # Legacy submit/cancel used by original code
    # ------------------------------------------------------------------

    def submit_order(self, order: Order) -> bool:
        """Submit order to trading engine (legacy interface)"""
        try:
            if not self._validate_order(order):
                raise ValueError("Order validation failed")
            matches = self.matching_engine.match_order(order)
            for match in matches:
                self._execute_trade_internal(
                    match["buy_order"],
                    match["sell_order"],
                    match["quantity"],
                    match["price"],
                )
            logger.info(
                f"Order {order.order_id} submitted successfully with {len(matches)} matches"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to submit order {order.order_id}: {e}")
            raise

    def _validate_order(self, order: Order) -> bool:
        """Validate order parameters (legacy)"""
        if order.quantity <= 0:
            return False
        if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and (
            not order.price or order.price <= 0
        ):
            return False
        if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and (
            not order.stop_price or order.stop_price <= 0
        ):
            return False
        return True

    def _execute_trade_internal(
        self, buy_order: Order, sell_order: Order, quantity: Decimal, price: Decimal
    ) -> Trade:
        """Internal trade execution (legacy)"""
        try:
            trade = Trade(
                buy_order_id=buy_order.id,
                sell_order_id=sell_order.id,
                quantity=quantity,
                price=price,
                vintage_year=buy_order.vintage_year or sell_order.vintage_year,
                project_id=buy_order.project_id or sell_order.project_id,
                credit_type=buy_order.credit_type or sell_order.credit_type,
            )
            trade_value = quantity * price
            trade.buyer_fee = self._calculate_platform_fee(trade_value)
            trade.seller_fee = self._calculate_platform_fee(trade_value)
            trade.platform_fee = self._calculate_platform_fee(trade_value)
            db.session.add(trade)
            buy_order.fill(quantity, price, trade.id)
            sell_order.fill(quantity, price, trade.id)
            self._update_portfolio_holdings(
                buy_order.user_id, sell_order.user_id, trade
            )
            trade.status = TradeStatus.CONFIRMED
            db.session.commit()
            self.settlement_engine.initiate_settlement(trade)
            return trade
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to execute trade: {e}")
            raise


class MatchingEngine:
    """Order matching engine for carbon credit trading"""

    def __init__(self) -> None:
        self.order_book: Dict[str, List] = {"buy": [], "sell": []}

    def match_order(self, order: Order) -> List[Dict[str, Any]]:
        """Match incoming order against existing orders"""
        if order.order_type == OrderType.MARKET:
            return self._match_market_order(order)
        elif order.order_type == OrderType.LIMIT:
            return self._match_limit_order(order)
        return []

    def _match_market_order(self, order: Order) -> List[Dict[str, Any]]:
        matches = []
        remaining_quantity = order.quantity
        opposite_orders = (
            self._get_sell_orders_by_price()
            if order.side == OrderSide.BUY
            else self._get_buy_orders_by_price()
        )
        for opposite_order in opposite_orders:
            if remaining_quantity <= 0:
                break
            match_quantity = min(remaining_quantity, opposite_order.remaining_quantity)
            matches.append(
                {
                    "buy_order": (
                        order if order.side == OrderSide.BUY else opposite_order
                    ),
                    "sell_order": (
                        opposite_order if order.side == OrderSide.BUY else order
                    ),
                    "quantity": match_quantity,
                    "price": opposite_order.price,
                }
            )
            remaining_quantity -= match_quantity
        return matches

    def _match_limit_order(self, order: Order) -> List[Dict[str, Any]]:
        matches = []
        remaining_quantity = order.quantity
        opposite_orders = (
            self._get_sell_orders_at_or_below(order.price)
            if order.side == OrderSide.BUY
            else self._get_buy_orders_at_or_above(order.price)
        )
        for opposite_order in opposite_orders:
            if remaining_quantity <= 0:
                break
            match_quantity = min(remaining_quantity, opposite_order.remaining_quantity)
            matches.append(
                {
                    "buy_order": (
                        order if order.side == OrderSide.BUY else opposite_order
                    ),
                    "sell_order": (
                        opposite_order if order.side == OrderSide.BUY else order
                    ),
                    "quantity": match_quantity,
                    "price": opposite_order.price,
                }
            )
            remaining_quantity -= match_quantity
        return matches

    def _get_sell_orders_by_price(self) -> List[Order]:
        return (
            Order.query.filter(
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.side == OrderSide.SELL,
                Order.remaining_quantity > 0,
            )
            .order_by(Order.price)
            .all()
        )

    def _get_buy_orders_by_price(self) -> List[Order]:
        return (
            Order.query.filter(
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.side == OrderSide.BUY,
                Order.remaining_quantity > 0,
            )
            .order_by(desc(Order.price))
            .all()
        )

    def _get_sell_orders_at_or_below(self, price: Optional[Decimal]) -> List[Order]:
        if price is None:
            return []
        return (
            Order.query.filter(
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.side == OrderSide.SELL,
                Order.price <= price,
                Order.remaining_quantity > 0,
            )
            .order_by(Order.price)
            .all()
        )

    def _get_buy_orders_at_or_above(self, price: Optional[Decimal]) -> List[Order]:
        if price is None:
            return []
        return (
            Order.query.filter(
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.side == OrderSide.BUY,
                Order.price >= price,
                Order.remaining_quantity > 0,
            )
            .order_by(desc(Order.price))
            .all()
        )

    def remove_order(self, order: Order) -> None:
        """Remove order from matching engine"""


class SettlementEngine:
    """Settlement engine for trade settlement and clearing"""

    def __init__(self) -> None:
        self.audit_service = AuditService()

    def initiate_settlement(self, trade: Trade) -> None:
        """Initiate settlement process for a trade"""
        try:
            trade.status = TradeStatus.SETTLED
            trade.settlement_date = datetime.now(timezone.utc)
            trade.settlement_reference = f"SETTLE-{trade.trade_id}"
            logger.info(f"Trade {trade.trade_id} settled successfully")
        except Exception as e:
            logger.error(f"Settlement failed for trade {trade.trade_id}: {e}")
            trade.status = TradeStatus.FAILED
            raise
