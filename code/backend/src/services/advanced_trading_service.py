"""
Advanced Trading Service for CarbonXchange Backend
Implements sophisticated trading algorithms and risk management for financial markets
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from flask import current_app
from src.models import db
from src.models.carbon_credit import CarbonCredit
from src.models.market import MarketData, PriceHistory
from src.models.trading import (Order, OrderSide, OrderStatus, OrderType,
                                Portfolio, Trade)
from src.models.user import User
from src.services.pricing_service import PricingService
from src.services.risk_service import RiskService

logger = logging.getLogger(__name__)


class TradingAlgorithm(Enum):
    """Trading algorithm types"""

    TWAP = "twap"  # Time Weighted Average Price
    VWAP = "vwap"  # Volume Weighted Average Price
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"
    MARKET_MAKING = "market_making"
    ARBITRAGE = "arbitrage"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"


class ExecutionStrategy(Enum):
    """Order execution strategies"""

    AGGRESSIVE = "aggressive"  # Market orders, immediate execution
    PASSIVE = "passive"  # Limit orders, wait for fills
    BALANCED = "balanced"  # Mix of market and limit orders
    ICEBERG = "iceberg"  # Large orders split into smaller chunks
    STEALTH = "stealth"  # Minimize market impact


@dataclass
class TradingSignal:
    """Trading signal data structure"""

    symbol: str
    signal_type: str  # buy, sell, hold
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    price_target: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class RiskMetrics:
    """Risk metrics for trading decisions"""

    var_95: Decimal  # Value at Risk 95%
    var_99: Decimal  # Value at Risk 99%
    expected_shortfall: Decimal
    max_drawdown: Decimal
    sharpe_ratio: float
    beta: float
    volatility: float


class AdvancedTradingService:
    """Advanced trading service with sophisticated algorithms"""

    def __init__(self):
        self.risk_service = RiskService()
        self.pricing_service = PricingService()
        self.min_order_size = Decimal("0.01")
        self.max_order_size = Decimal("1000000")
        self.max_position_size = Decimal("5000000")

    def execute_twap_order(
        self,
        user_id: int,
        symbol: str,
        total_quantity: Decimal,
        side: OrderSide,
        duration_minutes: int = 60,
    ) -> List[Order]:
        """Execute Time Weighted Average Price algorithm"""
        try:
            # Validate inputs
            if total_quantity <= 0 or duration_minutes <= 0:
                raise ValueError("Invalid TWAP parameters")

            # Calculate number of child orders
            num_orders = min(duration_minutes // 5, 20)  # Max 20 child orders
            child_quantity = total_quantity / num_orders
            interval_minutes = duration_minutes // num_orders

            child_orders = []
            current_time = datetime.now(timezone.utc)

            for i in range(num_orders):
                # Calculate execution time for this child order
                execution_time = current_time + timedelta(minutes=i * interval_minutes)

                # Get current market price
                current_price = self._get_current_price(symbol)
                if not current_price:
                    logger.error(f"Unable to get price for {symbol}")
                    break

                # Create child order with slight price improvement
                price_adjustment = (
                    Decimal("0.001") if side == OrderSide.BUY else Decimal("-0.001")
                )
                limit_price = current_price + price_adjustment

                child_order = Order(
                    user_id=user_id,
                    order_type=OrderType.LIMIT,
                    side=side,
                    quantity=child_quantity,
                    price=limit_price,
                    time_in_force="GTC",
                    notes=f"TWAP child order {i+1}/{num_orders}",
                )

                db.session.add(child_order)
                child_orders.append(child_order)

            db.session.commit()
            logger.info(
                f"Created {len(child_orders)} TWAP child orders for user {user_id}"
            )
            return child_orders

        except Exception as e:
            logger.error(f"TWAP execution error: {e}")
            db.session.rollback()
            return []

    def execute_vwap_order(
        self,
        user_id: int,
        symbol: str,
        total_quantity: Decimal,
        side: OrderSide,
        lookback_hours: int = 24,
    ) -> List[Order]:
        """Execute Volume Weighted Average Price algorithm"""
        try:
            # Get historical volume profile
            volume_profile = self._get_volume_profile(symbol, lookback_hours)
            if not volume_profile:
                logger.warning(
                    f"No volume profile available for {symbol}, falling back to TWAP"
                )
                return self.execute_twap_order(user_id, symbol, total_quantity, side)

            # Calculate quantity distribution based on volume profile
            total_historical_volume = sum(volume_profile.values())
            child_orders = []

            for hour, volume in volume_profile.items():
                if volume <= 0:
                    continue

                # Calculate quantity for this time period
                volume_weight = volume / total_historical_volume
                child_quantity = total_quantity * Decimal(str(volume_weight))

                if child_quantity < self.min_order_size:
                    continue

                # Get current market price
                current_price = self._get_current_price(symbol)
                if not current_price:
                    continue

                # Create child order
                child_order = Order(
                    user_id=user_id,
                    order_type=OrderType.LIMIT,
                    side=side,
                    quantity=child_quantity,
                    price=current_price,
                    time_in_force="GTC",
                    notes=f"VWAP child order for hour {hour}",
                )

                db.session.add(child_order)
                child_orders.append(child_order)

            db.session.commit()
            logger.info(
                f"Created {len(child_orders)} VWAP child orders for user {user_id}"
            )
            return child_orders

        except Exception as e:
            logger.error(f"VWAP execution error: {e}")
            db.session.rollback()
            return []

    def execute_iceberg_order(
        self,
        user_id: int,
        symbol: str,
        total_quantity: Decimal,
        side: OrderSide,
        visible_quantity: Decimal,
    ) -> Order:
        """Execute iceberg order strategy"""
        try:
            if visible_quantity >= total_quantity:
                raise ValueError("Visible quantity must be less than total quantity")

            # Get current market price
            current_price = self._get_current_price(symbol)
            if not current_price:
                raise ValueError(f"Unable to get price for {symbol}")

            # Create parent iceberg order
            iceberg_order = Order(
                user_id=user_id,
                order_type=OrderType.LIMIT,
                side=side,
                quantity=total_quantity,
                price=current_price,
                time_in_force="GTC",
                notes=f"Iceberg order - visible: {visible_quantity}, total: {total_quantity}",
            )

            # Set custom attributes for iceberg handling
            iceberg_order.iceberg_visible_qty = visible_quantity
            iceberg_order.iceberg_remaining_qty = total_quantity

            db.session.add(iceberg_order)
            db.session.commit()

            logger.info(
                f"Created iceberg order {iceberg_order.order_id} for user {user_id}"
            )
            return iceberg_order

        except Exception as e:
            logger.error(f"Iceberg order execution error: {e}")
            db.session.rollback()
            raise

    def generate_trading_signals(
        self, symbol: str, algorithm: TradingAlgorithm
    ) -> List[TradingSignal]:
        """Generate trading signals using specified algorithm"""
        try:
            # Get historical price data
            price_data = self._get_price_history(symbol, days=30)
            if len(price_data) < 20:
                logger.warning(f"Insufficient price data for {symbol}")
                return []

            signals = []

            if algorithm == TradingAlgorithm.MOMENTUM:
                signals = self._generate_momentum_signals(symbol, price_data)
            elif algorithm == TradingAlgorithm.MEAN_REVERSION:
                signals = self._generate_mean_reversion_signals(symbol, price_data)
            elif algorithm == TradingAlgorithm.ARBITRAGE:
                signals = self._generate_arbitrage_signals(symbol, price_data)
            else:
                logger.warning(f"Algorithm {algorithm} not implemented")

            return signals

        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return []

    def _generate_momentum_signals(
        self, symbol: str, price_data: pd.DataFrame
    ) -> List[TradingSignal]:
        """Generate momentum-based trading signals"""
        signals = []

        try:
            # Calculate technical indicators
            price_data["sma_20"] = price_data["close"].rolling(window=20).mean()
            price_data["sma_50"] = price_data["close"].rolling(window=50).mean()
            price_data["rsi"] = self._calculate_rsi(price_data["close"])
            price_data["macd"], price_data["macd_signal"] = self._calculate_macd(
                price_data["close"]
            )

            latest = price_data.iloc[-1]

            # Momentum signal logic
            signal_strength = 0.0
            signal_type = "hold"

            # SMA crossover
            if latest["sma_20"] > latest["sma_50"]:
                signal_strength += 0.3
                signal_type = "buy"
            elif latest["sma_20"] < latest["sma_50"]:
                signal_strength += 0.3
                signal_type = "sell"

            # RSI momentum
            if latest["rsi"] > 70:
                signal_strength += 0.2 if signal_type == "sell" else -0.2
            elif latest["rsi"] < 30:
                signal_strength += 0.2 if signal_type == "buy" else -0.2

            # MACD momentum
            if latest["macd"] > latest["macd_signal"]:
                signal_strength += 0.2 if signal_type == "buy" else -0.2
            else:
                signal_strength += 0.2 if signal_type == "sell" else -0.2

            # Normalize signal strength
            signal_strength = max(0.0, min(1.0, abs(signal_strength)))
            confidence = signal_strength * 0.8  # Conservative confidence

            if signal_strength > 0.5:
                signal = TradingSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=signal_strength,
                    confidence=confidence,
                    price_target=Decimal(
                        str(latest["close"] * (1.05 if signal_type == "buy" else 0.95))
                    ),
                    stop_loss=Decimal(
                        str(latest["close"] * (0.98 if signal_type == "buy" else 1.02))
                    ),
                )
                signals.append(signal)

        except Exception as e:
            logger.error(f"Momentum signal generation error: {e}")

        return signals

    def _generate_mean_reversion_signals(
        self, symbol: str, price_data: pd.DataFrame
    ) -> List[TradingSignal]:
        """Generate mean reversion trading signals"""
        signals = []

        try:
            # Calculate Bollinger Bands
            price_data["sma_20"] = price_data["close"].rolling(window=20).mean()
            price_data["std_20"] = price_data["close"].rolling(window=20).std()
            price_data["bb_upper"] = price_data["sma_20"] + (price_data["std_20"] * 2)
            price_data["bb_lower"] = price_data["sma_20"] - (price_data["std_20"] * 2)

            latest = price_data.iloc[-1]
            current_price = latest["close"]

            # Mean reversion logic
            signal_strength = 0.0
            signal_type = "hold"

            # Price relative to Bollinger Bands
            if current_price <= latest["bb_lower"]:
                signal_type = "buy"
                signal_strength = min(
                    1.0, (latest["bb_lower"] - current_price) / latest["bb_lower"]
                )
            elif current_price >= latest["bb_upper"]:
                signal_type = "sell"
                signal_strength = min(
                    1.0, (current_price - latest["bb_upper"]) / latest["bb_upper"]
                )

            # Distance from mean
            distance_from_mean = (
                abs(current_price - latest["sma_20"]) / latest["sma_20"]
            )
            if distance_from_mean > 0.02:  # 2% deviation
                signal_strength += distance_from_mean

            signal_strength = min(1.0, signal_strength)
            confidence = signal_strength * 0.7  # Mean reversion can be risky

            if signal_strength > 0.4:
                signal = TradingSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=signal_strength,
                    confidence=confidence,
                    price_target=Decimal(str(latest["sma_20"])),  # Target mean
                    stop_loss=Decimal(
                        str(current_price * (0.97 if signal_type == "buy" else 1.03))
                    ),
                )
                signals.append(signal)

        except Exception as e:
            logger.error(f"Mean reversion signal generation error: {e}")

        return signals

    def _generate_arbitrage_signals(
        self, symbol: str, price_data: pd.DataFrame
    ) -> List[TradingSignal]:
        """Generate arbitrage trading signals"""
        signals = []

        try:
            # This would typically compare prices across different exchanges
            # For now, we'll implement a simple statistical arbitrage

            # Calculate price spreads and correlations
            price_data["returns"] = price_data["close"].pct_change()
            price_data["volatility"] = price_data["returns"].rolling(window=20).std()

            latest = price_data.iloc[-1]

            # Look for unusual price movements that might indicate arbitrage opportunities
            recent_volatility = latest["volatility"]
            avg_volatility = price_data["volatility"].mean()

            if recent_volatility > avg_volatility * 1.5:
                # High volatility might indicate arbitrage opportunity
                signal = TradingSignal(
                    symbol=symbol,
                    signal_type="buy",  # Simplified logic
                    strength=0.6,
                    confidence=0.4,  # Lower confidence for arbitrage
                    price_target=Decimal(str(latest["close"] * 1.02)),
                )
                signals.append(signal)

        except Exception as e:
            logger.error(f"Arbitrage signal generation error: {e}")

        return signals

    def calculate_portfolio_risk(self, user_id: int) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            # Get user's portfolio
            portfolio = Portfolio.query.filter_by(user_id=user_id).first()
            if not portfolio:
                raise ValueError(f"No portfolio found for user {user_id}")

            # Get portfolio holdings and historical returns
            holdings_data = self._get_portfolio_holdings_data(portfolio.id)
            if not holdings_data:
                raise ValueError("No holdings data available")

            # Calculate returns
            returns = self._calculate_portfolio_returns(holdings_data)

            # Calculate VaR (Value at Risk)
            var_95 = Decimal(str(np.percentile(returns, 5)))
            var_99 = Decimal(str(np.percentile(returns, 1)))

            # Calculate Expected Shortfall (Conditional VaR)
            expected_shortfall = Decimal(
                str(np.mean(returns[returns <= float(var_95)]))
            )

            # Calculate Maximum Drawdown
            cumulative_returns = (1 + pd.Series(returns)).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = Decimal(str(drawdown.min()))

            # Calculate Sharpe Ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02 / 252  # Daily risk-free rate
            excess_returns = returns - risk_free_rate
            sharpe_ratio = (
                np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
            )

            # Calculate Beta (relative to market - simplified)
            beta = 1.0  # Placeholder - would need market benchmark

            # Calculate Volatility
            volatility = np.std(returns) * np.sqrt(252)  # Annualized

            return RiskMetrics(
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                beta=beta,
                volatility=volatility,
            )

        except Exception as e:
            logger.error(f"Portfolio risk calculation error: {e}")
            raise

    def optimize_portfolio(
        self,
        user_id: int,
        target_return: float = None,
        risk_tolerance: str = "moderate",
    ) -> Dict[str, float]:
        """Optimize portfolio allocation using Modern Portfolio Theory"""
        try:
            # Get available assets and their historical returns
            available_assets = self._get_available_assets()
            if len(available_assets) < 2:
                raise ValueError("Need at least 2 assets for optimization")

            # Get historical returns for all assets
            returns_data = {}
            for asset in available_assets:
                price_history = self._get_price_history(asset, days=252)  # 1 year
                if len(price_history) > 20:
                    returns = price_history["close"].pct_change().dropna()
                    returns_data[asset] = returns

            if len(returns_data) < 2:
                raise ValueError("Insufficient price history for optimization")

            # Create returns matrix
            returns_df = pd.DataFrame(returns_data)

            # Calculate expected returns and covariance matrix
            expected_returns = returns_df.mean() * 252  # Annualized
            cov_matrix = returns_df.cov() * 252  # Annualized

            # Set risk tolerance parameters
            risk_params = {
                "conservative": {"max_volatility": 0.10, "min_return": 0.05},
                "moderate": {"max_volatility": 0.15, "min_return": 0.08},
                "aggressive": {"max_volatility": 0.25, "min_return": 0.12},
            }

            params = risk_params.get(risk_tolerance, risk_params["moderate"])

            # Simple equal-weight optimization (placeholder for more sophisticated methods)
            num_assets = len(returns_data)
            equal_weights = {asset: 1.0 / num_assets for asset in returns_data.keys()}

            # Apply basic constraints
            optimized_weights = {}
            for asset, weight in equal_weights.items():
                # Ensure no single asset exceeds 40% allocation
                optimized_weights[asset] = min(weight, 0.4)

            # Normalize weights to sum to 1
            total_weight = sum(optimized_weights.values())
            for asset in optimized_weights:
                optimized_weights[asset] /= total_weight

            logger.info(f"Portfolio optimization completed for user {user_id}")
            return optimized_weights

        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            raise

    def _get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price for symbol"""
        try:
            market_data = MarketData.query.filter_by(symbol=symbol).first()
            return market_data.current_price if market_data else None
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None

    def _get_volume_profile(self, symbol: str, hours: int) -> Dict[int, float]:
        """Get volume profile for the last N hours"""
        try:
            # This would typically query historical volume data
            # For now, return a mock profile
            return {hour: 1000.0 + (hour * 100) for hour in range(24)}
        except Exception as e:
            logger.error(f"Error getting volume profile for {symbol}: {e}")
            return {}

    def _get_price_history(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get price history as pandas DataFrame"""
        try:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)

            price_history = (
                PriceHistory.query.filter(
                    PriceHistory.symbol == symbol,
                    PriceHistory.timestamp >= start_date,
                    PriceHistory.timestamp <= end_date,
                )
                .order_by(PriceHistory.timestamp)
                .all()
            )

            if not price_history:
                # Generate mock data for testing
                dates = pd.date_range(start=start_date, end=end_date, freq="D")
                prices = np.random.normal(100, 5, len(dates))  # Mock price data
                return pd.DataFrame(
                    {
                        "timestamp": dates,
                        "close": prices,
                        "volume": np.random.normal(1000, 200, len(dates)),
                    }
                )

            data = []
            for record in price_history:
                data.append(
                    {
                        "timestamp": record.timestamp,
                        "close": float(record.close_price),
                        "volume": float(record.volume or 0),
                    }
                )

            return pd.DataFrame(data)

        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}")
            return pd.DataFrame()

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(
        self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and signal line"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd, signal_line

    def _get_portfolio_holdings_data(self, portfolio_id: int) -> Optional[pd.DataFrame]:
        """Get portfolio holdings data"""
        try:
            # This would query actual holdings data
            # For now, return mock data
            return pd.DataFrame(
                {
                    "asset": ["CARBON_CREDIT_A", "CARBON_CREDIT_B"],
                    "quantity": [100, 200],
                    "value": [10000, 15000],
                }
            )
        except Exception as e:
            logger.error(f"Error getting portfolio holdings data: {e}")
            return None

    def _calculate_portfolio_returns(self, holdings_data: pd.DataFrame) -> np.ndarray:
        """Calculate portfolio returns"""
        try:
            # Mock returns calculation
            return np.random.normal(0.001, 0.02, 252)  # Daily returns for 1 year
        except Exception as e:
            logger.error(f"Error calculating portfolio returns: {e}")
            return np.array([])

    def _get_available_assets(self) -> List[str]:
        """Get list of available assets for trading"""
        try:
            # Query available carbon credits
            credits = CarbonCredit.query.filter_by(is_active=True).all()
            return [
                f"CARBON_{credit.id}" for credit in credits[:10]
            ]  # Limit to 10 assets
        except Exception as e:
            logger.error(f"Error getting available assets: {e}")
            return [
                "CARBON_CREDIT_A",
                "CARBON_CREDIT_B",
                "CARBON_CREDIT_C",
            ]  # Mock data
