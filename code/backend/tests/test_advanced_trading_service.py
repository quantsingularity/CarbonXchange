"""
Comprehensive test suite for Advanced Trading Service
Tests all trading algorithms, risk management, and portfolio optimization features
"""

import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from models.trading import OrderSide, OrderType
from models.user import User
from services.advanced_trading_service import (
    AdvancedTradingService,
    RiskMetrics,
    TradingAlgorithm,
    TradingSignal,
)


class TestAdvancedTradingService:
    """Test suite for AdvancedTradingService"""

    @pytest.fixture
    def trading_service(self):
        """Create a trading service instance for testing"""
        return AdvancedTradingService()

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.is_kyc_approved = True
        user.risk_level = "medium"
        return user

    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data for testing"""
        dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
        np.random.seed(42)  # For reproducible tests

        # Generate realistic price data with trend and volatility
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = [100]  # Starting price

        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        volumes = np.random.normal(10000, 2000, len(dates))
        volumes = np.maximum(volumes, 1000)  # Ensure positive volumes

        return pd.DataFrame({"timestamp": dates, "close": prices, "volume": volumes})

    def test_twap_order_execution(self, trading_service, mock_user):
        """Test TWAP (Time Weighted Average Price) order execution"""
        with patch.object(
            trading_service, "_get_current_price", return_value=Decimal("85.50")
        ):
            with patch("src.models.db.session") as mock_session:
                # Execute TWAP order
                child_orders = trading_service.execute_twap_order(
                    user_id=mock_user.id,
                    symbol="CARBON_CREDIT_A",
                    total_quantity=Decimal("1000"),
                    side=OrderSide.BUY,
                    duration_minutes=60,
                )

                # Verify child orders were created
                assert len(child_orders) > 0
                assert len(child_orders) <= 20  # Max 20 child orders

                # Verify total quantity is preserved
                total_child_quantity = sum(order.quantity for order in child_orders)
                assert total_child_quantity == Decimal("1000")

                # Verify all orders are buy orders
                assert all(order.side == OrderSide.BUY for order in child_orders)

                # Verify order types are limit orders
                assert all(
                    order.order_type == OrderType.LIMIT for order in child_orders
                )

                # Verify database session was used
                mock_session.add.assert_called()
                mock_session.commit.assert_called()

    def test_vwap_order_execution(self, trading_service, mock_user):
        """Test VWAP (Volume Weighted Average Price) order execution"""
        # Mock volume profile
        volume_profile = {i: 1000 + i * 100 for i in range(24)}

        with patch.object(
            trading_service, "_get_volume_profile", return_value=volume_profile
        ):
            with patch.object(
                trading_service, "_get_current_price", return_value=Decimal("85.50")
            ):
                with patch("src.models.db.session") as mock_session:
                    # Execute VWAP order
                    child_orders = trading_service.execute_vwap_order(
                        user_id=mock_user.id,
                        symbol="CARBON_CREDIT_A",
                        total_quantity=Decimal("1000"),
                        side=OrderSide.SELL,
                        lookback_hours=24,
                    )

                    # Verify child orders were created
                    assert len(child_orders) > 0

                    # Verify all orders are sell orders
                    assert all(order.side == OrderSide.SELL for order in child_orders)

                    # Verify quantities are distributed based on volume
                    total_child_quantity = sum(order.quantity for order in child_orders)
                    assert abs(total_child_quantity - Decimal("1000")) < Decimal(
                        "1"
                    )  # Allow small rounding differences

    def test_iceberg_order_execution(self, trading_service, mock_user):
        """Test iceberg order execution"""
        with patch.object(
            trading_service, "_get_current_price", return_value=Decimal("85.50")
        ):
            with patch("src.models.db.session") as mock_session:
                # Execute iceberg order
                iceberg_order = trading_service.execute_iceberg_order(
                    user_id=mock_user.id,
                    symbol="CARBON_CREDIT_A",
                    total_quantity=Decimal("10000"),
                    side=OrderSide.BUY,
                    visible_quantity=Decimal("1000"),
                )

                # Verify iceberg order properties
                assert iceberg_order.quantity == Decimal("10000")
                assert iceberg_order.iceberg_visible_qty == Decimal("1000")
                assert iceberg_order.iceberg_remaining_qty == Decimal("10000")
                assert iceberg_order.side == OrderSide.BUY
                assert iceberg_order.order_type == OrderType.LIMIT

    def test_momentum_signal_generation(self, trading_service, sample_price_data):
        """Test momentum-based trading signal generation"""
        with patch.object(
            trading_service, "_get_price_history", return_value=sample_price_data
        ):
            signals = trading_service.generate_trading_signals(
                symbol="CARBON_CREDIT_A", algorithm=TradingAlgorithm.MOMENTUM
            )

            # Verify signals were generated
            assert isinstance(signals, list)

            if signals:  # If signals were generated
                signal = signals[0]
                assert isinstance(signal, TradingSignal)
                assert signal.symbol == "CARBON_CREDIT_A"
                assert signal.signal_type in ["buy", "sell", "hold"]
                assert 0 <= signal.strength <= 1
                assert 0 <= signal.confidence <= 1
                assert signal.timestamp is not None

    def test_mean_reversion_signal_generation(self, trading_service, sample_price_data):
        """Test mean reversion trading signal generation"""
        with patch.object(
            trading_service, "_get_price_history", return_value=sample_price_data
        ):
            signals = trading_service.generate_trading_signals(
                symbol="CARBON_CREDIT_A", algorithm=TradingAlgorithm.MEAN_REVERSION
            )

            # Verify signals structure
            assert isinstance(signals, list)

            if signals:
                signal = signals[0]
                assert isinstance(signal, TradingSignal)
                assert signal.symbol == "CARBON_CREDIT_A"
                assert signal.price_target is not None
                assert signal.stop_loss is not None

    def test_portfolio_risk_calculation(self, trading_service, mock_user):
        """Test portfolio risk metrics calculation"""
        # Mock portfolio data
        mock_portfolio = Mock()
        mock_portfolio.id = 1

        with patch("src.models.trading.Portfolio.query") as mock_portfolio_query:
            mock_portfolio_query.filter_by.return_value.first.return_value = (
                mock_portfolio
            )

            with patch.object(
                trading_service, "_get_portfolio_holdings_data"
            ) as mock_holdings:
                mock_holdings.return_value = pd.DataFrame(
                    {
                        "asset": ["CARBON_CREDIT_A", "CARBON_CREDIT_B"],
                        "quantity": [100, 200],
                        "value": [10000, 15000],
                    }
                )

                with patch.object(
                    trading_service, "_calculate_portfolio_returns"
                ) as mock_returns:
                    # Mock returns data (252 trading days)
                    np.random.seed(42)
                    mock_returns.return_value = np.random.normal(0.001, 0.02, 252)

                    # Calculate risk metrics
                    risk_metrics = trading_service.calculate_portfolio_risk(
                        mock_user.id
                    )

                    # Verify risk metrics structure
                    assert isinstance(risk_metrics, RiskMetrics)
                    assert isinstance(risk_metrics.var_95, Decimal)
                    assert isinstance(risk_metrics.var_99, Decimal)
                    assert isinstance(risk_metrics.expected_shortfall, Decimal)
                    assert isinstance(risk_metrics.max_drawdown, Decimal)
                    assert isinstance(risk_metrics.sharpe_ratio, float)
                    assert isinstance(risk_metrics.beta, float)
                    assert isinstance(risk_metrics.volatility, float)

                    # Verify risk metrics are reasonable
                    assert risk_metrics.var_95 < 0  # VaR should be negative
                    assert (
                        risk_metrics.var_99 < risk_metrics.var_95
                    )  # 99% VaR should be more negative
                    assert risk_metrics.volatility > 0  # Volatility should be positive

    def test_portfolio_optimization(self, trading_service, mock_user):
        """Test portfolio optimization using Modern Portfolio Theory"""
        # Mock available assets
        mock_assets = ["CARBON_CREDIT_A", "CARBON_CREDIT_B", "CARBON_CREDIT_C"]

        with patch.object(
            trading_service, "_get_available_assets", return_value=mock_assets
        ):
            # Mock price history for each asset
            def mock_price_history(asset, days):
                np.random.seed(hash(asset) % 2**32)  # Different seed for each asset
                dates = pd.date_range(start="2023-01-01", periods=days, freq="D")
                prices = np.random.normal(100, 10, days)
                prices = np.maximum(prices, 50)  # Ensure positive prices
                return pd.DataFrame({"timestamp": dates, "close": prices})

            with patch.object(
                trading_service, "_get_price_history", side_effect=mock_price_history
            ):
                # Optimize portfolio
                optimized_weights = trading_service.optimize_portfolio(
                    user_id=mock_user.id, risk_tolerance="moderate"
                )

                # Verify optimization results
                assert isinstance(optimized_weights, dict)
                assert len(optimized_weights) == len(mock_assets)

                # Verify weights sum to 1 (approximately)
                total_weight = sum(optimized_weights.values())
                assert abs(total_weight - 1.0) < 0.01

                # Verify all weights are positive
                assert all(weight >= 0 for weight in optimized_weights.values())

                # Verify no single asset exceeds 40%
                assert all(weight <= 0.4 for weight in optimized_weights.values())

    def test_rsi_calculation(self, trading_service):
        """Test RSI (Relative Strength Index) calculation"""
        # Create test price series with known pattern
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])

        rsi = trading_service._calculate_rsi(prices, period=5)

        # Verify RSI is calculated
        assert not rsi.isna().all()

        # Verify RSI values are in valid range (0-100)
        valid_rsi = rsi.dropna()
        assert all(0 <= value <= 100 for value in valid_rsi)

    def test_macd_calculation(self, trading_service):
        """Test MACD calculation"""
        # Create test price series
        prices = pd.Series(range(100, 150))  # Upward trend

        macd, signal = trading_service._calculate_macd(prices)

        # Verify MACD and signal are calculated
        assert not macd.isna().all()
        assert not signal.isna().all()

        # Verify they have the same length
        assert len(macd) == len(signal)
        assert len(macd) == len(prices)

    def test_invalid_order_parameters(self, trading_service, mock_user):
        """Test handling of invalid order parameters"""
        with pytest.raises(ValueError):
            # Test negative quantity
            trading_service.execute_twap_order(
                user_id=mock_user.id,
                symbol="CARBON_CREDIT_A",
                total_quantity=Decimal("-100"),
                side=OrderSide.BUY,
                duration_minutes=60,
            )

        with pytest.raises(ValueError):
            # Test zero duration
            trading_service.execute_twap_order(
                user_id=mock_user.id,
                symbol="CARBON_CREDIT_A",
                total_quantity=Decimal("100"),
                side=OrderSide.BUY,
                duration_minutes=0,
            )

        with pytest.raises(ValueError):
            # Test invalid iceberg parameters
            trading_service.execute_iceberg_order(
                user_id=mock_user.id,
                symbol="CARBON_CREDIT_A",
                total_quantity=Decimal("1000"),
                side=OrderSide.BUY,
                visible_quantity=Decimal("1500"),  # Visible > total
            )

    def test_price_data_validation(self, trading_service):
        """Test price data validation and error handling"""
        # Test with insufficient data
        insufficient_data = pd.DataFrame(
            {
                "timestamp": pd.date_range("2023-01-01", periods=5, freq="D"),
                "close": [100, 101, 102, 103, 104],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )

        with patch.object(
            trading_service, "_get_price_history", return_value=insufficient_data
        ):
            signals = trading_service.generate_trading_signals(
                symbol="CARBON_CREDIT_A", algorithm=TradingAlgorithm.MOMENTUM
            )

            # Should return empty list for insufficient data
            assert signals == []

    def test_risk_metrics_edge_cases(self, trading_service, mock_user):
        """Test risk metrics calculation with edge cases"""
        mock_portfolio = Mock()
        mock_portfolio.id = 1

        with patch("src.models.trading.Portfolio.query") as mock_portfolio_query:
            mock_portfolio_query.filter_by.return_value.first.return_value = (
                mock_portfolio
            )

            with patch.object(
                trading_service, "_get_portfolio_holdings_data"
            ) as mock_holdings:
                mock_holdings.return_value = pd.DataFrame(
                    {"asset": ["CARBON_CREDIT_A"], "quantity": [100], "value": [10000]}
                )

                with patch.object(
                    trading_service, "_calculate_portfolio_returns"
                ) as mock_returns:
                    # Test with zero returns
                    mock_returns.return_value = np.zeros(252)

                    risk_metrics = trading_service.calculate_portfolio_risk(
                        mock_user.id
                    )

                    # Verify handling of zero returns
                    assert risk_metrics.var_95 == Decimal("0")
                    assert risk_metrics.var_99 == Decimal("0")
                    assert risk_metrics.volatility == 0.0

    def test_concurrent_order_execution(self, trading_service, mock_user):
        """Test handling of concurrent order execution"""
        with patch.object(
            trading_service, "_get_current_price", return_value=Decimal("85.50")
        ):
            with patch("src.models.db.session") as mock_session:
                # Simulate concurrent TWAP orders
                orders1 = trading_service.execute_twap_order(
                    user_id=mock_user.id,
                    symbol="CARBON_CREDIT_A",
                    total_quantity=Decimal("1000"),
                    side=OrderSide.BUY,
                    duration_minutes=60,
                )

                orders2 = trading_service.execute_twap_order(
                    user_id=mock_user.id,
                    symbol="CARBON_CREDIT_A",
                    total_quantity=Decimal("500"),
                    side=OrderSide.SELL,
                    duration_minutes=30,
                )

                # Verify both order sets were created
                assert len(orders1) > 0
                assert len(orders2) > 0

                # Verify they have different sides
                assert all(order.side == OrderSide.BUY for order in orders1)
                assert all(order.side == OrderSide.SELL for order in orders2)


class TestTradingSignal:
    """Test suite for TradingSignal class"""

    def test_trading_signal_creation(self):
        """Test TradingSignal creation and validation"""
        signal = TradingSignal(
            symbol="CARBON_CREDIT_A",
            signal_type="buy",
            strength=0.8,
            confidence=0.7,
            price_target=Decimal("90.00"),
            stop_loss=Decimal("80.00"),
        )

        assert signal.symbol == "CARBON_CREDIT_A"
        assert signal.signal_type == "buy"
        assert signal.strength == 0.8
        assert signal.confidence == 0.7
        assert signal.price_target == Decimal("90.00")
        assert signal.stop_loss == Decimal("80.00")
        assert signal.timestamp is not None

    def test_trading_signal_auto_timestamp(self):
        """Test automatic timestamp assignment"""
        before_creation = datetime.now(timezone.utc)

        signal = TradingSignal(
            symbol="CARBON_CREDIT_A", signal_type="sell", strength=0.6, confidence=0.5
        )

        after_creation = datetime.now(timezone.utc)

        assert before_creation <= signal.timestamp <= after_creation


class TestRiskMetrics:
    """Test suite for RiskMetrics class"""

    def test_risk_metrics_creation(self):
        """Test RiskMetrics creation and validation"""
        risk_metrics = RiskMetrics(
            var_95=Decimal("-2.5"),
            var_99=Decimal("-4.2"),
            expected_shortfall=Decimal("-3.1"),
            max_drawdown=Decimal("-0.15"),
            sharpe_ratio=1.34,
            beta=0.87,
            volatility=0.128,
        )

        assert risk_metrics.var_95 == Decimal("-2.5")
        assert risk_metrics.var_99 == Decimal("-4.2")
        assert risk_metrics.expected_shortfall == Decimal("-3.1")
        assert risk_metrics.max_drawdown == Decimal("-0.15")
        assert risk_metrics.sharpe_ratio == 1.34
        assert risk_metrics.beta == 0.87
        assert risk_metrics.volatility == 0.128


@pytest.fixture(scope="session")
def test_database():
    """Set up test database for integration tests"""
    # This would set up a test database in a real implementation


class TestTradingServiceIntegration:
    """Integration tests for trading service with database"""

    @pytest.mark.integration
    def test_full_trading_workflow(self, trading_service, mock_user):
        """Test complete trading workflow from signal generation to execution"""
        # This would be a comprehensive integration test
        # involving real database operations and multiple components

    @pytest.mark.integration
    def test_risk_management_integration(self, trading_service, mock_user):
        """Test integration between trading service and risk management"""
        # This would test the integration with risk management systems


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=src.services.advanced_trading_service",
            "--cov-report=html",
            "--cov-report=term-missing",
        ]
    )
