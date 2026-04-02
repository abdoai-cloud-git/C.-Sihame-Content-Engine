import os
import httpx
from dotenv import load_dotenv

load_dotenv()

project_ref = 'luwlndsvudlmhcorvqwy'
token = os.getenv('SUPABASE_ACCESS_TOKEN')
table_name = os.getenv("SUPABASE_DRAFTS_TABLE", "drafts")

sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS rejection_reason TEXT;"

url = f'https://api.supabase.com/v1/projects/{project_ref}/query'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print(f"Applying migration to project {project_ref}, table {table_name}...")
response = httpx.post(url, headers=headers, json={'query': sql})

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
