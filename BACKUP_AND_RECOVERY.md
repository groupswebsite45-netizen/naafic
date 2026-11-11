# Permanent Student Profile Photo — Backup and Recovery Architecture

## Storage Architecture Overview

Student profile photos are permanently stored on the host file system in an isolated and protected directory:
- **Root Directory**: `backend/uploads/`
- **Student Photos Directory**: `backend/uploads/student_photos/`
- **Database Reference**: PostgreSQL `students` table:
  - `photo_path` (VARCHAR 500): Relative storage path (e.g., `student_photos/student_102_3b9f4a12c8e1.jpg`)
  - `photo_filename` (VARCHAR 255): Original uploaded file name
  - `photo_mime_type` (VARCHAR 100): Validated MIME type (`image/jpeg`, `image/png`, `image/webp`)
  - `photo_size` (INTEGER): File size in bytes
  - `photo_uploaded_at` (TIMESTAMP WITH TIME ZONE)
  - `photo_updated_at` (TIMESTAMP WITH TIME ZONE)

---

## Unified Backup Strategy

To ensure zero divergence between the PostgreSQL database records and the persistent image files on disk, both data stores must be captured concurrently.

### 1. Automated Consolidated Backup Script

A consolidated backup utility is provided in `backend/scripts/backup_and_recovery.py`:

```bash
cd backend
python scripts/backup_and_recovery.py
```

This creates a timestamped, gzip-compressed archive in `backend/backups/somroyal_ems_backup_<YYYYMMDD_HHMMSS>.tar.gz` containing:
1. Complete PostgreSQL database snapshot (`database_snapshot.json`)
2. All persistent uploads including `student_photos/` and `exam_papers/`

### 2. Manual System Level Backups (Production Linux / VPS)

If database backups and file backups are taken using native OS tools (e.g., `pg_dump` and `rsync`):

#### Database Backup:
```bash
pg_dump -U postgres -h localhost -d hawlwadaag_school_db -F c -b -v -f /var/backups/sms_db_$(date +%Y%m%d_%H%M%S).dump
```

#### Filesystem Storage Backup:
```bash
rsync -avz --delete /path/to/SMS/backend/uploads/ /var/backups/sms_uploads_$(date +%Y%m%d_%H%M%S)/
```

---

## Recovery Procedure

### 1. Restoring the Database
```bash
pg_restore -U postgres -h localhost -d hawlwadaag_school_db -v /var/backups/sms_db_<timestamp>.dump
```

### 2. Restoring the Upload Files
```bash
rsync -avz /var/backups/sms_uploads_<timestamp>/ /path/to/SMS/backend/uploads/
```

### 3. Verifying File-to-Database Integrity
Run the built-in integrity verification utility:
```bash
cd backend
python scripts/backup_and_recovery.py verify
```

This checks all student records where `photo_path IS NOT NULL` against the physical files on disk and reports any missing files or broken references.
