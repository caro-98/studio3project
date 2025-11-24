import os
import json
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "websites"
JSON_FILE = "fraud_results_final.json"

# Load JSON list
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

records = df.to_dict(orient="records")

# Remove ID so Supabase autogenerates primary key
for r in records:
    r.pop("id", None)

# Insert/upsert records
for r in records:
    response = supabase.table(TABLE_NAME).upsert(r).execute()
    print(response)

print(f"Uploaded {len(records)} OCC Table records to Supabase.")
