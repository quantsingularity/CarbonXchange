"""
Trading models for CarbonXchange Backend
Implements comprehensive trading, order management, and portfolio tracking
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class OrderType(Enum):
    """Order type enumeration"""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order side enumeration"""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status enumeration"""

    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TradeStatus(Enum):
    """Trade status enumeration"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SETTLED = "settled"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PortfolioType(Enum):
    """Portfolio type enumeration"""

    TRADING = "trading"
    RETIREMENT = "retirement"
    CUSTODY = "custody"


class Order(db.Model):
    """Order model for buy/sell orders"""

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    uuid = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    order_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_type = Column(SQLEnum(OrderType), nullable=False)
    side = Column(SQLEnum(OrderSide), nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    credit_type = Column(String(100), nullable=True)
    vintage_year = Column(Integer, nullable=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"), nullable=True)
    quantity = Column(Numeric(15, 4), nullable=False)
    filled_quantity = Column(Numeric(15, 4), nullable=False, default=0)
    remaining_quantity = Column(Numeric(15, 4), nullable=False)
    price = Column(Numeric(10, 4), nullable=True)
    stop_price = Column(Numeric(10, 4), nullable=True)
    currency = Column(String(3), nullable=False, default="USD")
    time_in_force = Column(String(10), nullable=False, default="GTC")
    expires_at = Column(DateTime, nullable=True)
    average_fill_price = Column(Numeric(10, 4), nullable=True)
    total_value = Column(Numeric(15, 2), nullable=True)
    fees = Column(Numeric(10, 2), nullable=False, default=0)
    fee_currency = Column(String(3), nullable=False, default="USD")
    client_order_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    risk_limit_checked = Column(Boolean, nullable=False, default=False)
    compliance_checked = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    submitted_at = Column(DateTime, nullable=True)
    first_fill_at = Column(DateTime, nullable=True)
    last_fill_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="orders")
    project = relationship("CarbonProject")
    trades = relationship("Trade", back_populates="order", cascade="all, delete-orphan")

    def __init__(self, **kwargs) -> Any:
        super().__init__(**kwargs)
        self.remaining_quantity = self.quantity
        if not self.order_id:
            self.order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    @hybrid_property
    def is_active(self) -> Any:
        """Check if order is active (can be filled)"""
        return self.status in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]

    @hybrid_property
    def is_filled(self) -> Any:
        """Check if order is completely filled"""
        return self.status == OrderStatus.FILLED

    @hybrid_property
    def fill_percentage(self) -> Any:
        """Get fill percentage"""
        if self.quantity == 0:
            return 0
        return float(self.filled_quantity / self.quantity * 100)

    @hybrid_property
    def is_buy_order(self) -> Any:
        """Check if this is a buy order"""
        return self.side == OrderSide.BUY

    @hybrid_property
    def is_sell_order(self) -> Any:
        """Check if this is a sell order"""
        return self.side == OrderSide.SELL

    def can_fill(self, quantity: Any) -> Any:
        """Check if order can be filled with given quantity"""
        return self.is_active and quantity <= self.remaining_quantity

    def fill(self, quantity: Any, price: Any, trade_id: Any = None) -> Any:
        """Fill order with given quantity and price"""
        if not self.can_fill(quantity):
            raise ValueError("Cannot fill order with given quantity")
        self.filled_quantity += quantity
        self.remaining_quantity -= quantity
        if self.average_fill_price is None:
            self.average_fill_price = price
        else:
            total_value = (
                self.filled_quantity - quantity
            ) * self.average_fill_price + quantity * price
            self.average_fill_price = total_value / self.filled_quantity
        self.total_value = self.filled_quantity * self.average_fill_price
        if self.first_fill_at is None:
            self.first_fill_at = datetime.now(timezone.utc)
        self.last_fill_at = datetime.now(timezone.utc)
        if self.remaining_quantity == 0:
            self.status = OrderStatus.FILLED
            self.closed_at = datetime.now(timezone.utc)
        else:
            self.status = OrderStatus.PARTIALLY_FILLED

    def cancel(self, reason: Any = None) -> Any:
        """Cancel the order"""
        if not self.is_active:
            raise ValueError("Cannot cancel inactive order")
        self.status = OrderStatus.CANCELLED
        self.closed_at = datetime.now(timezone.utc)
        if reason:
            self.notes = f"{self.notes or ''}\nCancelled: {reason}".strip()

    def to_dict(self, include_sensitive: Any = False) -> Any:
        """Convert order to dictionary"""
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "order_id": self.order_id,
            "order_type": self.order_type.value,
            "side": self.side.value,
            "status": self.status.value,
            "credit_type": self.credit_type,
            "vintage_year": self.vintage_year,
            "quantity": float(self.quantity),
            "filled_quantity": float(self.filled_quantity),
            "remaining_quantity": float(self.remaining_quantity),
            "fill_percentage": self.fill_percentage,
            "price": float(self.price) if self.price else None,
            "average_fill_price": (
                float(self.average_fill_price) if self.average_fill_price else None
            ),
            "total_value": float(self.total_value) if self.total_value else None,
            "currency": self.currency,
            "fees": float(self.fees),
            "time_in_force": self.time_in_force,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "submitted_at": (
                self.submitted_at.isoformat() if self.submitted_at else None
            ),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }
        if include_sensitive:
            data.update(
                {
                    "user_id": self.user_id,
                    "client_order_id": self.client_order_id,
                    "notes": self.notes,
                    "risk_limit_checked": self.risk_limit_checked,
                    "compliance_checked": self.compliance_checked,
                }
            )
        return data

    def __repr__(self) -> Any:
        return f"<Order {self.order_id} - {self.side.value} {self.quantity} @ {self.price}>"


class Trade(db.Model):
    """Trade model representing executed transactions"""

    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    uuid = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    trade_id = Column(String(50), unique=True, nullable=False)
    buy_order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    sell_order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    quantity = Column(Numeric(15, 4), nullable=False)
    price = Column(Numeric(10, 4), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    credit_id = Column(Integer, ForeignKey("carbon_credits.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"), nullable=True)
    vintage_year = Column(Integer, nullable=True)
    status = Column(SQLEnum(TradeStatus), nullable=False, default=TradeStatus.PENDING)
    execution_venue = Column(String(100), nullable=True)
    buyer_fee = Column(Numeric(10, 2), nullable=False, default=0)
    seller_fee = Column(Numeric(10, 2), nullable=False, default=0)
    platform_fee = Column(Numeric(10, 2), nullable=False, default=0)
    settlement_date = Column(DateTime, nullable=True)
    settlement_reference = Column(String(100), nullable=True)
    blockchain_tx_hash = Column(String(66), nullable=True)
    block_number = Column(Integer, nullable=True)
    gas_used = Column(Integer, nullable=True)
    gas_price = Column(Numeric(20, 0), nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    executed_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    buy_order = relationship(
        "Order", foreign_keys=[buy_order_id], back_populates="trades"
    )
    sell_order = relationship(
        "Order", foreign_keys=[sell_order_id], back_populates="trades"
    )
    credit = relationship("CarbonCredit")
    project = relationship("CarbonProject")

    def __init__(self, **kwargs) -> Any:
        super().__init__(**kwargs)
        if not self.trade_id:
            self.trade_id = f"TRD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        self.total_value = self.quantity * self.price

    @hybrid_property
    def buyer_id(self) -> Any:
        """Get buyer user ID"""
        return self.buy_order.user_id if self.buy_order else None

    @hybrid_property
    def seller_id(self) -> Any:
        """Get seller user ID"""
        return self.sell_order.user_id if self.sell_order else None

    @hybrid_property
    def is_settled(self) -> Any:
        """Check if trade is settled"""
        return self.status == TradeStatus.SETTLED

    def settle(self, settlement_reference: Any = None) -> Any:
        """Mark trade as settled"""
        self.status = TradeStatus.SETTLED
        self.settlement_date = datetime.now(timezone.utc)
        self.settlement_reference = settlement_reference

    def to_dict(self, include_sensitive: Any = False) -> Any:
        """Convert trade to dictionary"""
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "trade_id": self.trade_id,
            "quantity": float(self.quantity),
            "price": float(self.price),
            "total_value": float(self.total_value),
            "currency": self.currency,
            "vintage_year": self.vintage_year,
            "status": self.status.value,
            "executed_at": self.executed_at.isoformat(),
            "settlement_date": (
                self.settlement_date.isoformat() if self.settlement_date else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_sensitive:
            data.update(
                {
                    "buy_order_id": self.buy_order_id,
                    "sell_order_id": self.sell_order_id,
                    "buyer_fee": float(self.buyer_fee),
                    "seller_fee": float(self.seller_fee),
                    "platform_fee": float(self.platform_fee),
                    "blockchain_tx_hash": self.blockchain_tx_hash,
                    "settlement_reference": self.settlement_reference,
                }
            )
        return data

    def __repr__(self) -> Any:
        return f"<Trade {self.trade_id} - {self.quantity} @ {self.price}>"


class Portfolio(db.Model):
    """Portfolio model for tracking user holdings"""

    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True)
    uuid = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    portfolio_type = Column(
        SQLEnum(PortfolioType), nullable=False, default=PortfolioType.TRADING
    )
    description = Column(Text, nullable=True)
    base_currency = Column(String(3), nullable=False, default="USD")
    total_value = Column(Numeric(15, 2), nullable=False, default=0)
    total_credits = Column(Numeric(15, 4), nullable=False, default=0)
    realized_pnl = Column(Numeric(15, 2), nullable=False, default=0)
    unrealized_pnl = Column(Numeric(15, 2), nullable=False, default=0)
    var_95 = Column(Numeric(15, 2), nullable=True)
    max_drawdown = Column(Numeric(10, 4), nullable=True)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_valuation_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="portfolios")
    holdings = relationship(
        "PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan"
    )

    @hybrid_property
    def total_pnl(self) -> Any:
        """Get total P&L (realized + unrealized)"""
        return self.realized_pnl + self.unrealized_pnl

    @hybrid_property
    def number_of_holdings(self) -> Any:
        """Get number of holdings in portfolio"""
        return len([h for h in self.holdings if h.quantity > 0])

    def update_valuation(self) -> Any:
        """Update portfolio valuation based on current holdings"""
        total_value = Decimal("0")
        total_credits = Decimal("0")
        for holding in self.holdings:
            if holding.quantity > 0:
                holding_value = holding.quantity * (
                    holding.current_price or holding.average_cost
                )
                total_value += holding_value
                total_credits += holding.quantity
        self.total_value = total_value
        self.total_credits = total_credits
        self.last_valuation_at = datetime.now(timezone.utc)

    def to_dict(self, include_sensitive: Any = False) -> Any:
        """Convert portfolio to dictionary"""
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "portfolio_type": self.portfolio_type.value,
            "description": self.description,
            "base_currency": self.base_currency,
            "total_value": float(self.total_value),
            "total_credits": float(self.total_credits),
            "total_pnl": float(self.total_pnl),
            "number_of_holdings": self.number_of_holdings,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_valuation_at": (
                self.last_valuation_at.isoformat() if self.last_valuation_at else None
            ),
        }
        if include_sensitive:
            data.update(
                {
                    "user_id": self.user_id,
                    "realized_pnl": float(self.realized_pnl),
                    "unrealized_pnl": float(self.unrealized_pnl),
                    "var_95": float(self.var_95) if self.var_95 else None,
                    "max_drawdown": (
                        float(self.max_drawdown) if self.max_drawdown else None
                    ),
                    "sharpe_ratio": (
                        float(self.sharpe_ratio) if self.sharpe_ratio else None
                    ),
                }
            )
        return data

    def __repr__(self) -> Any:
        return f"<Portfolio {self.name} - {self.user_id}>"


class PortfolioHolding(db.Model):
    """Portfolio holding model for individual credit positions"""

    __tablename__ = "portfolio_holdings"
    id = Column(Integer, primary_key=True)
    uuid = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    credit_id = Column(Integer, ForeignKey("carbon_credits.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"), nullable=False)
    quantity = Column(Numeric(15, 4), nullable=False, default=0)
    average_cost = Column(Numeric(10, 4), nullable=False)
    current_price = Column(Numeric(10, 4), nullable=True)
    currency = Column(String(3), nullable=False, default="USD")
    total_cost = Column(Numeric(15, 2), nullable=False)
    current_value = Column(Numeric(15, 2), nullable=True)
    unrealized_pnl = Column(Numeric(15, 2), nullable=False, default=0)
    realized_pnl = Column(Numeric(15, 2), nullable=False, default=0)
    vintage_year = Column(Integer, nullable=True)
    acquisition_method = Column(String(50), nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    first_acquired_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    last_traded_at = Column(DateTime, nullable=True)
    portfolio = relationship("Portfolio", back_populates="holdings")
    credit = relationship("CarbonCredit")
    project = relationship("CarbonProject")

    @hybrid_property
    def total_pnl(self) -> Any:
        """Get total P&L (realized + unrealized)"""
        return self.realized_pnl + self.unrealized_pnl

    @hybrid_property
    def pnl_percentage(self) -> Any:
        """Get P&L percentage"""
        if self.total_cost == 0:
            return 0
        return float(self.total_pnl / self.total_cost * 100)

    def update_price(self, new_price: Any) -> Any:
        """Update current price and recalculate unrealized P&L"""
        self.current_price = new_price
        if self.quantity > 0:
            self.current_value = self.quantity * new_price
            self.unrealized_pnl = self.current_value - self.total_cost
        else:
            self.current_value = Decimal("0")
            self.unrealized_pnl = Decimal("0")

    def add_position(self, quantity: Any, price: Any) -> Any:
        """Add to existing position (average cost calculation)"""
        if self.quantity == 0:
            self.quantity = quantity
            self.average_cost = price
            self.total_cost = quantity * price
        else:
            new_total_cost = self.total_cost + quantity * price
            new_quantity = self.quantity + quantity
            self.average_cost = new_total_cost / new_quantity
            self.quantity = new_quantity
            self.total_cost = new_total_cost
        self.last_traded_at = datetime.now(timezone.utc)
        if self.current_price:
            self.update_price(self.current_price)

    def reduce_position(self, quantity: Any, price: Any) -> Any:
        """Reduce position and realize P&L"""
        if quantity > self.quantity:
            raise ValueError("Cannot reduce position by more than current quantity")
        realized_pnl_per_unit = price - self.average_cost
        realized_pnl = quantity * realized_pnl_per_unit
        self.realized_pnl += realized_pnl
        self.quantity -= quantity
        if self.quantity > 0:
            self.total_cost = self.quantity * self.average_cost
        else:
            self.total_cost = Decimal("0")
            self.average_cost = Decimal("0")
        self.last_traded_at = datetime.now(timezone.utc)
        if self.current_price:
            self.update_price(self.current_price)

    def to_dict(self, include_sensitive: Any = False) -> Any:
        """Convert holding to dictionary"""
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "quantity": float(self.quantity),
            "average_cost": float(self.average_cost),
            "current_price": float(self.current_price) if self.current_price else None,
            "current_value": float(self.current_value) if self.current_value else None,
            "total_pnl": float(self.total_pnl),
            "pnl_percentage": self.pnl_percentage,
            "vintage_year": self.vintage_year,
            "currency": self.currency,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "first_acquired_at": self.first_acquired_at.isoformat(),
            "last_traded_at": (
                self.last_traded_at.isoformat() if self.last_traded_at else None
            ),
        }
        if include_sensitive:
            data.update(
                {
                    "portfolio_id": self.portfolio_id,
                    "credit_id": self.credit_id,
                    "project_id": self.project_id,
                    "total_cost": float(self.total_cost),
                    "realized_pnl": float(self.realized_pnl),
                    "unrealized_pnl": float(self.unrealized_pnl),
                    "acquisition_method": self.acquisition_method,
                }
            )
        return data

    def __repr__(self) -> Any:
        return f"<PortfolioHolding {self.quantity} @ {self.average_cost}>"
