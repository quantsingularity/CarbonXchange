"""
Market routes for CarbonXchange Backend
"""

from flask import Blueprint, jsonify

market_bp = Blueprint("market", __name__)


@market_bp.route("/data", methods=["GET"])
def get_market_data() -> Any:
    """Get market data"""
    return (
        jsonify({"message": "Market data endpoint - implementation in progress"}),
        200,
    )


@market_bp.route("/prices", methods=["GET"])
def get_prices() -> Any:
    """Get price data"""
    return (
        jsonify({"message": "Price data endpoint - implementation in progress"}),
        200,
    )
