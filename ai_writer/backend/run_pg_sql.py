import os
import psycopg2

conn_str = "postgresql://postgres:Abdomangrgrabdo1!@db.luwlndsvudlmhcorvqwy.supabase.co:5432/postgres"

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

print("Connecting to database...")
try:
    with psycopg2.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
            print("Successfully created drafts table!")
except Exception as e:
    print("Database Error:", e)
