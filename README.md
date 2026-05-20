# BKMS1 Term Project: DB Doctor

Diagnosing PostgreSQL Performance Issues with LLM Agents

---

## File Structure

```
├── README.md                      ← This file (setup & usage guide)
├── init_db.sql                    ← DB schema + seed data (65,000 rows)
├── db_connect.py                  ← DB connection & run_sql utility
├── agent_example.py               ← LLM agent loop boilerplate
├── anomaly_slow_query.py          ← Scenario A: Slow Query skeleton
├── anomaly_lock_contention.py     ← Scenario B: Lock Contention skeleton
├── anomaly_index_bloat.py         ← Scenario C: Index Bloat skeleton
```

---

## 1. Setup

### 1-1. Prerequisites

- Python 3.9+
- PostgreSQL 14+ (assumed to be already installed)
- Anthropic API key (or OpenAI API key)

### 1-2. Install Python Packages

```bash
pip install psycopg2-binary anthropic
```

If using OpenAI instead:
```bash
pip install psycopg2-binary openai
```

### 1-3. Create and Initialize the Database

```bash
# 1) Create the database
createdb -U postgres dbdoctor

# 2) Enable pg_stat_statements extension
#    Make sure the following line exists in your postgresql.conf:
#    shared_preload_libraries = 'pg_stat_statements'
#    A PostgreSQL restart may be required after this change.

# 3) Run the init script (creates tables + inserts seed data)
psql -U postgres -d dbdoctor -f init_db.sql
```

On success, you should see:
```
 table_name | row_count
------------+-----------
 customers  |      5000
 books      |     10000
 orders     |     50000
```

### 1-4. Configure DB Connection

Edit `DB_CONFIG` in `db_connect.py` to match your environment, or set environment variables:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=dbdoctor
export DB_USER=postgres
export DB_PASSWORD=postgres
```

Test the connection:
```bash
python db_connect.py
```

### 1-5. Set Your API Key

```bash
# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."
```

---

## 2. Workflow

### Step 1: Inject the Anomaly

Open the skeleton file for your team's chosen scenario, fill in the TODO sections, and run it.

```bash
# Scenario A
python anomaly_slow_query.py

# Scenario B (run the agent in another terminal within 30 seconds)
python anomaly_lock_contention.py

# Scenario C
python anomaly_index_bloat.py
```

### Step 2: Manual Diagnosis

Query the system views yourself in psql.

```bash
psql -U postgres -d dbdoctor
```

```sql
-- Example: find the slowest queries (Scenario A)
SELECT ...
FROM pg_stat_statements
ORDER BY ... DESC
LIMIT ...;
```

### Step 3: Run the Agent

Modify `agent_example.py` (system prompt, tools, termination logic) and let the agent diagnose the anomaly.

```bash
python agent_example.py
```

---

## 3. Resetting the Database

To start fresh:

```bash
dropdb -U postgres dbdoctor
createdb -U postgres dbdoctor
psql -U postgres -d dbdoctor -f init_db.sql
```

---

## 5. References

- [PostgreSQL Monitoring Statistics](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [Anthropic Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

---

This project is inspired by the DB diagnosis scenario (Appendix A.6) in Zhu et al., "MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents" (arXiv:2503.01935).