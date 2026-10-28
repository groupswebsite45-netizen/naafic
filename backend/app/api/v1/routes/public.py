import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.tenant_context import get_central_db
from app.models.inquiry import Inquiry
from app.schemas.inquiry import InquiryCreate, InquiryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public", tags=["Public Portal & Inquiries"])


@router.post(
    "/inquiries",
    response_model=InquiryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new inquiry from the public website"
)
def submit_public_inquiry(
    payload: InquiryCreate,
    db: Session = Depends(get_central_db)
):
    """
    Public endpoint for prospective schools, academies, and institutions
    to submit demo inquiries and licensing consultations.
    Automatically ingested into the Super Admin Inbox with UNREAD status.
    """
    try:
        inquiry = Inquiry(
            full_name=payload.full_name.strip(),
            school_name=payload.school_name.strip(),
            email=payload.email.strip().lower(),
            phone=payload.phone.strip(),
            plan=payload.plan.strip() if payload.plan else None,
            message=payload.message.strip(),
            preferred_channel=payload.preferred_channel or "WhatsApp",
            status="UNREAD",
            priority="NORMAL",
            source="PUBLIC_LANDING_PAGE",
        )
        db.add(inquiry)
        db.commit()
        db.refresh(inquiry)
        logger.info(f"New public inquiry #{inquiry.id} received from {inquiry.full_name} ({inquiry.school_name})")
        return inquiry
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to submit public inquiry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit inquiry. Please try again shortly."
        )
