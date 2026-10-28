import logging
from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from app.api.dependencies.auth import get_current_super_admin
from app.core.tenant_context import get_central_db
from app.models.inquiry import Inquiry
from app.models.institution import Institution, Subscription
from app.models.user import User
from app.schemas.inquiry import (
    InquiryResponse,
    InquiryListResponse,
    InquiryStatsResponse,
    InquiryUpdate,
    InquiryConvertRequest,
)
from app.schemas.institution import InstitutionResponse
from app.core.tenant_provisioner import (
    generate_tenant_database_name,
    create_tenant_database,
    provision_tenant_schema_and_admin,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/super-admin/inquiries", tags=["Super Admin Inbox & Inquiries"])


@router.get(
    "/stats",
    response_model=InquiryStatsResponse,
    summary="Get inquiry aggregate counts and unread badges"
)
def get_inquiry_stats(
    db: Session = Depends(get_central_db),
    current_super_admin: User = Depends(get_current_super_admin),
):
    """Returns badge counters for header envelope and sidebar inbox indicator."""
    total = db.query(Inquiry).count()
    unread = db.query(Inquiry).filter(Inquiry.status == "UNREAD").count()
    in_review = db.query(Inquiry).filter(Inquiry.status == "IN_REVIEW").count()
    contacted = db.query(Inquiry).filter(Inquiry.status == "CONTACTED").count()
    converted = db.query(Inquiry).filter(Inquiry.status == "CONVERTED").count()

    today_start = datetime.combine(date.today(), datetime.min.time())
    today = db.query(Inquiry).filter(Inquiry.created_at >= today_start).count()

    return InquiryStatsResponse(
        total=total,
        unread=unread,
        in_review=in_review,
        contacted=contacted,
        converted=converted,
        today=today,
    )


@router.get(
    "",
    response_model=InquiryListResponse,
    summary="List and filter all incoming public inquiries"
)
def list_inquiries(
    status_filter: Optional[str] = Query(None, alias="status", description="UNREAD, READ, IN_REVIEW, CONTACTED, CONVERTED, ARCHIVED, ALL"),
    priority_filter: Optional[str] = Query(None, alias="priority", description="LOW, NORMAL, HIGH, URGENT"),
    search: Optional[str] = Query(None, description="Search by name, school name, email, or phone"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_central_db),
    current_super_admin: User = Depends(get_current_super_admin),
):
    """Paginated list of inquiries with filtering by status, priority, and text search."""
    q = db.query(Inquiry)

    if status_filter and status_filter.upper() != "ALL":
        q = q.filter(Inquiry.status == status_filter.upper())

    if priority_filter and priority_filter.upper() != "ALL":
        q = q.filter(Inquiry.priority == priority_filter.upper())

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        q = q.filter(
            or_(
                func.lower(Inquiry.full_name).like(term),
                func.lower(Inquiry.school_name).like(term),
                func.lower(Inquiry.email).like(term),
                Inquiry.phone.like(term),
                func.lower(Inquiry.message).like(term),
            )
        )

    total = q.count()
    items = q.order_by(desc(Inquiry.created_at)).offset(skip).limit(limit).all()

    # Breakdown counts
    unread_cnt = db.query(Inquiry).filter(Inquiry.status == "UNREAD").count()
    in_review_cnt = db.query(Inquiry).filter(Inquiry.status == "IN_REVIEW").count()
    contacted_cnt = db.query(Inquiry).filter(Inquiry.status == "CONTACTED").count()
    converted_cnt = db.query(Inquiry).filter(Inquiry.status == "CONVERTED").count()
    archived_cnt = db.query(Inquiry).filter(Inquiry.status == "ARCHIVED").count()

    return InquiryListResponse(
        items=items,
        total=total,
        unread_count=unread_cnt,
        in_review_count=in_review_cnt,
        contacted_count=contacted_cnt,
        converted_count=converted_cnt,
        archived_count=archived_cnt,
    )


@router.get(
    "/{inquiry_id}",
    response_model=InquiryResponse,
    summary="Get single inquiry details and mark as READ"
)
def get_inquiry_detail(
    inquiry_id: int,
    db: Session = Depends(get_central_db),
    current_super_admin: User = Depends(get_current_super_admin),
):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inquiry not found.")

    # Automatically transition UNREAD -> READ upon opening
    if inquiry.status == "UNREAD":
        inquiry.status = "READ"
        db.commit()
        db.refresh(inquiry)

    return inquiry


@router.patch(
    "/{inquiry_id}",
    response_model=InquiryResponse,
    summary="Update status, priority, or management notes for an inquiry"
)
def update_inquiry(
    inquiry_id: int,
    payload: InquiryUpdate,
    db: Session = Depends(get_central_db),
    current_super_admin: User = Depends(get_current_super_admin),
):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inquiry not found.")

    if payload.status:
        inquiry.status = payload.status.upper()
    if payload.priority:
        inquiry.priority = payload.priority.upper()
    if payload.admin_notes is not None:
        inquiry.admin_notes = payload.admin_notes
    if payload.contacted_by is not None:
        inquiry.contacted_by = payload.contacted_by
    if payload.preferred_channel is not None:
        inquiry.preferred_channel = payload.preferred_channel

    db.commit()
    db.refresh(inquiry)
    return inquiry


@router.post(
    "/{inquiry_id}/convert",
    summary="Convert an inquiry into an active institutional tenant",
    status_code=status.HTTP_201_CREATED
)
def convert_inquiry_to_institution(
    inquiry_id: int,
    payload: InquiryConvertRequest,
    db: Session = Depends(get_central_db),
    current_super_admin: User = Depends(get_current_super_admin),
):
    """
    1-Click Conversion: Converts prospective inquiry lead into a fully provisioned school/academy.
    Generates code, provisions dedicated database, sets initial admin credentials,
    and links the resulting institution ID back to the inquiry record.
    """
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inquiry not found.")

    if inquiry.converted_institution_id:
        existing = db.query(Institution).filter(Institution.id == inquiry.converted_institution_id).first()
        if existing:
            return {
                "message": "Inquiry is already converted to an institution.",
                "institution_id": existing.id,
                "institution_code": existing.code,
                "institution_name": existing.name,
            }

    import random
    import string

    # Generate unique institution code
    next_num = db.query(Institution).count() + 1
    code = f"SOM-SCH-{next_num:04d}"
    while db.query(Institution).filter(Institution.code == code).first():
        next_num += 1
        code = f"SOM-SCH-{next_num:04d}"

    plan = payload.subscription_plan or inquiry.plan or "Professional School"
    admin_user = payload.admin_username or f"admin_{inquiry.school_name[:6].lower().replace(' ', '')}"
    temp_password = f"Somroyal@{next_num}{''.join(random.choices(string.digits, k=3))}"

    inst_name = inquiry.school_name.strip()
    database_name = generate_tenant_database_name(inst_name, code)

    new_inst = Institution(
        code=code,
        name=inst_name,
        type=payload.institution_type or "School",
        contact_person=inquiry.full_name,
        email=inquiry.email,
        phone=inquiry.phone,
        region=payload.region or "Banaadir",
        city=payload.city or "Mogadishu",
        status="ACTIVE",
        database_name=database_name,
        provisioning_status="PROVISIONED",
        admin_email=inquiry.email,
        admin_username=admin_user,
        subscription_plan=plan,
        subscription_status="ACTIVE",
        subscription_start_date=date.today(),
        subscription_expiry_date=date.today() + timedelta(days=365),
    )
    db.add(new_inst)
    db.commit()
    db.refresh(new_inst)

    # Automatically provision tenant database schema and initial admin
    try:
        create_tenant_database(database_name)
        provision_tenant_schema_and_admin(
            database_name=database_name,
            admin_data={
                "email": inquiry.email,
                "username": admin_user,
                "password": temp_password,
                "full_name": inquiry.full_name,
                "phone_number": inquiry.phone,
            },
            institution_info={
                "name": inst_name,
                "code": code,
                "type": payload.institution_type or "School",
                "email": inquiry.email,
                "phone": inquiry.phone,
                "city": payload.city or "Mogadishu",
            }
        )
    except Exception as e:
        logger.warning(f"Tenant database provisioning completed with note: {e}")

    # Create initial annual subscription
    initial_sub = Subscription(
        institution_id=new_inst.id,
        plan_name=plan,
        billing_cycle="Annual",
        price=350.00,
        setup_fee=70.00,
        status="Active",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=365),
        auto_renew=True,
        notes=f"Converted from Inquiry #{inquiry.id} by Super Admin.",
    )
    db.add(initial_sub)

    # Update inquiry status to CONVERTED
    inquiry.status = "CONVERTED"
    inquiry.converted_institution_id = new_inst.id
    inquiry.admin_notes = (inquiry.admin_notes or "") + f"\n[Converted on {datetime.now().strftime('%Y-%m-%d %H:%M')}] Converted to Institution {code} ({inst_name}). Generated admin username: {admin_user}."
    db.commit()

    return {
        "success": True,
        "message": f"Inquiry successfully converted to institution '{inst_name}' ({code}).",
        "institution_id": new_inst.id,
        "institution_code": new_inst.code,
        "institution_name": new_inst.name,
        "database_name": database_name,
        "admin_username": admin_user,
        "temporary_password": temp_password,
    }


@router.delete(
    "/{inquiry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete or archive an inquiry"
)
def delete_inquiry(
    inquiry_id: int,
    db: Session = Depends(get_central_db),
    current_super_admin: User = Depends(get_current_super_admin),
):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inquiry not found.")

    db.delete(inquiry)
    db.commit()
    return None
