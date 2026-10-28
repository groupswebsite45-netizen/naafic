from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class InquiryCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150, description="Inquirer's full name")
    school_name: str = Field(..., min_length=2, max_length=200, description="School or institution name")
    email: EmailStr = Field(..., description="Official contact email")
    phone: str = Field(..., min_length=5, max_length=50, description="Phone or WhatsApp number")
    plan: Optional[str] = Field(None, max_length=120, description="Selected plan or tier")
    message: str = Field(..., min_length=5, description="Inquiry details and requirements")
    preferred_channel: Optional[str] = Field("WhatsApp", max_length=50, description="Preferred contact channel")


class InquiryUpdate(BaseModel):
    status: Optional[str] = Field(None, description="UNREAD, READ, IN_REVIEW, CONTACTED, CONVERTED, ARCHIVED")
    priority: Optional[str] = Field(None, description="LOW, NORMAL, HIGH, URGENT")
    admin_notes: Optional[str] = Field(None, description="Internal follow-up and CRM notes")
    contacted_by: Optional[str] = Field(None, description="Staff member who contacted the lead")
    preferred_channel: Optional[str] = Field(None, description="WhatsApp, Email, Phone, Meeting")


class InquiryConvertRequest(BaseModel):
    institution_type: Optional[str] = Field("School", description="School, Academy, University, Institute")
    region: Optional[str] = Field("Banaadir", description="Administrative region")
    city: Optional[str] = Field("Mogadishu", description="City")
    subscription_plan: Optional[str] = Field(None, description="Plan to assign upon conversion")
    admin_username: Optional[str] = Field(None, description="Custom admin username for institution")


class InquiryResponse(BaseModel):
    id: int
    full_name: str
    school_name: str
    email: str
    phone: str
    plan: Optional[str] = None
    message: str
    status: str
    priority: str
    admin_notes: Optional[str] = None
    contacted_by: Optional[str] = None
    preferred_channel: Optional[str] = None
    source: str
    converted_institution_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InquiryListResponse(BaseModel):
    items: List[InquiryResponse]
    total: int
    unread_count: int
    in_review_count: int
    contacted_count: int
    converted_count: int
    archived_count: int


class InquiryStatsResponse(BaseModel):
    total: int
    unread: int
    in_review: int
    contacted: int
    converted: int
    today: int
