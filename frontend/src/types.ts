export interface Message {
  id: string;
  sender: string;
  subject: string;
  received_at: string;
  verdict: 'Critical' | 'High' | 'Elevated' | 'Low';
  score: number;
  confidence: 'High' | 'Medium' | 'Low';
  status: 'New' | 'Triage' | 'Investigating' | 'Closed';
  evidence_reference: string;
  summary: string;
}

export interface DashboardSummary {
  total_messages: number;
  critical: number;
  high: number;
  elevated: number;
  low: number;
  new: number;
  total_cases: number;
  active_campaigns: number;
}

export interface ScoreContribution {
  signal: string;
  family: string;
  points: number;
  reason: string;
  evidence_reference_id?: string | null;
}

export interface FamilyBreakdownItem {
  allocated_points: number;
  ceiling_points: number;
}

export interface ScoreData {
  value: number;
  verdict: 'Critical' | 'High' | 'Elevated' | 'Low';
  confidence: 'High' | 'Medium' | 'Low';
  contributions: ScoreContribution[];
  disclaimer: string;
  first_contact_suppressed?: boolean;
  suppression_reason?: string | null;
}

export interface AuthenticationSemantics {
  spf: string;
  dkim: string;
  dmarc: string;
  spf_aligned: boolean;
  dkim_aligned: boolean;
  arc_status: string;
  forwarding_detected: boolean;
  semantics_key: string;
  establishes: string;
  does_not_establish: string;
  investigation_effect: string;
  is_lookalike_authenticated?: boolean;
}

export interface DeliveryHopItem {
  hop_no: number;
  claimed_host?: string;
  real_ip?: string;
  rdns?: string;
  tls_version?: string;
  delay_seconds?: number;
  trust_status: 'internal_trusted' | 'perimeter_ingress' | 'untrusted_external' | 'unverified';
  raw_header?: string;
}

export interface OriginInfo {
  ip: string;
  candidate_ip?: string;
  country?: string;
  country_code?: string;
  region?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  asn?: string;
  isp?: string;
  infra_type: 'datacenter' | 'residential' | 'vpn_proxy' | 'tor_node' | 'unknown';
  confidence: string;
  caveat: string;
  hop_no?: number;
  justification?: string;
}

export interface UrlArtifactItem {
  raw_url: string;
  normalized_url: string;
  provenance: string;
  destination_host?: string;
  redirect_chain?: string[];
  anchor_text?: string;
  mismatch_flag: boolean;
}

export interface QrResultItem {
  payload?: string;
  provenance: string;
  rotation?: number;
  undecodable?: boolean;
  bounding_box?: number[];
}

export interface EvidenceConflictItem {
  conflict_type: string;
  rule_id: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  title: string;
  summary: string;
  evidence_side_a: string;
  evidence_side_b: string;
  investigative_guidance?: string;
  reconciliation_effect?: string;
  score_adjustment?: number;
  evidence_ref_a_id?: string;
  evidence_ref_b_id?: string;
}

export interface AnalysisRunResult {
  analysed_at: string;
  score: ScoreData;
  authentication: AuthenticationSemantics;
  delivery_path: DeliveryHopItem[];
  origin: OriginInfo;
  domain_intel?: {
    domain: string;
    age_days?: number;
    high_risk_flags?: string[];
  };
  detections: {
    classification: {
      predicted_class: string;
      probabilities: Record<string, number>;
      confidence: string;
    };
    social_engineering: Array<{ title: string; category: string; description: string }>;
    bec_patterns: Array<{ title: string; pattern_type: string; description: string }>;
    impersonation: Array<{ title: string; type: string; description: string }>;
    lookalike_domains: Array<{ title: string; domain: string; description: string; target?: string }>;
    concealment: Array<{ title: string; description: string }>;
    thread_hijack: Array<{ title: string; description: string }>;
  };
  urls: UrlArtifactItem[];
  qr_results: QrResultItem[];
  conflicts: EvidenceConflictItem[];
  scenario: {
    scenario: string;
    hypothesis: string;
    confidence: string;
    caveat: string;
  };
  first_contact?: {
    is_first_contact: boolean;
    familiarity_band: string;
    sighting_count: number;
    suppressed?: boolean;
  };
  structural_fingerprint?: {
    hash: string;
  };
  indicators?: Array<{
    indicator_type: string;
    value: string;
    provenance?: string;
  }>;
}

export interface CaseItem {
  id: string;
  title: string;
  status: string;
  owner_id?: string | null;
  notes?: Array<{ at: string; text: string }>;
  created_at: string;
  message_ids?: string[];
}

export interface CampaignItem {
  id: string;
  name: string;
  shared_indicators?: string[];
  score?: number;
  status?: string;
  created_at?: string;
  first_seen?: string;
  last_seen?: string;
  message_count?: number;
  shared_ip_count?: number;
  shared_domain_count?: number;
  shared_structural_hashes?: string[];
  confidence?: string;
}

export interface GraphNodeItem {
  id: string;
  node_type: string;
  value: string;
  sighting_count?: number;
  first_seen?: string;
  last_seen?: string;
}

export interface GraphEdgeItem {
  id?: string;
  from_node?: string;
  to_node?: string;
  source_id?: string;
  target_id?: string;
  edge_type?: string;
  relation_type?: string;
  weight?: number;
  created_at?: string;
}

export interface ModelRegistryItem {
  id?: string;
  model_name?: string;
  version: string;
  accuracy?: number;
  macro_f1?: number;
  per_class_metrics?: Record<string, { precision: number; recall: number; f1: number; support: number }>;
  confusion_matrix?: Record<string, Record<string, number>>;
  limitations_disclosure?: string[];
  metrics?: {
    accuracy: number;
    macro_f1: number;
    per_class: Record<string, { precision: number; recall: number; f1: number; support: number }>;
    confusion_matrix: Record<string, Record<string, number>>;
  };
  corpus_manifest?: {
    corpus_id?: string;
    name?: string;
    total_samples?: number;
    explicit_limitations?: string;
  };
  trained_at?: string;
  calibrated_at?: string;
}

export interface LedgerItem {
  sequence: number;
  event_type: string;
  subject_id: string;
  evidence_reference_id: string;
  payload_hash: string;
  previous_hash?: string;
  entry_hash: string;
  created_at: string;
}
