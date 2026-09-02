CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE ROLE drishtimail_app LOGIN PASSWORD 'change-me-for-local-use' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;

-- M7 / F7 Core Evidence Tables
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
  role VARCHAR(32) NOT NULL DEFAULT 'analyst', -- admin, investigator, analyst, auditor, compliance
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- M1 Ingestion & Messages
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sender VARCHAR(320) NOT NULL,
  subject VARCHAR(998) NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  verdict VARCHAR(20) NOT NULL DEFAULT 'Elevated', -- Low, Elevated, High, Critical
  score INTEGER NOT NULL DEFAULT 0,
  confidence VARCHAR(20) NOT NULL DEFAULT 'Medium', -- Low, Medium, High
  status VARCHAR(20) NOT NULL DEFAULT 'New', -- New, Investigating, Escalated, Closed
  evidence_reference TEXT NOT NULL,
  summary TEXT NOT NULL DEFAULT 'Awaiting analysis'
);

CREATE TABLE IF NOT EXISTS mime_parts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  evidence_object_id UUID NOT NULL REFERENCES evidence_objects(id) ON DELETE RESTRICT,
  part_index INTEGER NOT NULL,
  content_type VARCHAR(255) NOT NULL,
  filename VARCHAR(512),
  byte_start BIGINT NOT NULL CHECK (byte_start >= 0),
  byte_end BIGINT NOT NULL CHECK (byte_end >= byte_start),
  sha256 CHAR(64) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS parsed_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  evidence_object_id UUID NOT NULL UNIQUE REFERENCES evidence_objects(id) ON DELETE RESTRICT,
  rfc_message_id VARCHAR(998),
  dedupe_key CHAR(64) NOT NULL UNIQUE,
  headers JSONB NOT NULL,
  plain_text TEXT NOT NULL DEFAULT '',
  html_body TEXT NOT NULL DEFAULT '',
  attachment_count INTEGER NOT NULL DEFAULT 0,
  evidence_map JSONB NOT NULL,
  parsed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- M3 Header & Protocol
CREATE TABLE IF NOT EXISTS authentication_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  spf VARCHAR(16) NOT NULL,
  dkim VARCHAR(16) NOT NULL,
  dmarc VARCHAR(16) NOT NULL,
  spf_aligned BOOLEAN NOT NULL DEFAULT false,
  dkim_aligned BOOLEAN NOT NULL DEFAULT false,
  arc_status VARCHAR(16) NOT NULL DEFAULT 'none',
  forwarding_detected BOOLEAN NOT NULL DEFAULT false,
  semantics_key VARCHAR(96) NOT NULL,
  establishes TEXT NOT NULL,
  does_not_establish TEXT NOT NULL,
  investigation_effect TEXT NOT NULL,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS delivery_hops (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  hop_no INTEGER NOT NULL,
  timestamp TIMESTAMPTZ,
  claimed_host TEXT,
  real_ip TEXT,
  rdns TEXT,
  tls_version TEXT,
  delay_seconds DOUBLE PRECISION,
  trust_status VARCHAR(32) NOT NULL DEFAULT 'unverified', -- verified_internal, earliest_reliable, unverified
  raw_header TEXT NOT NULL
);

-- M4 Origin & Geolocation
CREATE TABLE IF NOT EXISTS origin_enrichments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  ip TEXT NOT NULL,
  country VARCHAR(100),
  country_code VARCHAR(8),
  region VARCHAR(100),
  city VARCHAR(100),
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  accuracy_radius INTEGER,
  asn INTEGER,
  isp TEXT,
  infra_type VARCHAR(32) NOT NULL DEFAULT 'unknown', -- datacenter, residential, business, vpn_proxy, relay, unknown
  confidence VARCHAR(20) NOT NULL DEFAULT 'Limited',
  caveat TEXT NOT NULL,
  enriched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS domain_intel (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  domain VARCHAR(255) NOT NULL UNIQUE,
  registrar TEXT,
  creation_date TIMESTAMPTZ,
  age_days INTEGER,
  nameservers JSONB NOT NULL DEFAULT '[]',
  mail_records JSONB NOT NULL DEFAULT '[]',
  high_risk_flags JSONB NOT NULL DEFAULT '[]',
  checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- M9 Content & URL Engine
CREATE TABLE IF NOT EXISTS url_artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  raw_url TEXT NOT NULL,
  normalized_url TEXT NOT NULL,
  provenance VARCHAR(24) NOT NULL DEFAULT 'body', -- body, qr_inline, qr_attachment, attachment_link
  destination_host TEXT,
  redirect_chain JSONB NOT NULL DEFAULT '[]',
  anchor_text TEXT,
  mismatch_flag BOOLEAN NOT NULL DEFAULT false,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS attachment_artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  filename VARCHAR(512) NOT NULL,
  declared_mime VARCHAR(255),
  true_mime VARCHAR(255),
  byte_size BIGINT NOT NULL,
  sha256 CHAR(64) NOT NULL,
  static_indicators JSONB NOT NULL DEFAULT '[]',
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT
);

-- M2 Detections & Findings
CREATE TABLE IF NOT EXISTS findings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  title VARCHAR(256) NOT NULL,
  category VARCHAR(64) NOT NULL,
  severity VARCHAR(20) NOT NULL,
  contribution DOUBLE PRECISION NOT NULL DEFAULT 0,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS analysis_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT,
  result JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- M10 Evidence Conflicts (F1)
CREATE TABLE IF NOT EXISTS evidence_conflicts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  conflict_type VARCHAR(64) NOT NULL,
  summary TEXT NOT NULL,
  severity VARCHAR(20) NOT NULL DEFAULT 'Medium',
  evidence_ref_a_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT,
  evidence_ref_b_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT,
  detail JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- M11 Explainable Scoring (F8)
CREATE TABLE IF NOT EXISTS score_explanations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  score INTEGER NOT NULL,
  verdict VARCHAR(20) NOT NULL,
  confidence VARCHAR(20) NOT NULL,
  contributions JSONB NOT NULL,
  disclaimer TEXT NOT NULL,
  first_contact_suppressed BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- M5 Correlation Graph, Campaign Memory (F6) & First-Contact Baseline (F4)
CREATE TABLE IF NOT EXISTS graph_nodes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  node_type VARCHAR(32) NOT NULL, -- domain, ip, structural_hash, email, campaign, message
  value TEXT NOT NULL UNIQUE,
  first_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
  sighting_count INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS graph_edges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_node UUID NOT NULL REFERENCES graph_nodes(id) ON DELETE RESTRICT,
  to_node UUID NOT NULL REFERENCES graph_nodes(id) ON DELETE RESTRICT,
  edge_type VARCHAR(32) NOT NULL, -- shares_ip, shares_domain, shares_fingerprint, originated_from, contains_url
  weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
  evidence_reference_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS indicator_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  indicator_type VARCHAR(32) NOT NULL,
  value TEXT NOT NULL,
  first_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
  sighting_count INTEGER NOT NULL DEFAULT 1,
  distinct_cases INTEGER NOT NULL DEFAULT 0,
  familiarity_band VARCHAR(20) NOT NULL DEFAULT 'Novel', -- Novel, Rare, Common
  CONSTRAINT uq_indicator UNIQUE(indicator_type, value)
);

CREATE TABLE IF NOT EXISTS structural_fingerprints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL UNIQUE REFERENCES messages(id) ON DELETE RESTRICT,
  skeleton_hash CHAR(64) NOT NULL,
  raw_skeleton TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(256) NOT NULL,
  shared_indicators JSONB NOT NULL DEFAULT '[]',
  score DOUBLE PRECISION NOT NULL DEFAULT 0,
  status VARCHAR(24) NOT NULL DEFAULT 'Active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS campaign_messages (
  campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  primary_evidence_ref_id UUID NOT NULL REFERENCES evidence_references(id) ON DELETE RESTRICT,
  PRIMARY KEY (campaign_id, message_id)
);

-- M6 Cases & Workflow
CREATE TABLE IF NOT EXISTS cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(256) NOT NULL,
  status VARCHAR(24) NOT NULL DEFAULT 'Open',
  owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
  notes JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS case_messages (
  case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  PRIMARY KEY (case_id, message_id)
);

-- M8 / M12 Platform Config & Model Registry (F2)
CREATE TABLE IF NOT EXISTS platform_config (
  key VARCHAR(64) PRIMARY KEY,
  value JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  version VARCHAR(64) NOT NULL UNIQUE,
  trained_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  calibrated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metrics JSONB NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT false,
  corpus_manifest JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  action VARCHAR(64) NOT NULL,
  target_type VARCHAR(64) NOT NULL,
  target_id UUID,
  details JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS retention_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  data_class VARCHAR(64) NOT NULL UNIQUE,
  retention_days INTEGER NOT NULL,
  legal_hold_exempt BOOLEAN NOT NULL DEFAULT true,
  is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS alert_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(128) NOT NULL,
  score_threshold INTEGER NOT NULL DEFAULT 75,
  destinations JSONB NOT NULL DEFAULT '["console"]',
  is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL REFERENCES messages(id) ON DELETE RESTRICT,
  rule_id UUID REFERENCES alert_rules(id) ON DELETE SET NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'Fired',
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Immutable Ledger Trigger
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

-- Role Grants
GRANT USAGE ON SCHEMA public TO drishtimail_app;
GRANT SELECT, INSERT, UPDATE ON messages, cases, platform_config, indicator_history, campaigns, model_registry, retention_policies, alert_rules, alerts TO drishtimail_app;
GRANT SELECT, INSERT ON users, findings, evidence_objects, evidence_references, evidence_ledger, merkle_roots, mime_parts, parsed_messages, authentication_results, delivery_hops, origin_enrichments, domain_intel, url_artifacts, attachment_artifacts, analysis_runs, evidence_conflicts, score_explanations, graph_nodes, graph_edges, structural_fingerprints, campaign_messages, case_messages, audit_logs TO drishtimail_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO drishtimail_app;
REVOKE UPDATE, DELETE, TRUNCATE ON evidence_ledger FROM drishtimail_app;

