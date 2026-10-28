from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies.database import get_db
from app.repositories.setting_repo import SettingRepository
from app.schemas.system import SystemSettingResponse

router = APIRouter(prefix="/system", tags=["System Settings"])


@router.get(
    "/settings/public",
    response_model=List[SystemSettingResponse],
    summary="Get public school branding & system settings"
)
def get_public_settings(
    db: Session = Depends(get_db)
):
    repo = SettingRepository(db)
    return repo.get_public_settings()
