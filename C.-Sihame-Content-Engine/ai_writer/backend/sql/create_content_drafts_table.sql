CREATE TABLE IF NOT EXISTS content_drafts (
  draft_id TEXT PRIMARY KEY,
  raw_input TEXT NOT NULL,
  post_type TEXT NOT NULL,
  platform TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft_generated',
  model_used TEXT,
  angle TEXT,
  hook TEXT,
  body TEXT,
  cta TEXT,
  safety_flags TEXT DEFAULT '',
  approved_text TEXT,
  revision_history JSONB DEFAULT '[]',
  routing_metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
