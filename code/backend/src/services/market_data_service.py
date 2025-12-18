"""
Market Data Service for CarbonXchange Backend
Handles market data collection, processing, and analytics
"""

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from ..models import db
from ..models.market import MarketData, PriceHistory
from ..models.trading import Trade, TradeStatus

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for market data management"""

    def __init__(self) -> None:
        pass

    def get_current_prices(
        self, credit_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get current market prices"""
        try:
            query = MarketData.query

            if credit_types:
                query = query.filter(MarketData.credit_type.in_(credit_types))

            market_data = query.all()

            prices = {}
            for data in market_data:
                prices[data.credit_type] = {
                    "price": float(data.current_price),
                    "volume_24h": float(data.volume_24h),
                    "change_24h": float(data.price_change_24h),
                    "timestamp": data.updated_at.isoformat(),
                }

            return prices
        except Exception as e:
            logger.error(f"Error getting current prices: {e}")
            return {}

    def get_price_history(
        self,
        credit_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1d",
    ) -> List[Dict[str, Any]]:
        """Get historical price data"""
        try:
            query = PriceHistory.query.filter_by(credit_type=credit_type)

            if start_date:
                query = query.filter(PriceHistory.timestamp >= start_date)
            if end_date:
                query = query.filter(PriceHistory.timestamp <= end_date)

            history = query.order_by(PriceHistory.timestamp).all()

            return [
                {
                    "timestamp": h.timestamp.isoformat(),
                    "open": float(h.open_price),
                    "high": float(h.high_price),
                    "low": float(h.low_price),
                    "close": float(h.close_price),
                    "volume": float(h.volume),
                }
                for h in history
            ]
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []

    def calculate_market_statistics(self, credit_type: str) -> Dict[str, Any]:
        """Calculate market statistics for a credit type"""
        try:
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

            trades = Trade.query.filter(
                Trade.status == TradeStatus.SETTLED,
                Trade.executed_at >= thirty_days_ago,
            ).all()

            if not trades:
                return {"error": "Insufficient data"}

            prices = [float(t.price) for t in trades]
            volumes = [float(t.quantity) for t in trades]

            return {
                "average_price": sum(prices) / len(prices),
                "min_price": min(prices),
                "max_price": max(prices),
                "total_volume": sum(volumes),
                "trade_count": len(trades),
                "period_days": 30,
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {"error": str(e)}

    def update_market_data(self, credit_type: str, price_data: Dict[str, Any]) -> bool:
        """Update market data for a credit type"""
        try:
            market_data = MarketData.query.filter_by(credit_type=credit_type).first()

            if not market_data:
                market_data = MarketData(credit_type=credit_type)
                db.session.add(market_data)

            market_data.current_price = Decimal(str(price_data.get("price", 0)))
            market_data.volume_24h = Decimal(str(price_data.get("volume", 0)))
            market_data.price_change_24h = Decimal(str(price_data.get("change", 0)))
            market_data.updated_at = datetime.now(timezone.utc)

            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
            db.session.rollback()
            return False

    def record_price_history(
        self,
        credit_type: str,
        timestamp: datetime,
        open_price: Decimal,
        high_price: Decimal,
        low_price: Decimal,
        close_price: Decimal,
        volume: Decimal,
    ) -> bool:
        """Record price history data point"""
        try:
            price_history = PriceHistory(
                credit_type=credit_type,
                timestamp=timestamp,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
            )
            db.session.add(price_history)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error recording price history: {e}")
            db.session.rollback()
            return False
