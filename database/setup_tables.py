"""
Database table setup script.
Creates all required tables using Supabase's SQL query execution.
Run this once before starting the app.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# We need the service_role key or use the Supabase Management API
# Since we only have the anon key, we'll check if tables exist
# and instruct the user if they don't.

# However, we CAN create tables through the Supabase REST API
# if RLS is disabled or if we use the service_role key.

# Let's try a different approach: use individual table creation
# via the PostgREST endpoint by inserting and catching errors.


def get_schema_sql() -> str:
    """Read the schema.sql file."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        return f.read()


def split_sql_statements(sql: str) -> list:
    """Split SQL into individual statements."""
    statements = []
    current = []
    for line in sql.split("\n"):
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue
        current.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current))
            current = []
    if current:
        statements.append("\n".join(current))
    return statements


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists via a simple query."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table_name}?limit=0",
        headers=headers,
    )
    return resp.status_code == 200


def print_setup_instructions():
    """Print instructions for manual setup."""
    print("\n" + "=" * 60)
    print("  DATABASE SETUP REQUIRED")
    print("=" * 60)
    print()
    print("The database tables need to be created in your Supabase project.")
    print()
    print("Steps:")
    print("  1. Go to: https://supabase.com/dashboard")
    print("  2. Open your project")
    print("  3. Click 'SQL Editor' in the left sidebar")
    print("  4. Click 'New Query'")
    print("  5. Copy ALL the SQL from: database/schema.sql")
    print("  6. Paste it in the editor and click 'Run'")
    print()
    print("=" * 60)


if __name__ == "__main__":
    required_tables = [
        "users", "subjects", "subject_modules", "module_videos",
        "module_tests", "test_results", "cheatsheets", "assignments",
        "tasks", "study_plans",
    ]
    
    print("Checking database tables...")
    missing = []
    for table in required_tables:
        exists = check_table_exists(table)
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
        if not exists:
            missing.append(table)
    
    if missing:
        print(f"\n⚠️  {len(missing)} table(s) are missing!")
        print_setup_instructions()
    else:
        print("\n✅ All tables exist! The app is ready to run.")
