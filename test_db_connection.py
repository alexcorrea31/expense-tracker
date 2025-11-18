import os
import psycopg2

# Get the connection string from the environment
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("❌ DATABASE_URL environment variable not found.")
else:
    print(f"🔗 Connecting to: {db_url.split('@')[-1]} ...")

try:
    # Connect to Neon PostgreSQL
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("✅ Connected successfully!")
    print(f"PostgreSQL version: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print("❌ Connection failed.")
    print("Error details:", e)
