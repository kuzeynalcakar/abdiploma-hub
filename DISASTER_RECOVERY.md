# Disaster Recovery — ABDiploma Hub

This guide covers **database backup, restore, and verification** for student data and question banks.

**Do not** expose the backup directory via your web server or CDN. Keep `BACKUP_DIR` outside the frontend `dist/` / public root.

---

## What is backed up

Automated SQLite backups are a consistent snapshot of the full application database, including:

- Users and sessions  
- Quiz attempts and answers  
- Feedback and question reports  
- Courses, topics, questions, and answer choices (question banks)  
- Topic performance / history tables  

Default location: `backend/backups/` (configurable).

---

## Configuration

Set in `backend/.env`:

```env
BACKUP_DIR=backups
BACKUP_RETENTION_DAYS=14
```

| Variable | Purpose |
|----------|---------|
| `BACKUP_DIR` | Directory for timestamped files (`albertaprep_backup_YYYYMMDD_HHMMSS.db`) |
| `BACKUP_RETENTION_DAYS` | Delete backups older than N days after each successful backup |

---

## Create a backup

From `backend/`:

```bash
python scripts/backup_db.py
```

Success prints the filename and size. Failures are logged (`albertaprep.backup`) **without** dumping `DATABASE_URL` credentials.

### Schedule (production)

Example daily cron (Linux):

```cron
15 2 * * * cd /path/to/AlbertaPrep/backend && /path/to/venv/bin/python scripts/backup_db.py >> /var/log/albertaprep-backup.log 2>&1
```

Windows Task Scheduler: run the same command daily; store logs outside the web root.

Copy backups off-box (S3, Azure Blob, encrypted disk) for real disaster resilience.

---

## Verify a backup

```bash
# Create a fresh backup and verify it
python scripts/verify_backup.py

# Or verify an existing file
python scripts/verify_backup.py backups/albertaprep_backup_YYYYMMDD_HHMMSS.db
```

Verification confirms:

1. File opens as SQLite (or Postgres dump heuristics)  
2. Required tables exist  
3. Row counts are readable  
4. Core content tables are not empty (`questions`, `courses`)  

Exit code `0` = OK; non-zero = failure.

---

## Restore procedure (SQLite)

### 1. Stop the API

Stop uvicorn / your process manager so nothing writes to the live DB mid-restore.

### 2. Identify the backup

```bash
ls backups/
```

Prefer the newest known-good file that passed `verify_backup.py`.

### 3. Restore

```bash
python scripts/restore_db.py backups/albertaprep_backup_YYYYMMDD_HHMMSS.db
```

This will:

1. Re-verify the backup  
2. Copy the **current** live DB aside as `albertaprep_pre_restore_*.db`  
3. Replace the live SQLite file  

### 4. Start the API

Restart uvicorn / container.

### 5. Verify restore

```bash
python scripts/verify_backup.py path/to/live/albertaprep.db
python scripts/audit_integrity.py
curl -s http://127.0.0.1:8000/api/v1/health
curl -s http://127.0.0.1:8000/api/v1/ready
```

Admin UI → **Database Health** should show last backup metadata and integrity status.

### 6. Smoke-check the product

- Log in as a test account  
- Load a quiz (guest + authenticated)  
- Confirm courses/questions still appear  

---

## Data integrity checks

```bash
python scripts/audit_integrity.py
```

Or as admin: `GET /api/v1/admin/integrity` (shown under Admin → Database Health).

Checks for:

- Orphaned answers, choices, reports, sessions, attempt links  
- Topics/questions/courses with broken relationships  
- Active courses with empty banks  
- MC questions missing choices  

These checks are **read-only**.

---

## Recovery after failure (checklist)

| Symptom | Action |
|---------|--------|
| Disk corruption / empty DB | Stop API → restore last known-good backup → verify → start |
| Bad deploy migrated schema incorrectly | Restore pre-deploy backup; redeploy fixed code |
| Accidental data deletion | Restore backup from before the event; investigate access controls |
| Backup job failing | Check logs for `backup_failed`; ensure `BACKUP_DIR` is writable; confirm DB path exists |
| Integrity issues after restore | Run `audit_integrity.py`; if orphans persist, restore an older backup |

---

## PostgreSQL note

If `DATABASE_URL` is Postgres, `create_backup` uses `pg_dump` when installed and writes a `.sql` file. Restore with `psql` (not `restore_db.py`). Prefer managed backups (RDS / Cloud SQL snapshots) in production.

---

## Security

- Never commit `backups/` or `*.db` to git (gitignored)  
- Never serve `BACKUP_DIR` from nginx/Caddy static roots  
- Do not email raw DB files without encryption  
- Logs must not print connection strings or passwords  

---

## Related scripts

| Script | Role |
|--------|------|
| `scripts/backup_db.py` | Create backup + retention |
| `scripts/verify_backup.py` | Create (optional) + verify |
| `scripts/restore_db.py` | Safe SQLite restore |
| `scripts/audit_integrity.py` | Orphan / relationship audit |

