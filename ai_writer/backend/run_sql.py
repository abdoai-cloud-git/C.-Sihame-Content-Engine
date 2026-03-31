import os
import httpx
from dotenv import load_dotenv

load_dotenv()

project_ref = 'luwlndsvudlmhcorvqwy'
token = os.getenv('SUPABASE_ACCESS_TOKEN')

sql = """
CREATE TABLE IF NOT EXISTS drafts (
  draft_id TEXT PRIMARY KEY,
  raw_input TEXT NOT NULL,
  post_type TEXT NOT NULL,
  platform TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft_generated',
  model_used TEXT,
  angle TEXT, hook TEXT, body TEXT, cta TEXT,
  safety_flags TEXT DEFAULT '',
  approved_text TEXT,
  image_prompt TEXT,
  image_url TEXT,
  image_status TEXT DEFAULT 'pending',
  revision_history JSONB DEFAULT '[]',
  routing_metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
"""

url = f'https://api.supabase.com/v1/projects/{project_ref}/query'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = httpx.post(url, headers=headers, json={'query': sql})
print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
