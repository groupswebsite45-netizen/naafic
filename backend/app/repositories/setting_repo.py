from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.system_setting import SystemSetting
from app.repositories.base_repo import BaseRepository


class SettingRepository(BaseRepository[SystemSetting]):
    """System setting repository."""

    def __init__(self, db: Session):
        super().__init__(SystemSetting, db)

    def get_by_key(self, key: str) -> Optional[SystemSetting]:
        return self.db.query(SystemSetting).filter(SystemSetting.key == key).first()

    def get_public_settings(self) -> List[SystemSetting]:
        return self.db.query(SystemSetting).filter(SystemSetting.is_public == True).all()  # noqa: E712

    def set_value(self, key: str, value: str, description: Optional[str] = None, is_public: bool = False) -> SystemSetting:
        setting = self.get_by_key(key)
        if setting:
            setting.value = value
            if description is not None:
                setting.description = description
            setting.is_public = is_public
            self.db.commit()
            self.db.refresh(setting)
        else:
            setting = SystemSetting(
                key=key,
                value=value,
                description=description,
                is_public=is_public
            )
            self.create(setting)
        return setting
