import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as session:
        res = await session.execute(text("SELECT count(*) FROM students"))
        total = res.scalar()
        print(f"Total students currently in DB: {total}")
        
        # Primary students proposed: 21, 22, 23, 24, 1 (Grade 7-A, class_id=147) and 25, 26, 244, 291, 292 (Grade 8-A, class_id=32)
        # Secondary students proposed: 27, 28, 29, 343, 344 (Form 1-A, class_id=157) and 345, 346, 347, 348, 349 (Form 2-A, class_id=56)
        student_ids = [21, 22, 23, 24, 1, 25, 26, 244, 291, 292, 27, 28, 29, 343, 344, 345, 346, 347, 348, 349]
        
        query = text("""
            SELECT s.id, s.admission_number, s.first_name, s.last_name, s.user_id, s.status,
                   c.id as class_id, c.name as class_name, c.education_level, c.academic_year
            FROM students s
            LEFT JOIN student_enrollments se ON se.student_id = s.id AND se.status = 'ACTIVE'
            LEFT JOIN classes c ON c.id = se.class_id
            WHERE s.id = ANY(:ids)
            ORDER BY s.id
        """)
        res = await session.execute(query, {"ids": student_ids})
        rows = res.fetchall()
        print(f"\nFound {len(rows)} selected students:")
        for r in rows:
            print(dict(r._mapping))

if __name__ == "__main__":
    asyncio.run(main())
