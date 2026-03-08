# test_connection.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

assert url is not None, "SUPABASE_URL not found in .env"
assert key is not None, "SUPABASE_KEY not found in .env"

supabase: Client = create_client(url, key)

# Try a simple query on a small table, e.g., events
try:
    response = supabase.table("events").select("*").limit(1).execute()
    if response.data:
        print("✅ Connection successful! Sample row:", response.data[0])
    else:
        print("✅ Connection successful! Table is empty.")
except Exception as e:
    print("❌ Connection failed:", e)