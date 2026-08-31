CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE ROLE drishtimail_app LOGIN PASSWORD 'change-me-for-local-use' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;

CREATE TABLE IF NOT EXISTS evidence_objects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sha256 CHAR(64) NOT NULL UNIQUE,
  storage_key TEXT NOT NULL UNIQUE,
  filename TEXT NOT NULL,
  content_type TEXT NOT NULL,
  byte_size BIGINT NOT NULL CHECK (byte_size >= 0),
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidence_references (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  evidence_object_id UUID NOT NULL REFERENCES evidence_objects(id) ON DELETE RESTRICT,
  header_name TEXT,
  mime_part_index INTEGER,
  byte_start BIGINT NOT NULL CHECK (byte_start >= 0),
  byte_end BIGINT NOT NULL CHECK (byte_end >= byte_start),
  description TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidence_ledger (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sequence BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE NOT NULL,
  event_type TEXT NOT NULL,
  subject_id UUID NOT NULL,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT,
  payload_hash CHAR(64) NOT NULL,
  previous_hash CHAR(64),
  entry_hash CHAR(64) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS merkle_roots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  root_hash CHAR(64) NOT NULL UNIQUE,
  from_sequence BIGINT NOT NULL,
  to_sequence BIGINT NOT NULL,
  computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (to_sequence >= from_sequence)
);

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(320) NOT NULL UNIQUE,
  password_hash VARCHAR(512) NOT NULL,
  role VARCHAR(32) NOT NULL DEFAULT 'analyst',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sender VARCHAR(320) NOT NULL,
  subject VARCHAR(998) NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  verdict VARCHAR(20) NOT NULL DEFAULT 'Elevated',
  score INTEGER NOT NULL DEFAULT 0,
  confidence VARCHAR(20) NOT NULL DEFAULT 'Medium',
  status VARCHAR(20) NOT NULL DEFAULT 'New',
  evidence_reference TEXT NOT NULL,
  summary TEXT NOT NULL DEFAULT 'Awaiting analysis'
);

CREATE TABLE IF NOT EXISTS findings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id),
  title VARCHAR(256) NOT NULL,
  category VARCHAR(64) NOT NULL,
  severity VARCHAR(20) NOT NULL,
  contribution DOUBLE PRECISION NOT NULL DEFAULT 0,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS parsed_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  evidence_object_id UUID NOT NULL UNIQUE REFERENCES evidence_objects(id) ON DELETE RESTRICT,
  rfc_message_id VARCHAR(998),
  dedupe_key CHAR(64) NOT NULL UNIQUE,
  headers JSONB NOT NULL,
  plain_text TEXT NOT NULL DEFAULT '',
  attachment_count INTEGER NOT NULL DEFAULT 0,
  evidence_map JSONB NOT NULL,
  parsed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS authentication_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  spf VARCHAR(16) NOT NULL, dkim VARCHAR(16) NOT NULL, dmarc VARCHAR(16) NOT NULL,
  semantics_key VARCHAR(96) NOT NULL,
  establishes TEXT NOT NULL, does_not_establish TEXT NOT NULL, investigation_effect TEXT NOT NULL,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS url_artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  raw_url TEXT NOT NULL, normalized_url TEXT NOT NULL, provenance VARCHAR(24) NOT NULL DEFAULT 'body',
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS analysis_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT,
  result JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), title VARCHAR(256) NOT NULL,
  status VARCHAR(24) NOT NULL DEFAULT 'Open', owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
  notes JSONB NOT NULL DEFAULT '[]', created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS case_messages (
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  PRIMARY KEY (case_id, message_id)
);
CREATE TABLE IF NOT EXISTS platform_config (
  key VARCHAR(64) PRIMARY KEY, value JSONB NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION prevent_ledger_mutation()
RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'evidence_ledger is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS evidence_ledger_immutable ON evidence_ledger;
CREATE TRIGGER evidence_ledger_immutable
BEFORE UPDATE OR DELETE ON evidence_ledger
FOR EACH ROW EXECUTE FUNCTION prevent_ledger_mutation();

GRANT USAGE ON SCHEMA public TO drishtimail_app;
GRANT SELECT, INSERT, UPDATE ON messages TO drishtimail_app;
GRANT SELECT, INSERT, UPDATE ON cases, platform_config TO drishtimail_app;
GRANT SELECT, INSERT ON users, findings, evidence_objects, evidence_references, evidence_ledger, merkle_roots, parsed_messages, authentication_results, url_artifacts, analysis_runs, case_messages TO drishtimail_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO drishtimail_app;
REVOKE UPDATE, DELETE, TRUNCATE ON evidence_ledger FROM drishtimail_app;
