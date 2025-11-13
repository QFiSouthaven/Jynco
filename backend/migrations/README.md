# Database Migrations

This directory contains SQL migration scripts for the database schema.

## Running Migrations

### Using psql (PostgreSQL command line)

```bash
psql -h localhost -U your_user -d your_database -f 001_add_error_code_to_segments.sql
```

### Using Docker

If your database is running in a Docker container:

```bash
docker exec -i postgres_container psql -U postgres -d jynco < backend/migrations/001_add_error_code_to_segments.sql
```

### Using Python

You can also run migrations programmatically:

```python
from backend.config import get_db_context

with get_db_context() as db:
    with open('backend/migrations/001_add_error_code_to_segments.sql', 'r') as f:
        migration_sql = f.read()
    db.execute(migration_sql)
    db.commit()
```

## Migration Files

- `001_add_error_code_to_segments.sql` - Adds error_code column to segments table for better error handling

## Notes

- Migrations should be run in order (001, 002, 003, etc.)
- Always backup your database before running migrations
- The migrations use `IF NOT EXISTS` to be idempotent (safe to run multiple times)
