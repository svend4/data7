# Database Setup Guide

PostgreSQL database setup and migration guide for Meta-Orchestrator Switchboard.

## Prerequisites

- PostgreSQL 14+ installed
- Python 3.11+ with pip

## Quick Start

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Docker:**
```bash
docker run --name switchboard-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=switchboard \
  -p 5432:5432 \
  -d postgres:14
```

### 2. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE switchboard;

# Create user (if needed)
CREATE USER switchboard_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE switchboard TO switchboard_user;

# Exit
\q
```

### 3. Configure Environment

Create `.env` file in `backend/` directory:

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=switchboard

# Or use DATABASE_URL directly
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/switchboard

# Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=false  # Set to true for SQL query logging
```

### 4. Run Migrations

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head
```

## Database Schema

### Tables Created

**agents** - AI agent entities
- id (PK)
- role, status
- avg_response_time, success_rate, total_tasks, current_load
- position_x, position_y, position_z (3D coordinates)
- metadata (JSON)
- created_at, updated_at

**agent_capabilities** - Agent capabilities/skills
- id (PK, autoincrement)
- agent_id (FK → agents)
- name, category, level (1-5)
- description

**tasks** - Work units
- id (PK)
- description, task_type, status, priority (1-10)
- assigned_agent_id (FK → agents)
- result (JSON), error
- metadata (JSON)
- created_at, started_at, completed_at

**connections** - Agent-to-agent links
- id (PK)
- from_agent_id, to_agent_id (FK → agents)
- status, socket_from, socket_to
- bandwidth (0.0-1.0), latency_ms
- metadata (JSON)
- established_at, closed_at

**communication_graphs** - Multi-agent coordination graphs
- id (PK)
- root_task_id
- nodes (JSON array of agent IDs)
- execution_plan (JSON array of task IDs)
- metadata (JSON)
- created_at

**graph_edges** - Connections within a graph
- id (PK, autoincrement)
- graph_id (FK → communication_graphs)
- connection_id (FK → connections)

**graph_executions** - Execution tracking
- id (PK)
- graph_id (FK → communication_graphs)
- status, current_step
- completed_tasks, failed_tasks, active_connections (JSON arrays)
- results (JSON object)
- started_at, completed_at

**event_logs** - Audit trail (future)
- id (PK, autoincrement)
- event_type, entity_type, entity_id
- data (JSON)
- correlation_id
- timestamp

### Indexes

- All tables have indexes on status, timestamps, and foreign keys
- Agents indexed by role, status
- Tasks indexed by type, priority, agent, status
- Connections indexed by both agent IDs and sockets
- Events indexed by type, entity, correlation ID, and timestamp

### Constraints

- Check constraints on numeric ranges (load, success_rate, bandwidth, priority, level)
- Foreign key constraints with CASCADE/SET NULL policies
- Self-connection prevention on connections table

## Alembic Commands

```bash
# Check current revision
alembic current

# View migration history
alembic history --verbose

# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade all (drop all tables)
alembic downgrade base

# Generate new migration (autogenerate)
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

## Migration Workflow

### Creating New Migration

1. **Modify SQLAlchemy models** in `app/infrastructure/models.py`

2. **Generate migration**:
```bash
alembic revision --autogenerate -m "add new field to agents"
```

3. **Review generated migration** in `alembic/versions/`
   - Check upgrade() and downgrade() functions
   - Verify SQL statements
   - Add data migrations if needed

4. **Test migration**:
```bash
# Apply migration
alembic upgrade head

# Rollback to test downgrade
alembic downgrade -1

# Re-apply
alembic upgrade head
```

5. **Commit migration file** to git

### Example: Adding a New Field

```python
# In models.py
class AgentModel(Base):
    # ... existing fields ...
    specialization = Column(String(100), nullable=True)  # NEW
```

```bash
# Generate migration
alembic revision --autogenerate -m "add specialization to agents"

# Review generated file in alembic/versions/

# Apply migration
alembic upgrade head
```

## Connection String Formats

### PostgreSQL

```
postgresql://user:password@host:port/database
postgresql+asyncpg://user:password@host:port/database  # Async (application)
postgresql+psycopg2://user:password@host:port/database  # Sync (Alembic)
```

### Examples

```bash
# Local
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/switchboard

# Docker
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/switchboard

# Remote
DATABASE_URL=postgresql://user:pass@db.example.com:5432/switchboard

# With SSL
DATABASE_URL=postgresql://user:pass@db.example.com:5432/switchboard?sslmode=require
```

## Troubleshooting

### Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U postgres -d switchboard -h localhost

# Check port
sudo netstat -plnt | grep 5432
```

### Migration Conflicts

```bash
# Reset to base (WARNING: drops all data!)
alembic downgrade base
alembic upgrade head

# Or create new database
dropdb switchboard
createdb switchboard
alembic upgrade head
```

### Permission Errors

```sql
-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE switchboard TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
```

### View Schema

```sql
-- Connect to database
psql -U postgres -d switchboard

-- List tables
\dt

-- Describe table
\d agents
\d+ agents  # Detailed

-- View indexes
\di

-- View constraints
\d+ agents
```

## Backup and Restore

### Backup

```bash
# Dump database
pg_dump -U postgres switchboard > backup.sql

# Dump with compression
pg_dump -U postgres switchboard | gzip > backup.sql.gz

# Custom format (faster restore)
pg_dump -U postgres -Fc switchboard > backup.dump
```

### Restore

```bash
# From SQL
psql -U postgres switchboard < backup.sql

# From gzip
gunzip -c backup.sql.gz | psql -U postgres switchboard

# From custom format
pg_restore -U postgres -d switchboard backup.dump
```

## Performance Tuning

### Connection Pooling

Configured in `app/core/config.py`:

```python
DB_POOL_SIZE=20  # Number of connections in pool
DB_MAX_OVERFLOW=10  # Additional connections under load
```

### Query Optimization

```sql
-- Analyze tables
ANALYZE agents;
ANALYZE tasks;

-- View query performance
EXPLAIN ANALYZE SELECT * FROM tasks WHERE status = 'running';

-- Create additional indexes if needed
CREATE INDEX idx_custom ON table_name (column_name);
```

### Monitoring

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Long-running queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Kill query
SELECT pg_terminate_backend(pid);
```

## Testing

### Test Database

```bash
# Create test database
createdb switchboard_test

# Run migrations on test DB
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/switchboard_test \
alembic upgrade head

# Run tests
pytest tests/integration/
```

## Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: switchboard
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Next Steps

1. ✅ Database schema created
2. ✅ Migrations configured
3. ⏳ Update API endpoints to use database (next)
4. ⏳ Add database tests
5. ⏳ Setup database monitoring
6. ⏳ Configure backups

---

**Meta-Orchestrator Switchboard**
*PostgreSQL Database - Art Deco 1920s Telephonic Exchange*
