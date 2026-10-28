from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Institution(Base):
    """Educational Institution model representing schools, academies, colleges, and networks."""
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False, default="School", index=True)
    logo_url = Column(String(500), nullable=True)
    contact_person = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE", index=True)  # ACTIVE, SUSPENDED, PENDING
    database_name = Column(String(100), nullable=True, index=True)
    provisioning_status = Column(String(50), nullable=False, default="PROVISIONED", index=True)  # PROVISIONED, PENDING, FAILED
    provisioning_error = Column(Text, nullable=True)
    admin_email = Column(String(255), nullable=True)
    admin_username = Column(String(100), nullable=True)
    subscription_plan = Column(String(100), nullable=False, default="Professional School")
    subscription_status = Column(String(50), nullable=False, default="ACTIVE", index=True)  # ACTIVE, EXPIRED, SUSPENDED, TRIAL
    subscription_start_date = Column(Date, nullable=True)
    subscription_expiry_date = Column(Date, nullable=True)
    admin_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="institution", cascade="all, delete-orphan")
    payments = relationship("InstitutionPayment", back_populates="institution", cascade="all, delete-orphan")
    admin_user = relationship("User", foreign_keys=[admin_user_id])

    @property
    def institution_type(self) -> str:
        return self.type

    def __repr__(self) -> str:
        return f"<Institution(id={self.id}, code='{self.code}', name='{self.name}')>"


class Subscription(Base):
    """Subscription record for an educational institution."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_name = Column(String(100), nullable=False)
    billing_cycle = Column(String(50), nullable=False, default="Monthly")  # Monthly, Annual
    price = Column(Numeric(10, 2), nullable=False, default=25.00)
    setup_fee = Column(Numeric(10, 2), nullable=False, default=70.00)
    status = Column(String(50), nullable=False, default="Active", index=True)  # Active, Expired, Suspended
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, institution_id={self.institution_id}, plan='{self.plan_name}')>"


class InstitutionPayment(Base):
    """Financial transaction record for an institution subscription/setup payment."""
    __tablename__ = "institution_payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    reference = Column(String(100), unique=True, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    payment_method = Column(String(50), nullable=False, default="EVC Plus")  # EVC Plus, Zaad, Sahal, Bank Transfer, Card
    payment_date = Column(DateTime, nullable=False, default=func.now())
    status = Column(String(50), nullable=False, default="Completed", index=True)  # Completed, Pending, Failed
    invoice_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    institution = relationship("Institution", back_populates="payments")

    def __repr__(self) -> str:
        return f"<InstitutionPayment(id={self.id}, ref='{self.reference}', amount={self.amount})>"
