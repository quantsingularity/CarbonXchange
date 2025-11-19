"""
Compliance Service for CarbonXchange Backend
Implements comprehensive compliance management with financial industry regulatory standards
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_

from ..models import db
from ..models.trading import Order, Trade, TradeStatus
from ..models.user import User, UserStatus
from .audit_service import AuditService

logger = logging.getLogger(__name__)


class ComplianceRule(Enum):
    """Compliance rule types"""

    KYC_VERIFICATION = "kyc_verification"
    AML_SCREENING = "aml_screening"
    SANCTIONS_CHECK = "sanctions_check"
    POSITION_LIMITS = "position_limits"
    TRADING_HOURS = "trading_hours"
    MARKET_MANIPULATION = "market_manipulation"
    INSIDER_TRADING = "insider_trading"
    BEST_EXECUTION = "best_execution"
    RECORD_KEEPING = "record_keeping"
    REPORTING_REQUIREMENTS = "reporting_requirements"


class ComplianceStatus(Enum):
    """Compliance status levels"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    REQUIRES_ACTION = "requires_action"


class ComplianceService:
    """
    Comprehensive compliance service implementing financial industry regulatory standards
    """

    def __init__(self):
        self.audit_service = AuditService()
        self.compliance_rules = self._load_compliance_rules()
        self.sanctions_list = self._load_sanctions_list()
        self.trading_hours = self._load_trading_hours()

    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules configuration"""
        return {
            "kyc_required_for_trading": True,
            "max_transaction_without_enhanced_kyc": Decimal("10000"),
            "suspicious_activity_threshold": Decimal("50000"),
            "large_transaction_reporting_threshold": Decimal("100000"),
            "position_reporting_threshold": Decimal("500000"),
            "max_daily_transactions": 100,
            "max_transaction_velocity": 10,  # transactions per hour
            "price_manipulation_threshold": 0.10,  # 10% price impact
            "wash_trading_detection_window": 300,  # 5 minutes
            "insider_trading_blackout_period": 7,  # 7 days
            "record_retention_period": 2555,  # 7 years in days
        }

    def _load_sanctions_list(self) -> List[str]:
        """Load sanctions and watchlist data"""
        # In production, this would load from official sanctions databases
        return [
            # Placeholder sanctions list
            "OFAC_SDN_LIST",
            "EU_SANCTIONS_LIST",
            "UN_SANCTIONS_LIST",
        ]

    def _load_trading_hours(self) -> Dict[str, Any]:
        """Load trading hours configuration"""
        return {
            "market_open": "09:00",
            "market_close": "17:00",
            "timezone": "UTC",
            "trading_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            "holidays": [],  # Market holidays
        }

    def check_order_compliance(
        self, user_id: int, order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive compliance check for new orders

        Args:
            user_id: User ID
            order_data: Order details

        Returns:
            Compliance check result with approval status and reasons
        """
        try:
            compliance_checks = []

            # Get user
            user = User.query.get(user_id)
            if not user:
                return {"approved": False, "reason": "User not found"}

            # 1. KYC/AML Compliance
            kyc_check = self._check_kyc_compliance(user, order_data)
            if kyc_check:
                compliance_checks.extend(kyc_check)

            # 2. Sanctions Screening
            sanctions_check = self._check_sanctions_compliance(user)
            if sanctions_check:
                compliance_checks.extend(sanctions_check)

            # 3. Trading Hours Compliance
            trading_hours_check = self._check_trading_hours_compliance()
            if trading_hours_check:
                compliance_checks.extend(trading_hours_check)

            # 4. Position Limits Compliance
            position_limits_check = self._check_position_limits_compliance(
                user_id, order_data
            )
            if position_limits_check:
                compliance_checks.extend(position_limits_check)

            # 5. Market Manipulation Detection
            manipulation_check = self._check_market_manipulation(user_id, order_data)
            if manipulation_check:
                compliance_checks.extend(manipulation_check)

            # 6. Wash Trading Detection
            wash_trading_check = self._check_wash_trading(user_id, order_data)
            if wash_trading_check:
                compliance_checks.extend(wash_trading_check)

            # 7. Transaction Velocity Limits
            velocity_check = self._check_transaction_velocity(user_id)
            if velocity_check:
                compliance_checks.extend(velocity_check)

            # 8. Suspicious Activity Detection
            suspicious_activity_check = self._check_suspicious_activity(
                user_id, order_data
            )
            if suspicious_activity_check:
                compliance_checks.extend(suspicious_activity_check)

            # Determine approval based on compliance violations
            blocking_violations = [
                c for c in compliance_checks if c.get("blocking", False)
            ]
            approved = len(blocking_violations) == 0

            # Log compliance assessment
            self.audit_service.log_event(
                user_id=user_id,
                event_type="compliance_check",
                event_category="compliance",
                event_description=f'Order compliance check: {"Approved" if approved else "Rejected"}',
                metadata={
                    "compliance_checks": len(compliance_checks),
                    "blocking_violations": len(blocking_violations),
                    "order_value": float(
                        Decimal(str(order_data.get("quantity", 0)))
                        * Decimal(str(order_data.get("price", 0) or 50))
                    ),
                },
                success=approved,
            )

            return {
                "approved": approved,
                "reason": (
                    blocking_violations[0]["message"] if blocking_violations else None
                ),
                "compliance_checks": compliance_checks,
                "requires_manual_review": any(
                    c.get("manual_review", False) for c in compliance_checks
                ),
            }

        except Exception as e:
            logger.error(f"Error in order compliance check: {str(e)}")
            return {"approved": False, "reason": "Compliance assessment failed"}

    def _check_kyc_compliance(
        self, user: User, order_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check KYC/AML compliance"""
        violations = []

        # Basic KYC requirement
        if (
            self.compliance_rules["kyc_required_for_trading"]
            and not user.is_kyc_approved
        ):
            violations.append(
                {
                    "rule": ComplianceRule.KYC_VERIFICATION,
                    "message": "KYC verification required for trading",
                    "blocking": True,
                }
            )

        # Enhanced KYC for large transactions
        order_value = Decimal(str(order_data.get("quantity", 0))) * Decimal(
            str(order_data.get("price", 0) or 50)
        )
        if order_value > self.compliance_rules["max_transaction_without_enhanced_kyc"]:
            # Check if user has enhanced KYC
            latest_kyc = self._get_latest_kyc_record(user.id)
            if not latest_kyc or latest_kyc.verification_level < 2:
                violations.append(
                    {
                        "rule": ComplianceRule.KYC_VERIFICATION,
                        "message": "Enhanced KYC verification required for large transactions",
                        "blocking": True,
                        "manual_review": True,
                    }
                )

        # AML screening status
        if (
            user.risk_level.value == "very_high"
            or user.risk_level.value == "prohibited"
        ):
            violations.append(
                {
                    "rule": ComplianceRule.AML_SCREENING,
                    "message": "Account flagged for AML review",
                    "blocking": True,
                    "manual_review": True,
                }
            )

        return violations

    def _check_sanctions_compliance(self, user: User) -> List[Dict[str, Any]]:
        """Check sanctions and watchlist compliance"""
        violations = []

        # Check if user is on sanctions list
        # In production, this would check against real sanctions databases
        if self._is_user_sanctioned(user):
            violations.append(
                {
                    "rule": ComplianceRule.SANCTIONS_CHECK,
                    "message": "User appears on sanctions watchlist",
                    "blocking": True,
                    "manual_review": True,
                }
            )

        return violations

    def _check_trading_hours_compliance(self) -> List[Dict[str, Any]]:
        """Check trading hours compliance"""
        violations = []

        current_time = datetime.utcnow()
        current_day = current_time.strftime("%A").lower()
        current_hour_minute = current_time.strftime("%H:%M")

        # Check if it's a trading day
        if current_day not in self.trading_hours["trading_days"]:
            violations.append(
                {
                    "rule": ComplianceRule.TRADING_HOURS,
                    "message": "Trading not allowed on weekends",
                    "blocking": False,  # Warning only
                }
            )

        # Check trading hours
        if (
            current_hour_minute < self.trading_hours["market_open"]
            or current_hour_minute > self.trading_hours["market_close"]
        ):
            violations.append(
                {
                    "rule": ComplianceRule.TRADING_HOURS,
                    "message": "Trading outside market hours",
                    "blocking": False,  # Warning only
                }
            )

        return violations

    def _check_position_limits_compliance(
        self, user_id: int, order_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check position limits compliance"""
        violations = []

        try:
            order_value = Decimal(str(order_data.get("quantity", 0))) * Decimal(
                str(order_data.get("price", 0) or 50)
            )

            # Check large position reporting threshold
            if order_value > self.compliance_rules["position_reporting_threshold"]:
                violations.append(
                    {
                        "rule": ComplianceRule.POSITION_LIMITS,
                        "message": "Large position requires regulatory reporting",
                        "blocking": False,
                        "manual_review": True,
                        "reporting_required": True,
                    }
                )

            # Check user-specific position limits based on risk profile
            user = User.query.get(user_id)
            if user and user.risk_level.value == "low":
                daily_volume = self._get_daily_trading_volume(user_id)
                if daily_volume + order_value > Decimal(
                    "50000"
                ):  # $50K daily limit for low-risk users
                    violations.append(
                        {
                            "rule": ComplianceRule.POSITION_LIMITS,
                            "message": "Daily trading limit exceeded for risk profile",
                            "blocking": True,
                        }
                    )

        except Exception as e:
            logger.error(f"Error checking position limits: {str(e)}")

        return violations

    def _check_market_manipulation(
        self, user_id: int, order_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for potential market manipulation"""
        violations = []

        try:
            # Check for unusual price impact
            current_market_price = self._get_current_market_price(
                order_data.get("credit_type")
            )
            order_price = Decimal(str(order_data.get("price", 0) or 0))

            if current_market_price and order_price > 0:
                price_impact = (
                    abs(order_price - current_market_price) / current_market_price
                )
                if price_impact > self.compliance_rules["price_manipulation_threshold"]:
                    violations.append(
                        {
                            "rule": ComplianceRule.MARKET_MANIPULATION,
                            "message": f"Order may cause significant price impact ({price_impact:.1%})",
                            "blocking": False,
                            "manual_review": True,
                        }
                    )

            # Check for layering/spoofing patterns
            recent_orders = self._get_recent_user_orders(user_id, minutes=30)
            if len(recent_orders) > 10:  # Many orders in short time
                cancel_rate = sum(
                    1 for o in recent_orders if o.status.value == "cancelled"
                ) / len(recent_orders)
                if cancel_rate > 0.8:  # High cancellation rate
                    violations.append(
                        {
                            "rule": ComplianceRule.MARKET_MANIPULATION,
                            "message": "Potential layering/spoofing pattern detected",
                            "blocking": False,
                            "manual_review": True,
                        }
                    )

        except Exception as e:
            logger.error(f"Error checking market manipulation: {str(e)}")

        return violations

    def _check_wash_trading(
        self, user_id: int, order_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for wash trading patterns"""
        violations = []

        try:
            # Look for recent opposite trades by the same user
            recent_window = datetime.utcnow() - timedelta(
                seconds=self.compliance_rules["wash_trading_detection_window"]
            )

            opposite_side = "sell" if order_data.get("side") == "buy" else "buy"

            recent_opposite_orders = (
                db.session.query(Order)
                .filter(
                    Order.user_id == user_id,
                    Order.side.has(value=opposite_side),
                    Order.created_at >= recent_window,
                    Order.credit_type == order_data.get("credit_type"),
                    Order.vintage_year == order_data.get("vintage_year"),
                )
                .all()
            )

            if recent_opposite_orders:
                violations.append(
                    {
                        "rule": ComplianceRule.MARKET_MANIPULATION,
                        "message": "Potential wash trading pattern detected",
                        "blocking": False,
                        "manual_review": True,
                    }
                )

        except Exception as e:
            logger.error(f"Error checking wash trading: {str(e)}")

        return violations

    def _check_transaction_velocity(self, user_id: int) -> List[Dict[str, Any]]:
        """Check transaction velocity limits"""
        violations = []

        try:
            # Check hourly transaction limit
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            hourly_orders = (
                db.session.query(func.count(Order.id))
                .filter(Order.user_id == user_id, Order.created_at >= one_hour_ago)
                .scalar()
            )

            if hourly_orders >= self.compliance_rules["max_transaction_velocity"]:
                violations.append(
                    {
                        "rule": ComplianceRule.POSITION_LIMITS,
                        "message": "Transaction velocity limit exceeded",
                        "blocking": True,
                    }
                )

            # Check daily transaction limit
            today = datetime.utcnow().date()
            daily_orders = (
                db.session.query(func.count(Order.id))
                .filter(Order.user_id == user_id, func.date(Order.created_at) == today)
                .scalar()
            )

            if daily_orders >= self.compliance_rules["max_daily_transactions"]:
                violations.append(
                    {
                        "rule": ComplianceRule.POSITION_LIMITS,
                        "message": "Daily transaction limit exceeded",
                        "blocking": True,
                    }
                )

        except Exception as e:
            logger.error(f"Error checking transaction velocity: {str(e)}")

        return violations

    def _check_suspicious_activity(
        self, user_id: int, order_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for suspicious activity patterns"""
        violations = []

        try:
            order_value = Decimal(str(order_data.get("quantity", 0))) * Decimal(
                str(order_data.get("price", 0) or 50)
            )

            # Large transaction reporting
            if (
                order_value
                > self.compliance_rules["large_transaction_reporting_threshold"]
            ):
                violations.append(
                    {
                        "rule": ComplianceRule.REPORTING_REQUIREMENTS,
                        "message": "Large transaction requires regulatory reporting",
                        "blocking": False,
                        "reporting_required": True,
                    }
                )

            # Suspicious activity threshold
            if order_value > self.compliance_rules["suspicious_activity_threshold"]:
                # Check user's typical trading patterns
                avg_order_value = self._get_user_average_order_value(user_id)
                if (
                    avg_order_value > 0 and order_value > avg_order_value * 10
                ):  # 10x typical size
                    violations.append(
                        {
                            "rule": ComplianceRule.AML_SCREENING,
                            "message": "Transaction significantly larger than typical pattern",
                            "blocking": False,
                            "manual_review": True,
                            "sar_filing_required": True,  # Suspicious Activity Report
                        }
                    )

        except Exception as e:
            logger.error(f"Error checking suspicious activity: {str(e)}")

        return violations

    def get_user_compliance_status(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive compliance status for user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {}

            # KYC Status
            kyc_record = self._get_latest_kyc_record(user_id)
            kyc_status = {
                "status": kyc_record.status.value if kyc_record else "not_started",
                "verification_level": (
                    kyc_record.verification_level if kyc_record else 0
                ),
                "last_updated": (
                    kyc_record.updated_at.isoformat() if kyc_record else None
                ),
                "expires_at": (
                    kyc_record.expires_at.isoformat()
                    if kyc_record and kyc_record.expires_at
                    else None
                ),
            }

            # AML Status
            aml_status = {
                "screening_status": "clear",  # Would be determined by AML screening
                "risk_score": float(user.risk_score) if user.risk_score else 0.0,
                "last_screened": (
                    user.risk_last_assessed.isoformat()
                    if user.risk_last_assessed
                    else None
                ),
            }

            # Trading Compliance
            trading_compliance = {
                "authorized_for_trading": user.is_kyc_approved
                and user.status == UserStatus.ACTIVE,
                "daily_volume_used": float(self._get_daily_trading_volume(user_id)),
                "daily_volume_limit": float(
                    self.compliance_rules["max_transaction_velocity"] * 1000
                ),  # Simplified
                "transaction_count_today": self._get_daily_transaction_count(user_id),
            }

            # Recent Compliance Issues
            recent_issues = self._get_recent_compliance_issues(user_id)

            # Overall Compliance Score
            compliance_score = self._calculate_compliance_score(user, kyc_record)

            return {
                "user_id": user_id,
                "overall_status": self._determine_overall_compliance_status(
                    compliance_score
                ),
                "compliance_score": compliance_score,
                "kyc": kyc_status,
                "aml": aml_status,
                "trading": trading_compliance,
                "recent_issues": recent_issues,
                "last_assessment": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting user compliance status: {str(e)}")
            return {}

    def _get_latest_kyc_record(self, user_id: int):
        """Get user's latest KYC record"""
        from ..models.user import UserKYC

        return (
            UserKYC.query.filter_by(user_id=user_id)
            .order_by(desc(UserKYC.created_at))
            .first()
        )

    def _is_user_sanctioned(self, user: User) -> bool:
        """Check if user is on sanctions list"""
        # In production, this would check against real sanctions databases
        # For now, return False as placeholder
        return False

    def _get_current_market_price(self, credit_type: str) -> Optional[Decimal]:
        """Get current market price for credit type"""
        recent_trade = (
            db.session.query(Trade)
            .filter(Trade.status == TradeStatus.SETTLED)
            .order_by(desc(Trade.executed_at))
            .first()
        )

        return recent_trade.price if recent_trade else None

    def _get_recent_user_orders(self, user_id: int, minutes: int = 30) -> List[Order]:
        """Get user's recent orders"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return (
            db.session.query(Order)
            .filter(Order.user_id == user_id, Order.created_at >= cutoff_time)
            .all()
        )

    def _get_daily_trading_volume(self, user_id: int) -> Decimal:
        """Get user's trading volume for today"""
        today = datetime.utcnow().date()

        volume = (
            db.session.query(func.sum(Trade.total_value))
            .join(
                Order,
                or_(
                    and_(Trade.buy_order_id == Order.id, Order.user_id == user_id),
                    and_(Trade.sell_order_id == Order.id, Order.user_id == user_id),
                ),
            )
            .filter(Trade.executed_at >= today, Trade.status == TradeStatus.SETTLED)
            .scalar()
        )

        return Decimal(str(volume)) if volume else Decimal("0")

    def _get_daily_transaction_count(self, user_id: int) -> int:
        """Get user's transaction count for today"""
        today = datetime.utcnow().date()

        count = (
            db.session.query(func.count(Order.id))
            .filter(Order.user_id == user_id, func.date(Order.created_at) == today)
            .scalar()
        )

        return count or 0

    def _get_user_average_order_value(self, user_id: int) -> Decimal:
        """Get user's average order value over last 30 days"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        avg_value = (
            db.session.query(func.avg(Trade.total_value))
            .join(
                Order,
                or_(
                    and_(Trade.buy_order_id == Order.id, Order.user_id == user_id),
                    and_(Trade.sell_order_id == Order.id, Order.user_id == user_id),
                ),
            )
            .filter(
                Trade.executed_at >= thirty_days_ago,
                Trade.status == TradeStatus.SETTLED,
            )
            .scalar()
        )

        return Decimal(str(avg_value)) if avg_value else Decimal("0")

    def _get_recent_compliance_issues(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recent compliance issues for user"""
        # This would query compliance violation records
        # For now, return empty list as placeholder
        return []

    def _calculate_compliance_score(self, user: User, kyc_record) -> float:
        """Calculate overall compliance score (0-100)"""
        score = 0.0

        # KYC Score (40 points)
        if user.is_kyc_approved:
            score += 30
            if kyc_record and kyc_record.verification_level >= 2:
                score += 10

        # Account Status (20 points)
        if user.status == UserStatus.ACTIVE:
            score += 20
        elif user.status == UserStatus.PENDING:
            score += 10

        # Risk Level (20 points)
        risk_scores = {
            "low": 20,
            "medium": 15,
            "high": 10,
            "very_high": 5,
            "prohibited": 0,
        }
        score += risk_scores.get(user.risk_level.value, 0)

        # Account Age and Activity (20 points)
        if user.created_at:
            days_active = (datetime.utcnow() - user.created_at).days
            if days_active > 365:
                score += 20
            elif days_active > 90:
                score += 15
            elif days_active > 30:
                score += 10
            else:
                score += 5

        return min(100.0, score)

    def _determine_overall_compliance_status(self, compliance_score: float) -> str:
        """Determine overall compliance status from score"""
        if compliance_score >= 90:
            return ComplianceStatus.COMPLIANT.value
        elif compliance_score >= 70:
            return ComplianceStatus.REQUIRES_ACTION.value
        elif compliance_score >= 50:
            return ComplianceStatus.UNDER_REVIEW.value
        else:
            return ComplianceStatus.NON_COMPLIANT.value
