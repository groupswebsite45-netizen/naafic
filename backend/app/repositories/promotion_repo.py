from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.class_promotion import ClassPromotionBatch, ClassPromotionRecord
from app.repositories.base_repo import BaseRepository


class PromotionRepository(BaseRepository[ClassPromotionBatch]):
    """Repository for Class Promotion Batches and Audit Records."""

    def __init__(self, db: Session):
        super().__init__(ClassPromotionBatch, db)

    def generate_batch_code(self, target_academic_year: str) -> str:
        """
        Generate human-readable unique batch code.
        Format: PROM-YYYY-XXXX (e.g. PROM-2027-0001)
        """
        # Extract 4-digit year from academic year string
        clean_year = "".join(filter(str.isdigit, target_academic_year))
        year_prefix = clean_year[:4] if len(clean_year) >= 4 else str(datetime.now().year)

        existing_codes = {
            b[0]
            for b in self.db.query(ClassPromotionBatch.batch_code)
            .filter(ClassPromotionBatch.batch_code.like(f"PROM-{year_prefix}-%"))
            .all()
        }
        seq = len(existing_codes) + 1
        while f"PROM-{year_prefix}-{seq:04d}" in existing_codes:
            seq += 1
        return f"PROM-{year_prefix}-{seq:04d}"

    def get_batch_by_code(self, batch_code: str) -> Optional[ClassPromotionBatch]:
        return (
            self.db.query(ClassPromotionBatch)
            .filter(ClassPromotionBatch.batch_code == batch_code.strip())
            .first()
        )

    def get_batch_by_id(self, batch_id: int) -> Optional[ClassPromotionBatch]:
        return (
            self.db.query(ClassPromotionBatch)
            .filter(ClassPromotionBatch.id == batch_id)
            .first()
        )

    def list_batches(
        self,
        academic_year: Optional[str] = None,
        promotion_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ClassPromotionBatch], int]:
        q = self.db.query(ClassPromotionBatch)

        if academic_year:
            q = q.filter(
                (ClassPromotionBatch.source_academic_year == academic_year.strip()) |
                (ClassPromotionBatch.target_academic_year == academic_year.strip())
            )
        if promotion_type:
            q = q.filter(ClassPromotionBatch.promotion_type == promotion_type.upper().strip())
        if status:
            q = q.filter(ClassPromotionBatch.status == status.upper().strip())

        total = q.count()
        batches = q.order_by(desc(ClassPromotionBatch.id)).offset(skip).limit(limit).all()
        return batches, total

    def list_records(
        self,
        batch_id: Optional[int] = None,
        student_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ClassPromotionRecord], int]:
        q = self.db.query(ClassPromotionRecord)

        if batch_id:
            q = q.filter(ClassPromotionRecord.batch_id == batch_id)
        if student_id:
            q = q.filter(ClassPromotionRecord.student_id == student_id)
        if academic_year:
            q = q.filter(
                (ClassPromotionRecord.source_academic_year == academic_year.strip()) |
                (ClassPromotionRecord.target_academic_year == academic_year.strip())
            )

        total = q.count()
        records = q.order_by(desc(ClassPromotionRecord.id)).offset(skip).limit(limit).all()
        return records, total
