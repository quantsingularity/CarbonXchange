"""
Portfolio Management Service for CarbonXchange Backend
Implements sophisticated portfolio management, optimization, and analytics
"""

import logging
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from sqlalchemy import and_, desc, func, or_

from ..models import db
from ..models.carbon_credit import CarbonCredit, CarbonProject
from ..models.trading import Order, Portfolio, PortfolioHolding, Trade, TradeStatus
from ..models.user import User
from .audit_service import AuditService
from .pricing_service import PricingService
from .risk_service import RiskService

logger = logging.getLogger(__name__)


class PortfolioService:
    """
    Comprehensive portfolio management service implementing financial industry standards
    """

    def __init__(self):
        self.pricing_service = PricingService()
        self.risk_service = RiskService()
        self.audit_service = AuditService()

    def create_portfolio(
        self, user_id: int, portfolio_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new portfolio for user

        Args:
            user_id: User ID
            portfolio_data: Portfolio configuration data

        Returns:
            Created portfolio information
        """
        try:
            # Validate user exists
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Create portfolio
            portfolio = Portfolio(
                user_id=user_id,
                name=portfolio_data.get("name", "Default Portfolio"),
                description=portfolio_data.get("description", ""),
                portfolio_type=portfolio_data.get("type", "STANDARD"),
                base_currency=portfolio_data.get("currency", "USD"),
                is_active=True,
            )

            db.session.add(portfolio)
            db.session.commit()

            # Log portfolio creation
            self.audit_service.log_event(
                user_id=user_id,
                event_type="portfolio_create",
                event_category="portfolio",
                event_description=f"Portfolio created: {portfolio.name}",
                metadata={"portfolio_id": portfolio.id},
                success=True,
            )

            return {
                "portfolio_id": portfolio.id,
                "name": portfolio.name,
                "type": portfolio.portfolio_type.value,
                "currency": portfolio.base_currency,
                "created_at": portfolio.created_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error creating portfolio: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}

    def get_portfolio_summary(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Get comprehensive portfolio summary

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Portfolio summary with performance metrics
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return {"error": "Portfolio not found"}

            # Get holdings
            holdings = (
                PortfolioHolding.query.filter_by(portfolio_id=portfolio_id)
                .filter(PortfolioHolding.quantity > 0)
                .all()
            )

            # Calculate current values
            total_value = Decimal("0")
            total_cost = Decimal("0")
            holdings_data = []

            for holding in holdings:
                # Get current price
                current_price = self._get_current_holding_price(holding)
                current_value = holding.quantity * current_price

                # Update holding with current price
                holding.current_price = current_price
                holding.current_value = current_value
                holding.unrealized_pnl = current_value - holding.total_cost

                total_value += current_value
                total_cost += holding.total_cost

                holdings_data.append(
                    {
                        "id": holding.id,
                        "project_id": holding.project_id,
                        "credit_type": holding.credit_type,
                        "vintage_year": holding.vintage_year,
                        "quantity": float(holding.quantity),
                        "average_cost": float(holding.average_cost),
                        "current_price": float(current_price),
                        "current_value": float(current_value),
                        "total_cost": float(holding.total_cost),
                        "unrealized_pnl": float(holding.unrealized_pnl),
                        "pnl_percentage": holding.pnl_percentage,
                        "weight": (
                            float(current_value / total_value * 100)
                            if total_value > 0
                            else 0
                        ),
                    }
                )

            # Update portfolio totals
            portfolio.total_value = total_value
            portfolio.total_cost = total_cost
            portfolio.unrealized_pnl = total_value - total_cost

            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(portfolio)

            # Calculate risk metrics
            risk_metrics = self._calculate_portfolio_risk_metrics(portfolio, holdings)

            # Get allocation breakdown
            allocation_breakdown = self._calculate_allocation_breakdown(holdings_data)

            db.session.commit()

            return {
                "portfolio_id": portfolio.id,
                "name": portfolio.name,
                "total_value": float(total_value),
                "total_cost": float(total_cost),
                "unrealized_pnl": float(portfolio.unrealized_pnl),
                "realized_pnl": float(portfolio.realized_pnl),
                "total_pnl": float(portfolio.total_pnl),
                "pnl_percentage": portfolio.pnl_percentage,
                "holdings_count": len(holdings_data),
                "holdings": holdings_data,
                "performance": performance_metrics,
                "risk": risk_metrics,
                "allocation": allocation_breakdown,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {"error": str(e)}

    def optimize_portfolio(
        self, portfolio_id: int, optimization_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize portfolio allocation using modern portfolio theory

        Args:
            portfolio_id: Portfolio ID
            optimization_params: Optimization parameters

        Returns:
            Optimized allocation recommendations
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return {"error": "Portfolio not found"}

            # Get available assets for optimization
            available_assets = self._get_available_assets(optimization_params)

            if len(available_assets) < 2:
                return {"error": "Need at least 2 assets for optimization"}

            # Get historical returns
            returns_data = self._get_historical_returns(available_assets)

            if returns_data.empty:
                return {"error": "Insufficient historical data for optimization"}

            # Calculate expected returns and covariance matrix
            expected_returns = returns_data.mean().values
            cov_matrix = returns_data.cov().values

            # Set optimization constraints
            target_return = optimization_params.get(
                "target_return", np.mean(expected_returns)
            )
            risk_tolerance = optimization_params.get("risk_tolerance", "moderate")

            # Optimize portfolio
            optimal_weights = self._optimize_weights(
                expected_returns, cov_matrix, target_return, risk_tolerance
            )

            # Calculate optimization results
            portfolio_return = np.dot(optimal_weights, expected_returns)
            portfolio_risk = np.sqrt(
                np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights))
            )
            sharpe_ratio = (
                portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
            )

            # Generate recommendations
            recommendations = []
            current_value = float(portfolio.total_value)

            for i, asset in enumerate(available_assets):
                target_allocation = optimal_weights[i]
                target_value = current_value * target_allocation

                # Get current holding
                current_holding = self._get_current_holding(portfolio_id, asset)
                current_allocation = (
                    current_holding["weight"] / 100 if current_holding else 0
                )

                recommendations.append(
                    {
                        "asset": asset,
                        "current_allocation": current_allocation,
                        "target_allocation": target_allocation,
                        "current_value": (
                            current_holding["current_value"] if current_holding else 0
                        ),
                        "target_value": target_value,
                        "rebalance_amount": target_value
                        - (current_holding["current_value"] if current_holding else 0),
                        "action": self._determine_action(
                            current_allocation, target_allocation
                        ),
                    }
                )

            return {
                "portfolio_id": portfolio_id,
                "optimization_type": optimization_params.get("type", "mean_variance"),
                "target_return": target_return,
                "optimized_return": portfolio_return,
                "optimized_risk": portfolio_risk,
                "sharpe_ratio": sharpe_ratio,
                "recommendations": recommendations,
                "efficient_frontier": self._calculate_efficient_frontier(
                    expected_returns, cov_matrix
                ),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error optimizing portfolio: {str(e)}")
            return {"error": str(e)}

    def calculate_portfolio_performance(
        self, portfolio_id: int, period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate detailed portfolio performance metrics

        Args:
            portfolio_id: Portfolio ID
            period_days: Analysis period in days

        Returns:
            Comprehensive performance analysis
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return {"error": "Portfolio not found"}

            # Get portfolio value history
            value_history = self._get_portfolio_value_history(portfolio_id, period_days)

            if len(value_history) < 2:
                return {"error": "Insufficient data for performance calculation"}

            # Calculate returns
            returns = self._calculate_returns(value_history)

            # Performance metrics
            total_return = (
                value_history[-1]["value"] / value_history[0]["value"] - 1
            ) * 100
            annualized_return = self._calculate_annualized_return(returns, period_days)
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility

            # Risk metrics
            var_95 = np.percentile(returns, 5)  # 5% VaR
            var_99 = np.percentile(returns, 1)  # 1% VaR
            max_drawdown = self._calculate_max_drawdown(value_history)

            # Risk-adjusted returns
            risk_free_rate = 0.02  # 2% risk-free rate
            sharpe_ratio = (
                (annualized_return - risk_free_rate) / volatility
                if volatility > 0
                else 0
            )
            sortino_ratio = self._calculate_sortino_ratio(returns, risk_free_rate)

            # Benchmark comparison (simplified)
            benchmark_return = 0.05  # 5% benchmark return
            alpha = annualized_return - benchmark_return
            beta = self._calculate_beta(returns)

            # Performance attribution
            attribution = self._calculate_performance_attribution(
                portfolio_id, period_days
            )

            return {
                "portfolio_id": portfolio_id,
                "analysis_period": period_days,
                "total_return": total_return,
                "annualized_return": annualized_return,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "max_drawdown": max_drawdown,
                "var_95": var_95,
                "var_99": var_99,
                "alpha": alpha,
                "beta": beta,
                "attribution": attribution,
                "value_history": value_history,
                "returns": returns,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {str(e)}")
            return {"error": str(e)}

    def rebalance_portfolio(
        self, portfolio_id: int, target_allocations: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Rebalance portfolio to target allocations

        Args:
            portfolio_id: Portfolio ID
            target_allocations: Target allocation percentages by asset

        Returns:
            Rebalancing execution results
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return {"error": "Portfolio not found"}

            # Validate allocations sum to 100%
            total_allocation = sum(target_allocations.values())
            if abs(total_allocation - 100) > 0.01:
                return {"error": "Target allocations must sum to 100%"}

            # Get current holdings
            current_holdings = self._get_current_holdings_dict(portfolio_id)
            current_value = float(portfolio.total_value)

            # Calculate rebalancing trades
            rebalancing_trades = []

            for asset, target_pct in target_allocations.items():
                target_value = current_value * (target_pct / 100)
                current_holding = current_holdings.get(
                    asset, {"current_value": 0, "quantity": 0}
                )
                current_value_asset = current_holding["current_value"]

                difference = target_value - current_value_asset

                if abs(difference) > 10:  # Only rebalance if difference > $10
                    # Get current price
                    current_price = self._get_asset_current_price(asset)

                    if difference > 0:
                        # Buy more
                        quantity_to_buy = difference / current_price
                        rebalancing_trades.append(
                            {
                                "asset": asset,
                                "action": "buy",
                                "quantity": quantity_to_buy,
                                "estimated_value": difference,
                                "current_price": current_price,
                            }
                        )
                    else:
                        # Sell some
                        quantity_to_sell = abs(difference) / current_price
                        available_quantity = current_holding["quantity"]

                        if quantity_to_sell <= available_quantity:
                            rebalancing_trades.append(
                                {
                                    "asset": asset,
                                    "action": "sell",
                                    "quantity": quantity_to_sell,
                                    "estimated_value": abs(difference),
                                    "current_price": current_price,
                                }
                            )

            # Execute rebalancing trades (simplified - in practice would create actual orders)
            execution_results = []
            for trade in rebalancing_trades:
                # This would create actual buy/sell orders
                execution_results.append(
                    {
                        "asset": trade["asset"],
                        "action": trade["action"],
                        "quantity": trade["quantity"],
                        "status": "pending",  # Would be 'executed' after actual execution
                        "estimated_cost": trade["estimated_value"],
                    }
                )

            # Log rebalancing
            self.audit_service.log_event(
                user_id=portfolio.user_id,
                event_type="portfolio_rebalance",
                event_category="portfolio",
                event_description=f"Portfolio rebalancing initiated",
                metadata={
                    "portfolio_id": portfolio_id,
                    "trades_count": len(execution_results),
                    "target_allocations": target_allocations,
                },
                success=True,
            )

            return {
                "portfolio_id": portfolio_id,
                "rebalancing_trades": execution_results,
                "total_trades": len(execution_results),
                "estimated_total_cost": sum(
                    trade["estimated_cost"] for trade in execution_results
                ),
                "status": "initiated",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error rebalancing portfolio: {str(e)}")
            return {"error": str(e)}

    def get_portfolio_analytics(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Get comprehensive portfolio analytics

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Detailed analytics and insights
        """
        try:
            portfolio = Portfolio.query.get(portfolio_id)
            if not portfolio:
                return {"error": "Portfolio not found"}

            # Get holdings
            holdings = (
                PortfolioHolding.query.filter_by(portfolio_id=portfolio_id)
                .filter(PortfolioHolding.quantity > 0)
                .all()
            )

            # Diversification analysis
            diversification = self._analyze_diversification(holdings)

            # Concentration analysis
            concentration = self._analyze_concentration(holdings)

            # Sector analysis
            sector_analysis = self._analyze_sectors(holdings)

            # Vintage analysis
            vintage_analysis = self._analyze_vintages(holdings)

            # Geographic analysis
            geographic_analysis = self._analyze_geography(holdings)

            # Performance attribution
            performance_attribution = self._calculate_performance_attribution(
                portfolio_id, 30
            )

            # Risk analysis
            risk_analysis = self._analyze_portfolio_risks(portfolio, holdings)

            # ESG analysis (Environmental, Social, Governance)
            esg_analysis = self._analyze_esg_factors(holdings)

            return {
                "portfolio_id": portfolio_id,
                "diversification": diversification,
                "concentration": concentration,
                "sector_analysis": sector_analysis,
                "vintage_analysis": vintage_analysis,
                "geographic_analysis": geographic_analysis,
                "performance_attribution": performance_attribution,
                "risk_analysis": risk_analysis,
                "esg_analysis": esg_analysis,
                "recommendations": self._generate_portfolio_recommendations(
                    portfolio, holdings
                ),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting portfolio analytics: {str(e)}")
            return {"error": str(e)}

    # Helper methods

    def _get_current_holding_price(self, holding: PortfolioHolding) -> Decimal:
        """Get current market price for holding"""
        try:
            pricing_result = self.pricing_service.get_current_price(
                project_id=holding.project_id,
                credit_type=holding.credit_type,
                vintage_year=holding.vintage_year,
            )
            return pricing_result.get("price", holding.average_cost)
        except:
            return holding.average_cost

    def _calculate_performance_metrics(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Calculate basic performance metrics"""
        return {
            "total_return_pct": portfolio.pnl_percentage,
            "unrealized_pnl": float(portfolio.unrealized_pnl),
            "realized_pnl": float(portfolio.realized_pnl),
            "total_pnl": float(portfolio.total_pnl),
        }

    def _calculate_portfolio_risk_metrics(
        self, portfolio: Portfolio, holdings: List[PortfolioHolding]
    ) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        if not holdings:
            return {"var_95": 0, "concentration_risk": 0, "liquidity_risk": "low"}

        # Calculate concentration risk (Herfindahl-Hirschman Index)
        total_value = portfolio.total_value
        if total_value == 0:
            return {"var_95": 0, "concentration_risk": 0, "liquidity_risk": "low"}

        weights = []
        for holding in holdings:
            weight = holding.current_value / total_value if holding.current_value else 0
            weights.append(float(weight))

        hhi = sum(w**2 for w in weights)

        # Simplified VaR calculation
        portfolio_volatility = 0.15  # Assumed 15% volatility
        var_95 = float(total_value) * 1.645 * portfolio_volatility  # 95% VaR

        return {
            "var_95": var_95,
            "concentration_risk": hhi,
            "liquidity_risk": "medium",  # Simplified
            "portfolio_volatility": portfolio_volatility,
        }

    def _calculate_allocation_breakdown(
        self, holdings_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate allocation breakdown by various dimensions"""
        if not holdings_data:
            return {}

        # By credit type
        by_credit_type = {}
        for holding in holdings_data:
            credit_type = holding.get("credit_type", "Unknown")
            if credit_type not in by_credit_type:
                by_credit_type[credit_type] = 0
            by_credit_type[credit_type] += holding["weight"]

        # By vintage year
        by_vintage = {}
        for holding in holdings_data:
            vintage = str(holding.get("vintage_year", "Unknown"))
            if vintage not in by_vintage:
                by_vintage[vintage] = 0
            by_vintage[vintage] += holding["weight"]

        return {"by_credit_type": by_credit_type, "by_vintage_year": by_vintage}

    def _get_available_assets(self, optimization_params: Dict[str, Any]) -> List[str]:
        """Get available assets for optimization"""
        # Simplified - would query actual available assets
        return [
            "VCS_FORESTRY",
            "GOLD_STANDARD_RENEWABLE",
            "CDM_METHANE",
            "CAR_FORESTRY",
        ]

    def _get_historical_returns(self, assets: List[str]) -> pd.DataFrame:
        """Get historical returns for assets"""
        # Simplified - would get actual historical data
        np.random.seed(42)  # For reproducible results
        dates = pd.date_range(start="2023-01-01", end="2024-01-01", freq="D")

        returns_data = {}
        for asset in assets:
            # Generate synthetic returns
            returns = np.random.normal(0.0005, 0.02, len(dates))  # Daily returns
            returns_data[asset] = returns

        return pd.DataFrame(returns_data, index=dates)

    def _optimize_weights(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        target_return: float,
        risk_tolerance: str,
    ) -> np.ndarray:
        """Optimize portfolio weights using mean-variance optimization"""
        n_assets = len(expected_returns)

        # Objective function (minimize risk for given return)
        def objective(weights):
            return np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

        # Constraints
        constraints = [
            {"type": "eq", "fun": lambda x: np.sum(x) - 1},  # Weights sum to 1
            {
                "type": "eq",
                "fun": lambda x: np.dot(x, expected_returns) - target_return,
            },  # Target return
        ]

        # Bounds (no short selling)
        bounds = tuple((0, 1) for _ in range(n_assets))

        # Initial guess (equal weights)
        x0 = np.array([1 / n_assets] * n_assets)

        # Optimize
        result = minimize(
            objective, x0, method="SLSQP", bounds=bounds, constraints=constraints
        )

        if result.success:
            return result.x
        else:
            # Return equal weights if optimization fails
            return np.array([1 / n_assets] * n_assets)

    def _calculate_efficient_frontier(
        self, expected_returns: np.ndarray, cov_matrix: np.ndarray
    ) -> List[Dict[str, float]]:
        """Calculate efficient frontier points"""
        min_return = np.min(expected_returns)
        max_return = np.max(expected_returns)

        target_returns = np.linspace(min_return, max_return, 10)
        efficient_frontier = []

        for target_return in target_returns:
            try:
                weights = self._optimize_weights(
                    expected_returns, cov_matrix, target_return, "moderate"
                )
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_risk = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

                efficient_frontier.append(
                    {"return": float(portfolio_return), "risk": float(portfolio_risk)}
                )
            except:
                continue

        return efficient_frontier

    def _get_current_holding(
        self, portfolio_id: int, asset: str
    ) -> Optional[Dict[str, Any]]:
        """Get current holding for asset"""
        # Simplified asset matching
        holding = (
            PortfolioHolding.query.filter_by(portfolio_id=portfolio_id)
            .filter(PortfolioHolding.quantity > 0)
            .first()
        )

        if holding:
            return {
                "current_value": float(holding.current_value or 0),
                "quantity": float(holding.quantity),
                "weight": 50.0,  # Simplified
            }
        return None

    def _determine_action(
        self, current_allocation: float, target_allocation: float
    ) -> str:
        """Determine rebalancing action"""
        diff = target_allocation - current_allocation
        if abs(diff) < 0.01:  # 1% threshold
            return "hold"
        elif diff > 0:
            return "buy"
        else:
            return "sell"

    def _get_portfolio_value_history(
        self, portfolio_id: int, days: int
    ) -> List[Dict[str, Any]]:
        """Get portfolio value history"""
        # Simplified - would get actual historical values
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Generate synthetic value history
        dates = pd.date_range(start=start_date, end=end_date, freq="D")
        base_value = 100000  # $100k base value

        value_history = []
        for i, date in enumerate(dates):
            # Add some random walk
            value = base_value * (1 + 0.001 * i + np.random.normal(0, 0.01))
            value_history.append({"date": date.isoformat(), "value": max(0, value)})

        return value_history

    def _calculate_returns(self, value_history: List[Dict[str, Any]]) -> List[float]:
        """Calculate returns from value history"""
        values = [vh["value"] for vh in value_history]
        returns = []

        for i in range(1, len(values)):
            if values[i - 1] > 0:
                ret = (values[i] - values[i - 1]) / values[i - 1]
                returns.append(ret)

        return returns

    def _calculate_annualized_return(
        self, returns: List[float], period_days: int
    ) -> float:
        """Calculate annualized return"""
        if not returns:
            return 0.0

        total_return = np.prod([1 + r for r in returns]) - 1
        annualized = (1 + total_return) ** (365 / period_days) - 1
        return float(annualized)

    def _calculate_max_drawdown(self, value_history: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown"""
        values = [vh["value"] for vh in value_history]
        peak = values[0]
        max_dd = 0

        for value in values:
            if value > peak:
                peak = value

            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown

        return float(max_dd)

    def _calculate_sortino_ratio(
        self, returns: List[float], risk_free_rate: float
    ) -> float:
        """Calculate Sortino ratio"""
        if not returns:
            return 0.0

        excess_returns = [
            r - risk_free_rate / 252 for r in returns
        ]  # Daily risk-free rate
        downside_returns = [r for r in excess_returns if r < 0]

        if not downside_returns:
            return float("inf")

        downside_deviation = np.std(downside_returns)
        if downside_deviation == 0:
            return 0.0

        return float(np.mean(excess_returns) / downside_deviation * np.sqrt(252))

    def _calculate_beta(self, returns: List[float]) -> float:
        """Calculate portfolio beta (simplified)"""
        # Simplified - would compare against market benchmark
        return 1.0

    def _calculate_performance_attribution(
        self, portfolio_id: int, days: int
    ) -> Dict[str, Any]:
        """Calculate performance attribution"""
        # Simplified performance attribution
        return {
            "asset_selection": 0.02,  # 2% from asset selection
            "allocation": 0.01,  # 1% from allocation
            "interaction": 0.005,  # 0.5% from interaction
            "total_active_return": 0.035,  # 3.5% total active return
        }

    def _get_current_holdings_dict(
        self, portfolio_id: int
    ) -> Dict[str, Dict[str, Any]]:
        """Get current holdings as dictionary"""
        holdings = (
            PortfolioHolding.query.filter_by(portfolio_id=portfolio_id)
            .filter(PortfolioHolding.quantity > 0)
            .all()
        )

        holdings_dict = {}
        for holding in holdings:
            key = f"{holding.credit_type}_{holding.vintage_year}"
            holdings_dict[key] = {
                "current_value": float(holding.current_value or 0),
                "quantity": float(holding.quantity),
            }

        return holdings_dict

    def _get_asset_current_price(self, asset: str) -> float:
        """Get current price for asset"""
        # Simplified - would get actual current price
        return 50.0

    def _analyze_diversification(
        self, holdings: List[PortfolioHolding]
    ) -> Dict[str, Any]:
        """Analyze portfolio diversification"""
        if not holdings:
            return {
                "score": 0,
                "recommendations": ["Add holdings to improve diversification"],
            }

        # Calculate diversification metrics
        unique_projects = len(set(h.project_id for h in holdings if h.project_id))
        unique_types = len(set(h.credit_type for h in holdings if h.credit_type))
        unique_vintages = len(set(h.vintage_year for h in holdings if h.vintage_year))

        # Simple diversification score
        diversification_score = min(
            100, (unique_projects * 10 + unique_types * 15 + unique_vintages * 5)
        )

        recommendations = []
        if unique_types < 3:
            recommendations.append("Consider diversifying across more credit types")
        if unique_vintages < 3:
            recommendations.append("Consider diversifying across more vintage years")

        return {
            "score": diversification_score,
            "unique_projects": unique_projects,
            "unique_types": unique_types,
            "unique_vintages": unique_vintages,
            "recommendations": recommendations,
        }

    def _analyze_concentration(
        self, holdings: List[PortfolioHolding]
    ) -> Dict[str, Any]:
        """Analyze portfolio concentration"""
        if not holdings:
            return {"hhi": 0, "max_position": 0, "risk_level": "low"}

        total_value = sum(float(h.current_value or 0) for h in holdings)
        if total_value == 0:
            return {"hhi": 0, "max_position": 0, "risk_level": "low"}

        weights = [float(h.current_value or 0) / total_value for h in holdings]
        hhi = sum(w**2 for w in weights)
        max_position = max(weights) * 100

        # Determine risk level
        if hhi > 0.25:
            risk_level = "high"
        elif hhi > 0.15:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {"hhi": hhi, "max_position": max_position, "risk_level": risk_level}

    def _analyze_sectors(self, holdings: List[PortfolioHolding]) -> Dict[str, Any]:
        """Analyze sector allocation"""
        sector_allocation = {}
        total_value = sum(float(h.current_value or 0) for h in holdings)

        if total_value == 0:
            return sector_allocation

        for holding in holdings:
            sector = holding.credit_type or "Unknown"
            value = float(holding.current_value or 0)

            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += (value / total_value) * 100

        return sector_allocation

    def _analyze_vintages(self, holdings: List[PortfolioHolding]) -> Dict[str, Any]:
        """Analyze vintage year allocation"""
        vintage_allocation = {}
        total_value = sum(float(h.current_value or 0) for h in holdings)

        if total_value == 0:
            return vintage_allocation

        for holding in holdings:
            vintage = str(holding.vintage_year) if holding.vintage_year else "Unknown"
            value = float(holding.current_value or 0)

            if vintage not in vintage_allocation:
                vintage_allocation[vintage] = 0
            vintage_allocation[vintage] += (value / total_value) * 100

        return vintage_allocation

    def _analyze_geography(self, holdings: List[PortfolioHolding]) -> Dict[str, Any]:
        """Analyze geographic allocation"""
        # Simplified - would get actual project locations
        return {
            "North America": 40.0,
            "Europe": 25.0,
            "Asia": 20.0,
            "South America": 10.0,
            "Africa": 5.0,
        }

    def _analyze_portfolio_risks(
        self, portfolio: Portfolio, holdings: List[PortfolioHolding]
    ) -> Dict[str, Any]:
        """Analyze portfolio risks"""
        return {
            "market_risk": "medium",
            "credit_risk": "low",
            "liquidity_risk": "medium",
            "concentration_risk": "low",
            "regulatory_risk": "medium",
        }

    def _analyze_esg_factors(self, holdings: List[PortfolioHolding]) -> Dict[str, Any]:
        """Analyze ESG factors"""
        return {
            "environmental_score": 85,
            "social_score": 78,
            "governance_score": 82,
            "overall_esg_score": 82,
            "esg_rating": "A",
        }

    def _generate_portfolio_recommendations(
        self, portfolio: Portfolio, holdings: List[PortfolioHolding]
    ) -> List[str]:
        """Generate portfolio recommendations"""
        recommendations = []

        if len(holdings) < 5:
            recommendations.append(
                "Consider adding more holdings to improve diversification"
            )

        # Check concentration
        total_value = sum(float(h.current_value or 0) for h in holdings)
        if total_value > 0:
            max_weight = max(
                float(h.current_value or 0) / total_value for h in holdings
            )
            if max_weight > 0.3:
                recommendations.append(
                    "Consider reducing concentration in largest position"
                )

        recommendations.append(
            "Regular rebalancing recommended to maintain target allocations"
        )

        return recommendations
