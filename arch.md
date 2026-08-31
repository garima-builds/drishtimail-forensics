# Architecture — DrishtiMail Forensics
# Generated: 2026-08-31 | Revised: 2026-08-31 (PostgreSQL + Architecture Update v2) | Reviewed by: Ashutosh Garg
# Source: mvp-scope.md (Value-first framing, 12 features in scope)

## Client Summary
This build produces a system that examines incoming email, decides how dangerous each message
is and explains exactly why, reconstructs the path the message travelled, estimates where it
came from, links it to earlier incidents, and produces a report whose every statement traces
back to a specific location in the original message. Work proceeds in three tiers: the evidence
record and the explanation layer first, then correlation across incidents, then measurement and
validation. The system's central claim is that its findings can be independently checked — a
report exported today can be verified by someone with no access to the system, and any later
alteration is detectable. Two risks remain open: the training data available cannot represent
the institution's own mail, and the scope has grown considerably against the size of the team.
The system runs entirely on hardware the team already has, with no paid services anywhere.

## Tech Stack
| Layer | Decision | Status |
|---|---|---|
| Backend | FastAPI (Python 3.11) | ✓ Confirmed |
| Database | PostgreSQL | ✓ Confirmed — reversed from MongoDB 2026-08-31; v2's evidence design requires database-enforced append-only writes and constraint-enforced evidence references |
| Frontend | React + TypeScript | ✓ Confirmed |
| Queue / workers | Redis + Celery | ✓ Confirmed |
| Object storage | MinIO (object-lock) | ✓ Confirmed — write-once original messages and exported reports |
| ML | scikit-learn baseline, DistilBERT embeddings, XGBoost fusion | ✓ Confirmed |
| Scoring | Weighted-additive model, hand-implemented | ✓ Confirmed — v2 §5.8. Explanation is the requirement, so opaque aggregation is disqualified; SHAP is no longer needed for M11 |
| Correlation graph | PostgreSQL recursive CTEs over a typed edge table | ✓ Confirmed — v2 names the relational option the safe default at prototype scale |
| Search | PostgreSQL full-text search | ✓ Confirmed |
| Tamper evidence | Hash-chained ledger table + periodic Merkle root, exported with each report | ✓ Confirmed — v2 §5.7. No external anchoring service, no distributed ledger, no budget |
| QR decoding | Open-source symbol reader | [STRAWMAN] — licence unresolved; ZBar is LGPL, PyMuPDF (rasterisation) is AGPL |
| Geolocation | MaxMind GeoLite2 (offline DB) | ✓ Confirmed |
| Reporting | WeasyPrint | ✓ Confirmed |
| Infra | Docker Compose, self-hosted | ✓ Confirmed — all cloud defaults budget-eliminated |

## Components

### M1 — Ingestion & Normalisation
- IngestAPI (FastAPI) — `/ingest/upload`, `/ingest/headers`, `/analyze`
- GmailConnector (Python) — mail platform API polling, the primary feed
- ImapConnector, JournalReceiver (Python) — secondary ingestion routes
- MimeParser (Python) — MIME tree → headers, bodies, attachments; malformed-tolerant
- Deduplicator (Python) — Message-ID + body hash
- EvidenceStore (MinIO + PostgreSQL) — SHA-256 at ingest, write-once original, byte-offset addressing for evidence references

### M2 — Detection Engine
- FeatureExtractor (Python) — text, header and infrastructure feature families
- ClassifierService (XGBoost + DistilBERT) — six-class probability output
- SocialEngineeringDetector (Python) — urgency, authority, secrecy, financial instruction
- BecPatternDetector (Python) — payment diversion, fake invoice, payroll, gift card
- ImpersonationDetector (Python) — display name vs protected list
- LookalikeDomainDetector (Python) — homoglyph, IDN/punycode, edit distance, TLD swap
- ConcealmentDetector (Python) — hidden text, zero-width characters, tracking pixels
- ThreadHijackDetector (Python)
- MultilingualAnalyzer (Python)
- FeedbackQueue (Celery) — analyst corrections → retraining queue

*URL, attachment and scoring responsibilities extracted to M9 and M11 per v2. M2 now emits
probabilities and named indicators; it no longer computes the verdict score.*

### M3 — Header & Protocol Analysis
- ReceivedChainParser (Python) — chronological hop reconstruction
- TrustBoundaryResolver (Python) — earliest reliable node determination
- AuthValidator (Python) — SPF, DKIM, DMARC with alignment checking
- ArcEvaluator (Python) — forwarding-chain evaluation
- AuthResultsCrosschecker (Python) — own computation vs headers present
- HeaderAnomalyDetector, RelayCharacteristicDetector (Python)
- AuthSemanticsTable (data + Python) — **F5**: lookup over the (SPF, DKIM, DMARC, SPF-alignment, DKIM-alignment, forwarding-detected) tuple, returning three authored prose fields — establishes / does not establish / effect on this investigation

### M4 — Origin Traceability & Location
- OriginSelector (Python) — earliest reliable IP with written justification
- GeoResolver (GeoLite2), AsnResolver, InfraClassifier (Python)
- DomainIntelService (Python) — WHOIS/RDAP, age, registrar, nameservers, MX
- PassiveDnsClient (Python)
- EnrichmentCache (Redis) — TTL cache; the primary defence against quota exhaustion
- TraceMapUI (React + Leaflet) — hop polylines, mandatory confidence banner

### M5 — Investigation & Correlation Graph
- IocExtractor (Python)
- ThreatIntelClient (Python) — VirusTotal, URLhaus, PhishTank; optional, never load-bearing
- ThreatFeedImporter (Python) — manual CSV/Excel import
- IndicatorHistoryIndex (PostgreSQL) — **F4**: first-seen, sighting count, distinct case count, familiarity band
- FirstContactScorer (Python) — **F4**: capped low-weight signal with the guard-rail assertion
- StructuralFingerprinter (Python) — **F6**: strips text, keeps HTML tag skeleton and attribute order, computes a similarity signature
- CampaignGraphService (PostgreSQL recursive CTE) — **F6**: typed nodes and edges, explainable shared-indicator scoring
- OriginScenarioClassifier, AttributionSummarizer (Python)
- IocExporter (Python) — STIX 2.1 / MISP / CSV
- GraphExplorerUI (React + Cytoscape.js) — pivot on node, every edge clickable to its justifying evidence

### M6 — Alerting, Dashboard & Reporting
- AlertService (Celery) — threshold evaluation, channel fan-out
- QueueUI, EmailDetailUI, CaseUI, ExecutiveDashboardUI (React)
- AuthSemanticsPanel, ConflictPanel, ScorePanel, LedgerPanel (React) — the surfaces for F5, F1, F8 and F7
- CaseService (FastAPI) — CRUD + status workflow
- ReportGenerator (WeasyPrint) — forensic PDF, evidence-integrity page, Merkle root, per-finding evidence references
- CertificateTemplateService (Python) — BSA §63 admissibility template
- SearchService (PostgreSQL FTS) — full-text + indicator search
- EndUserReportIntake (FastAPI)

### M7 — Evidence Integrity Layer
- AuthService (FastAPI + JWT) — five-role RBAC
- EvidenceReferenceService (PostgreSQL) — **F7 layer 1**: binds every finding to header name, MIME part index and byte offset in the preserved original. A finding without one cannot be written — NOT NULL constraint plus foreign key, not convention
- LedgerService (PostgreSQL) — **F7 layer 2**: append-only hash-chained table. Application role holds INSERT only; UPDATE and DELETE revoked and additionally blocked by trigger
- MerkleRootService (Python) — **F7 layer 3**: periodic root over rows since the last root, exported with each report
- VerifierTool (standalone Python script) — recomputes original hash, per-finding artifact hashes and the ledger chain; runs with no access to the live system
- MaskingService (Python) — default-on masking, audited reveal
- RetentionService (Celery) — per-class purge with purge log
- ResidencyGuard (config) — storage-location enforcement

### M8 — Administration
- AdminAPI (FastAPI), AdminUI (React)
- VipListService — protected brands and individuals
- TrustedMtaService — trusted internal mail servers
- AllowBlockListService — entries with expiry
- ScoringConfigService — M11 weight ceilings, thresholds, F4 suppression floor
- ModelRegistry — version, training date, metrics written by M12, calibration date, rollback

### M9 — URL & Embedded Content Threat Engine
- UrlExtractor (Python) — hyperlinks from text and HTML bodies
- QrDecoder (Python + symbol reader) — **F3**: inline and referenced images, image attachments, rasterised document pages; grayscale, upscale, adaptive threshold, all four rotations before declaring failure
- QrPresenceDetector (Python) — **F3**: emits "QR present, undecodable" when a finder pattern is found but decoding fails
- UrlNormalizer (Python) — converges hyperlink and QR-sourced URLs into one set, provenance tagged
- RedirectExpander (Python) — shortener and redirect chain resolution
- DisplayDestinationComparator (Python) — anchor text vs resolved host
- TyposquatChecker (Python) — shared logic with M2's LookalikeDomainDetector
- AttachmentAnalyzer (Python, network-isolated container) — static indicators only, never executed

### M10 — Evidence Conflict Detector
- ConflictRuleEngine (Python) — evaluates the rule table over module outputs
- ConflictRuleTable (data) — authenticated-but-misaligned, reply-path divergence, authentication-pass vs content-risk, authentication-fail vs benign-content, display vs destination, QR vs body divergence, geography vs claim, header vs relay timing, feed vs baseline
- ConflictNarrator (Python) — renders each conflict quoting both sides of evidence

### M11 — Explainable Threat Scoring
- SignalNormalizer (Python) — per-family normalisation to a common strength scale
- WeightedScorer (Python) — weight × strength, conflict adjustment from M10, clamped 0–100
- FirstContactGuard (Python) — assertion that removing first-contact signals cannot drop the verdict below threshold; downgrade and record if it does
- ScoreExplanation (Python) — ranked contributions with point values summing visibly to the total, confidence band, fixed disclaimer text, and a link from each contribution to its M7 evidence reference

### M12 — ML Evaluation & Model Validation
- EvaluationRunner (Python) — held-out split, per-class precision, recall, F1
- CorpusManifest (data) — test-set size and an explicit statement of what the corpus does not cover
- EvaluationDashboardUI (React) — admin-only, off the per-email path
- Writes results to M8's ModelRegistry

**Shared:** EvidenceStore — [M1, M6, M7]
**Shared:** LedgerService + EvidenceReferenceService — [every module that produces a finding]
**Shared:** AuthService — [every API and UI surface]
**Shared:** TrustBoundaryResolver — [M3, M4]
**Shared:** EnrichmentCache — [M4, M5, M9]
**Shared:** TyposquatChecker — [M2, M9]
**Shared:** IndicatorHistoryIndex — [M5 F4, M5 F6]
**Shared:** VipListService — [M2, M8]
**Shared:** TrustedMtaService — [M3, M8]

## Data Model Hints
### M1 — Ingestion
- `messages` — sha256_raw, ingested_at, source, raw_uri → MinIO, parse_status
- `mime_parts` — message_id, part_index, content_type, byte_offset, byte_length; the addressing target for evidence references

### M2 / M9 — Analysis
- `analyses` — message_id, class_probabilities, model_version, analysed_at
- `indicators_found` — analysis_id, family, name, strength, evidence_ref_id
- `urls` — message_id, raw_url, normalised_url, provenance (body|qr|attachment), final_host, redirect_chain[]
- `attachments` — message_id, filename, true_type, claimed_type, sha256, static_indicators[]

### M3 / M4 — Trace
- `hops` — message_id, hop_no, timestamp, claimed_host, real_ip, rdns, tls, delay, trust_status
- `auth_results` — message_id, spf, dkim, dmarc, spf_aligned, dkim_aligned, forwarding_detected, semantics_key
- `enrichment` — key (ip|domain), geo, asn, infra_type, whois, fetched_at, ttl

### M5 — Correlation
- `graph_nodes` — node_id, node_type, value
- `graph_edges` — from_node, to_node, edge_type, weight, evidence_ref_id; traversed by recursive CTE
- `indicator_history` — indicator_type, value, first_seen, sighting_count, distinct_cases
- `campaigns` — campaign_id, shared_indicators[], score, member_message_ids[]
- `fingerprints` — message_id, skeleton_signature

### M6 — Cases
- `cases` — case_id, status, owner, message_ids[], notes[], timeline[]

### M7 — Evidence (the integrity core)
- `findings` — finding_id, case_id, source_module, **evidence_ref_id NOT NULL**, extracted_at, artifact_hash
- `evidence_refs` — ref_id, message_id, header_name | mime_part_index, byte_offset, byte_length
- `ledger` — seq, prev_hash, content_hash, payload, created_at; **INSERT-only role grant, UPDATE/DELETE revoked and trigger-blocked**
- `merkle_roots` — root_id, root_hash, from_seq, to_seq, computed_at

### M8 / M12 — Configuration and evaluation
- `config` — vip_list, trusted_mtas, allow_block, weight_ceilings, thresholds, first_contact_floor
- `models` — version, trained_at, calibrated_at, metrics_json, corpus_manifest_id, artifact_uri

## Integration Points
| System | Approach | Risk | Open Questions |
|---|---|---|---|
| Institutional mail platform API | OAuth service account, scheduled poll | MED [STRAWMAN] | Is a test account provisioned? Which scopes are grantable? |
| QR decoding library | Bundled open-source symbol reader | MED [STRAWMAN] | ZBar is LGPL, PyMuPDF is AGPL — which decoder, and does distribution change the answer? |
| Public phishing corpora | Offline download, held-out split | MED [STRAWMAN] | Licence terms for training use and redistribution unconfirmed |
| Malicious-file reputation feed | REST, cached, enrich-on-miss | MED | ~5,760 lookups/day vs 10,000 messages/hour. Severity reduced — F4 and F6 need zero feed calls, so this constrains an enhancement, not the core path |
| WHOIS / RDAP | REST, cached | MED | Registrant fields redacted under GDPR — is domain age alone sufficient? |
| Passive DNS | REST, cached | MED | Which provider has a usable free tier? |
| Phishing URL feeds | REST, cached | LOW | One requires registration on unconfirmed terms; one is open |
| IP geolocation database | Offline DB, periodic refresh | LOW | Licence permits this use — confirm before distribution |
| Manual threat import | CSV/Excel upload | LOW | Column schema not yet defined |

*External evidence anchoring has been removed from this table. v2 §5.7 downgrades it to optional;
the hash-chained ledger with exported Merkle root achieves tamper-evidence without it.*

## Build Order
Sequenced to v2 §7's P0/P1/P2 tiers, with foundations preceding tier 1.

**Foundations**
1. AuthService + PostgreSQL schema + LedgerService + EvidenceReferenceService — every finding written by any module needs both; retrofitting evidence references is not possible
2. EvidenceStore + MimeParser + IngestAPI — nothing is analysable before it is received, hashed and byte-addressable
3. TrustedMtaService + VipListService + ScoringConfigService — M3's trust boundary, M2's impersonation detection and M11's weights are undefined without them

**P0 — the demonstration depends on these**
4. MerkleRootService + VerifierTool (F7) — completes the evidence spine everything else writes into
5. ReceivedChainParser + TrustBoundaryResolver + AuthValidator + AuthSemanticsTable (F5) — cheapest build, highest explanatory value
6. UrlExtractor + RedirectExpander + DisplayDestinationComparator + QrDecoder (F3, M9) — self-contained, no external dependency
7. FeatureExtractor + ClassifierService — M11 consumes its probabilities
8. SignalNormalizer + WeightedScorer + ScoreExplanation (F8, M11) — needs F5 and M9 signals; a scorer with two inputs demonstrates worse than none
9. ConflictRuleEngine + ConflictNarrator (F1, M10) — needs F5 and M2 outputs to compare

**P1 — materially strengthens the demonstration**
10. EnrichmentCache + GeoResolver + AsnResolver + InfraClassifier + DomainIntelService + OriginSelector — cache first, or quota is exhausted in development
11. IocExtractor + StructuralFingerprinter + CampaignGraphService (F6, M5)
12. IndicatorHistoryIndex + FirstContactScorer (F4) — rides on the index F6 builds
13. CaseService + QueueUI + EmailDetailUI + the F1/F5/F7/F8 panels
14. ReportGenerator + CertificateTemplateService — renders every preceding output
15. TraceMapUI + GraphExplorerUI

**P2 — build last, state the limitation**
16. EvaluationRunner + CorpusManifest + EvaluationDashboardUI (F2, M12)
17. AlertService + SearchService + EndUserReportIntake + IocExporter + remaining M2 detectors
18. MaskingService + RetentionService + ResidencyGuard + remaining M8 surfaces

## Sprint Mapping
**Team:** 6 members. Source §16.4's allocation is extended to cover the four new modules —
(1) ingestion, parsing, header/auth, F5; (2) ML classifier, M12 evaluation; (3) tracer,
geolocation, enrichment, M9 URL and QR engine; (4) graph correlation, F6, F4; (5) frontend —
queue, detail, panels, map, graph, case view; (6) evidence ledger, F7, reporting, M10, M11.
Seniority is not stated in any source.
**Timeline:** relative — no calendar dates. The schedule is unbounded and scope-driven per the
consultant. Sprints are sequenced by dependency at a 2-week cadence; anchor them when a start
date exists.

| Sprint | Work | Owner |
|---|---|---|
| 1 | PostgreSQL schema, AuthService, LedgerService, EvidenceReferenceService, EvidenceStore | 6, 1 |
| 2 | MimeParser, IngestAPI, GmailConnector, Deduplicator ∥ MerkleRootService, VerifierTool (F7 complete) | 1 ∥ 6 |
| 3 | ReceivedChainParser, TrustBoundaryResolver, AuthValidator, AuthSemanticsTable (F5) ∥ UrlExtractor, RedirectExpander, QrDecoder (F3) ∥ admin lists | 1 ∥ 3 ∥ 6 |
| 4 | FeatureExtractor, ClassifierService ∥ DisplayDestinationComparator, TyposquatChecker, AttachmentAnalyzer ∥ QueueUI, EmailDetailUI scaffold, AuthSemanticsPanel | 2 ∥ 3 ∥ 5 |
| 5 | SignalNormalizer, WeightedScorer, ScoreExplanation (F8) ∥ ConflictRuleEngine, ConflictNarrator (F1) ∥ ScorePanel, ConflictPanel, LedgerPanel | 2, 6 ∥ 6 ∥ 5 |
| 6 | EnrichmentCache, GeoResolver, AsnResolver, InfraClassifier, DomainIntelService, OriginSelector ∥ IocExtractor, StructuralFingerprinter, CampaignGraphService (F6) ∥ CaseService, CaseUI | 3 ∥ 4 ∥ 5, 6 |
| 7 | IndicatorHistoryIndex, FirstContactScorer (F4) ∥ ReportGenerator, CertificateTemplateService ∥ TraceMapUI, GraphExplorerUI | 4 ∥ 6 ∥ 5 |
| 8 | EvaluationRunner, CorpusManifest, EvaluationDashboardUI (F2) ∥ remaining M2 detectors, multilingual, FeedbackQueue ∥ AlertService, SearchService, EndUserReportIntake, IocExporter | 2 ∥ 2 ∥ 3, 5 |
| 9 | MaskingService, RetentionService, ResidencyGuard, ExecutiveDashboardUI, remaining M8, ArcEvaluator, PassiveDnsClient, integration testing, demo seeding | all |

[STRAWMAN] — assumes full-time availability and parallel tracks from Sprint 3. The §16.4
allocation was written for a 36-hour build; scope has since roughly tripled, and no seniority
information exists to assign integration-heavy components deliberately.

## Effort Signals
| Feature | Size | Rationale |
|---|---|---|
| M1 — Ingestion & Normalisation | L | 6 components, three ingestion routes, write-once semantics, byte-offset addressing for evidence references |
| M2 — Detection Engine | L | 10 components; reduced from XL — URL, attachment and scoring work moved to M9 and M11. Still carries model training and the unresolved corpus question |
| M3 — Header & Protocol Analysis | L | 7 components, standards-heavy but precisely specified. F5 adds roughly a day of engineering plus a day of careful writing |
| M4 — Origin Traceability & Location | L | 8 components plus external enrichment under a quota constraint, now non-blocking |
| M5 — Investigation & Correlation Graph | XL [STRAWMAN] | 11 components. Structural fingerprinting is genuinely new work, and the graph plus history index plus explainable campaign scoring is the largest single build in the system |
| M6 — Alerting, Dashboard & Reporting | XL [STRAWMAN] | 14 components including six significant React surfaces, PDF generation and case management; every module surfaces here |
| M7 — Evidence Integrity Layer | L | 9 components; reduced from XL — v2's design removes the external anchoring integration entirely, and PostgreSQL enforces append-only rather than application code. Merkle tree is roughly forty lines |
| M8 — Administration | M | 7 components, thin CRUD over configuration |
| M9 — URL & Embedded Content Threat Engine | L | 8 components. QR decoding across three extraction surfaces with pre-processing is the bulk; the URL pipeline itself is well understood |
| M10 — Evidence Conflict Detector | M | 3 components, no external data, all inputs internal. Roughly a day for the engine, then ongoing rule-table work as modules complete |
| M11 — Explainable Threat Scoring | M | 4 components. An additive model with a fixed output contract; the discipline is in the guard rails, not the arithmetic |
| M12 — ML Evaluation & Model Validation | M | 3 components, admin-only, off the per-email path. The dashboard is small; the corpus question behind it is not |
| LedgerService + EvidenceReferenceService (shared) | M | Hash chain, role grants, trigger, constraint design — small surface, high correctness burden |
| EvidenceStore (shared) | M | MinIO object-lock plus byte-offset addressing discipline |
| AuthService (shared) | M | Five-role RBAC across every surface |
| TrustBoundaryResolver (shared) | M | Small surface, disproportionate correctness burden — M4's entire output depends on it |
| EnrichmentCache (shared) | S | TTL cache over Redis |

Two XL modules, down from four in the previous revision. That reduction is real and comes from
v2's design choices, not from optimism: M7 lost its external-anchoring integration and gained
database-enforced integrity, and M2 shed three responsibilities to M9 and M11. Scope grew by
four modules while total effort stayed close to flat.

All twelve are sized for a full build. The consultant directed on 2026-08-31 that resourcing is
not a planning constraint, so nothing here is trimmed to fit a team size, and ESTIMATOR should
size the full set without proposing cuts.

## Open Questions
1. What replaces the institution-donated training data? — public corpora reintroduce era-and-encoding bias, and no non-English corpus has been identified for the multilingual requirement — blocks: ClassifierService, M12's reported figures, any accuracy claim
2. What are the success metrics for this build? — M12 measures and discloses but commits to no target — blocks: acceptance of every module
4. Which QR decoder, given the licence question? — ZBar is LGPL, PyMuPDF is AGPL; distribution or open-sourcing changes the answer — blocks: QrDecoder, and any release of the prototype
5. Is a mail platform account with API access provisioned? — blocks: GmailConnector, the primary ingestion route
6. What is the minimum history volume before the F4 first-contact signal is trusted rather than suppressed? — 1,000 messages proposed — blocks: FirstContactScorer's suppression threshold
7. Who authors the F5 semantics prose? — the most user-visible text in the product; it must be technically exact and needs one named owner — blocks: AuthSemanticsTable
8. Does the F8 conflict adjustment need its own calibration set? — blocks: WeightedScorer's conflict weights
9. What is the retention rule for the F6 graph and the F4 indicator index? — indicator history is most useful when kept longest and most sensitive when kept at all — blocks: RetentionService policy for those two stores
10. Are the public corpora licensed for training use and redistribution in a demo? — blocks: M12's evaluation run and any published artifact

Resolved since the previous revision:
- *Is zero-cost tamper-evident anchoring viable?* — yes. Hash-chained ledger plus exported Merkle root, no external service.
- *Does application-enforced audit chaining meet the evidentiary bar?* — moot. PostgreSQL enforces it.
- *How is enrichment reconciled with the free-tier quota?* — downgraded from HIGH to MED. F4 and F6 function with zero feed calls, so the quota constrains an enhancement rather than the core path.
- *Is full scope deliverable by this team?* — closed by decision, not by analysis. The consultant directed that the whole scope be built and that resourcing is not a constraint to plan against. Recorded as a decision because no sizing analysis informed it — ESTIMATOR had not run at the time it was made.

## STRAWMAN Summary
All tentative decisions — challenge these before dev sprint 1:
- [STRAWMAN] QR decoder selection — licence unresolved between an LGPL symbol reader and an AGPL rasteriser; matters on distribution
- [STRAWMAN] Public corpora as the sole training source — licence and representativeness both unconfirmed
- [STRAWMAN] Team allocation extended from source §16.4 — that allocation covered six modules for a 36-hour build; it now covers twelve, and seniority is unstated
- [STRAWMAN] Relative sprint numbering — no calendar anchor exists; schedule stated as unbounded
- [STRAWMAN] M5 and M6 sized XL — auto-applied per skill rule
- [STRAWMAN] Mail platform integration — test account unconfirmed
- [STRAWMAN] Graph on PostgreSQL recursive CTEs — v2 names this the safe default at prototype scale; would change if traversal performance fails at demonstration size
- [STRAWMAN] F8 weight ceilings — taken from v2 §5.8 as authored; not calibrated against any labelled set

## Confidence Notes
- Database: this revision reverses the MongoDB decision recorded earlier on 2026-08-31. The reversal is not preference — v2's F7 requires INSERT-only role grants, revoked UPDATE and DELETE, and a NOT NULL evidence-reference constraint. MongoDB provides none of these. The consultant confirmed the switch.
- Evidence integrity: HIGH — this is now the strongest part of the design. Every finding is bound by constraint to a byte range in a write-once original; the ledger is database-enforced append-only; the verifier runs standalone. The tamper-evidence claim is defensible without qualification, which was not true of the previous revision.
- Timeline: WARN — no calendar dates anywhere. Sprint mapping is a dependency sequence, not a schedule. ESTIMATOR will report "start date not found" and ask.
- Budget: the zero-budget constraint eliminated every cloud option before selection began, and v2's design removed the last remaining external-service dependency from the critical path. Nothing in this architecture requires an account that costs money.
- Success metrics: LOW — no agreed target, carried unresolved through four skills. M12 improves the honesty of measurement without supplying a target.
- Scope: twelve modules against six people with no end date. Effort did not grow proportionally — see the note under Effort Signals. The consultant has directed that the full scope be built with resourcing excluded as a planning constraint, so deliverability is settled by decision rather than by analysis.
- Provenance: revised from the 8-module version after the consultant supplied Architecture Update v2 and chose PostgreSQL. mvp-scope.md was rebuilt in the same pass and the two are consistent as of this revision.
- Source agreement: no contradiction was found between mvp-scope.md and the decisions recorded here.

## Source Artifacts
- mvp-scope.md — DrishtiMail Forensics MVP scope, rebuilt 2026-08-31: 12 features at full breadth, 5 key journeys, P0/P1/P2 build priority, PostgreSQL recorded as the tech constraint, 10 open questions.
- drishtimail_architecture_v2 (2).pdf — Architecture Update v2, 2026-08-29: 8 features integrated into 12 modules, per-feature verification status, build priority, demonstration workflow, and effect on prior open questions.
