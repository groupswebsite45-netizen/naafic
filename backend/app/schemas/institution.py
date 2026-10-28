from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class AdminAccountCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None


class InstitutionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    type: str = Field(default="School", description="School, Academy, College, Institute, Primary School, Secondary School, Other")
    logo_url: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    subscription_plan: str = Field(default="Professional School")
    subscription_start_date: Optional[date] = None
    subscription_expiry_date: Optional[date] = None
    status: str = Field(default="ACTIVE")
    admin_account: Optional[AdminAccountCreate] = None


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    logo_url: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    subscription_plan: Optional[str] = None
    subscription_status: Optional[str] = None
    subscription_start_date: Optional[date] = None
    subscription_expiry_date: Optional[date] = None
    admin_username: Optional[str] = None
    admin_email: Optional[EmailStr] = None
    admin_password: Optional[str] = None


class InstitutionResponse(BaseModel):
    id: int
    code: str
    name: str
    type: str
    logo_url: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    status: str
    database_name: Optional[str] = None
    provisioning_status: Optional[str] = "PROVISIONED"
    provisioning_error: Optional[str] = None
    admin_email: Optional[str] = None
    admin_username: Optional[str] = None
    subscription_plan: str
    subscription_status: str
    subscription_start_date: Optional[date] = None
    subscription_expiry_date: Optional[date] = None
    admin_user_id: Optional[int] = None
    total_students: Optional[int] = 0
    total_teachers: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionCreate(BaseModel):
    institution_id: int
    plan_name: str
    billing_cycle: str = "Monthly"
    price: float = 25.0
    setup_fee: float = 0.0
    status: str = "Active"
    start_date: datetime
    end_date: datetime
    auto_renew: bool = True
    notes: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: int
    institution_id: int
    institution_name: Optional[str] = None
    institution_code: Optional[str] = None
    plan_name: str
    billing_cycle: str
    price: float
    setup_fee: float
    status: str
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InstitutionPaymentCreate(BaseModel):
    institution_id: int
    subscription_id: Optional[int] = None
    reference: Optional[str] = None
    amount: float
    currency: str = "USD"
    payment_method: str = "EVC Plus"
    status: str = "Completed"
    invoice_number: Optional[str] = None
    notes: Optional[str] = None


class InstitutionPaymentResponse(BaseModel):
    id: int
    institution_id: int
    institution_name: Optional[str] = None
    subscription_id: Optional[int] = None
    reference: str
    amount: float
    currency: str
    payment_method: str
    payment_date: datetime
    status: str
    invoice_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatCard(BaseModel):
    title: str
    value: int
    subtitle: Optional[str] = None


class TypeBreakdown(BaseModel):
    name: str
    count: int
    percentage: float


class RecentActivityItem(BaseModel):
    id: int
    type: str  # registration, subscription, payment, user
    title: str
    subtitle: str
    timestamp: str
    status: Optional[str] = None


class MonthlyRevenueItem(BaseModel):
    month: str
    amount: float


class StatusBreakdownItem(BaseModel):
    status: str
    count: int
    percentage: float


class SuperAdminDashboardStats(BaseModel):
    total_institutions: int
    total_schools: int
    total_academies: int
    total_students: int = 0
    total_teachers: int = 0
    active_subscriptions: int
    expired_subscriptions: int
    pending_subscriptions: int = 0
    total_revenue: float = 0.0
    total_payments_amount: float
    platform_usage: float = 94.0
    type_breakdown: List[TypeBreakdown]
    subscription_breakdown: List[StatusBreakdownItem] = []
    monthly_revenue: List[MonthlyRevenueItem] = []
    recent_institutions: List[InstitutionResponse] = []
    recent_payments: List[InstitutionPaymentResponse] = []
    recent_activities: List[RecentActivityItem] = []

