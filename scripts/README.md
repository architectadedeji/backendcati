# Backend Utility Scripts

This directory contains utility scripts for database management, debugging, and testing.

## Directory Structure

### `db/` - Database Management Scripts
Scripts for database initialization, migrations, seeding, and data import/export.

- `init_db.py`, `init_db_2.py` - Initialize database schema
- `seed_db_2.py`, `seed_db_2_clean.py`, `seed_admin.py` - Populate database with sample data
- `migrate_contacts.py` - Migrate contact data between schemas
- `import_contacts*.py` - Import contacts from CSV or other sources
- `export*.py` - Export data to CSV format
- `fix_contact_data.py` - Data cleanup and normalization
- `remove_email_column.py` - Schema alteration

### `debug/` - Debugging & Inspection Scripts
Scripts for inspecting database state, validating data, and troubleshooting issues.

- `check_*.py` - Verify database status, backups, and data integrity
- `list_*.py` - List database tables and contents
- `verify_*.py` - Validate field types, migrations, and contact data
- `delete_*.py` - Remove specific records (admin, test data)
- `debug_*.py` - Analyze timings and state

### `testing/` - Test Scripts
Ad-hoc test scripts for API endpoints and functionality validation.

- `test_*.py` - Various API endpoint and integration tests

## Usage

Run scripts from the backend directory:

```bash
cd backend
python scripts/db/init_db.py
python scripts/testing/test_api.py
python scripts/debug/check_backup.py
```

## Note

Consider migrating these to a proper pytest test suite for long-term maintainability.
