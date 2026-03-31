"""
Market routes for CarbonXchange Backend
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from flask import Blueprint, jsonify, request

from ..models.market import MarketData, PriceHistory

logger = logging.getLogger(__name__)
market_bp = Blueprint("market", __name__)


@market_bp.route("/data", methods=["GET"])
def get_market_data() -> Any:
    """Get current market data"""
    symbol = request.args.get("symbol")
    limit = min(request.args.get("limit", 50, type=int), 200)

    query = MarketData.query
    if symbol:
        query = query.filter_by(symbol=symbol)

    market_data = query.order_by(MarketData.timestamp.desc()).limit(limit).all()
    return jsonify(
        {
            "market_data": [m.to_dict() for m in market_data],
            "total": len(market_data),
        }
    )


@market_bp.route("/prices", methods=["GET"])
def get_prices() -> Any:
    """Get price history"""
    symbol = request.args.get("symbol")
    days = request.args.get("days", 30, type=int)
    limit = min(request.args.get("limit", 100, type=int), 500)

    query = PriceHistory.query
    if symbol:
        query = query.filter_by(symbol=symbol)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = query.filter(PriceHistory.timestamp >= cutoff)

    prices = query.order_by(PriceHistory.timestamp.desc()).limit(limit).all()
    return jsonify(
        {
            "prices": [p.to_dict() for p in prices],
            "total": len(prices),
            "symbol": symbol,
            "days": days,
        }
    )


@market_bp.route("/summary", methods=["GET"])
def get_market_summary() -> Any:
    """Get market summary statistics"""

    try:
        latest = MarketData.query.order_by(MarketData.timestamp.desc()).first()
        if not latest:
            return jsonify({"message": "No market data available"}), 200

        return jsonify(
            {
                "latest_price": latest.to_dict() if latest else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Market summary error: {e}")
        return jsonify({"error": "Failed to get market summary"}), 500
