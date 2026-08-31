# Discovery — DrishtiMail Forensics
# Generated: 2026-08-29 | Updated: 2026-08-29 (consultant Q&A) | Reviewed by: Ashutosh Garg

## Project Context
An institutional email security platform for the Smart India Hackathon problem statement
SIH26106 (AICTE — Cyber Security Cell, theme: Blockchain & Cybersecurity). Institutions can
already block malicious email but cannot explain, trace, or evidence it: when a spoofed
invoice or credential-harvesting mail lands, the security team can quarantine it but cannot
answer where it came from, which infrastructure sent it, whether it matches a prior incident,
or hand a defensible record to law enforcement. The platform is positioned as detection plus
forensics plus attribution-support — explicitly not another spam filter.

## Users
**Primary:** SOC / security analysts (persona handles 60–100 flagged mails/day, needs a verdict
in under 30 s) and cyber forensic investigators (deep-dive escalations, need relay
reconstruction and defensible evidence). Mail administrators are a third primary — they deploy
it and require no mail-flow breakage.
**Secondary:** Institutional head / registrar (sponsor), end users (staff, faculty, students),
law enforcement / cybercrime cell (report consumers), legal / DPO / compliance, CERT-In as
nodal agency. Scale is institution-sized; no user count is given.

## Core Problem
Four capability gaps are named: semantic (no understanding of intent independent of keywords),
forensic (headers stored but not reconstructed into a trust-boundary-aware relay path),
attribution (each email treated as an isolated event, no campaign clustering), and evidentiary
(no chain of custody, so findings cannot support disciplinary or legal proceedings). The
business cost is direct BEC/payment-diversion loss, credential compromise, domain-impersonation
reputational damage, stalled investigations, and repeat victimisation by unrecognised campaigns.

## Features Mentioned
- Ingestion and Normalisation — `.eml`/`.msg` upload, pasted headers, IMAP/Graph/Gmail, journaling feed; MIME parse, SHA-256 at ingest, immutable WORM original [HIGH]
- Fraudulent Email Detection Engine — six-class NLP/ML classification, 0–100 calibrated risk score, social-engineering and BEC sub-pattern detection, display-name spoofing, typosquat/homoglyph, URL and attachment analysis, ranked feature explainability, analyst feedback loop [HIGH]
- Header and Protocol Analysis — Received-chain parsing, trust-boundary logic, SPF/DKIM/DMARC/ARC validation with alignment, header-anomaly and relay-characteristic detection, per-hop table [HIGH]
- Origin Traceability and Location Analysis — candidate IP extraction, earliest-reliable-IP selection with justification, geo/ASN/ISP resolution, infrastructure-type classification, mandatory confidence bands, interactive trace map, WHOIS/RDAP domain intelligence, enrichment caching [HIGH]
- Identity Correlation and Attribution Support — IOC extraction, threat-intel correlation, property graph, campaign clustering, origin-scenario classification, confidence-scored investigative leads, STIX 2.1 / MISP export, graph explorer [HIGH]
- Alerting, Dashboard and Reporting — real-time alerts, analyst queue and email detail view, executive dashboard, PDF forensic report with evidence-integrity page, BSA §63 certificate template, case management, full-text/IOC search [HIGH]
- Privacy, Legal, Compliance and Evidence Integrity — RBAC (5 roles), append-only audit log, PII masking with audited reveal, retention and purge policy, chain of custody, Merkle-root anchoring to a permissioned ledger, independent verification tool, legal hold [HIGH]
- Administration — protected-brand/VIP list, trusted internal MTA list driving the trust boundary, allow/blocklists, scoring-weight and threshold configuration, model registry [HIGH]

Granularity note: the source specifies roughly 80 individual requirements (FR-1.1 … FR-8.5)
grouped into these eight modules. Features are recorded at module level; the FR-level detail
stays in the source doc and is not restated here. Each module carries its own M/S/C/W priority
markers in the source, which MVP_SYNTHESIZER should read directly.

## Constraints
- Timeline: **no fixed deadline — scope-driven, not time-boxed** (consultant, 2026-08-29).
  The target is the full project MVP; the consultant has explicitly stated there is no time
  constraint. The source's 36-hour / 6-member figure (C-4) and its §16 MVP cut therefore
  describe a narrower, time-boxed build that this engagement supersedes. This is an unbounded
  window by decision, not a missing value — scope is the fixed side of the trade, schedule is
  the free side.
- Budget: **none — student team.** Free-tier and open-source services only; no paid or
  subscription services may be assumed anywhere in the design (consultant, 2026-08-29).
  This is a hard constraint, not a preference.
- Tech: the source names a full recommended stack — Python 3.11 + FastAPI, React + TypeScript
  with Tailwind/Leaflet/Cytoscape.js/Recharts, PostgreSQL, Neo4j, OpenSearch, Redis + Celery,
  MinIO with object-lock, Hyperledger Fabric (or an Ethereum testnet for demo), DistilBERT +
  XGBoost + SHAP, MaxMind GeoLite2, Docker Compose → Kubernetes. Recorded as stated in the
  document, not as a decision taken here — ARCH_PROPOSER owns that call, and must now re-test
  every item against the zero-budget constraint above (several have free tiers or community
  editions; that needs verifying per component, not assuming).
- Ingestion: **Google Workspace / Gmail, via the Gmail API** (consultant, 2026-08-29). This
  promotes source FR-1.3, which was priority S, into the primary ingestion path. Exchange,
  M365 and on-prem Postfix are not targets for this engagement.
- Mail-flow mode: **out-of-band journaling only** — the system analyses a copy and performs no
  real-time blocking (consultant, 2026-08-29). Inline blocking is explicitly deferred to a
  future phase, conditional on the system first being proven and trusted in the mail path.
  Consistent with source C-3.
- Retention: headers **1 year**, bodies **90 days**, both configurable by the institution
  (consultant, 2026-08-29). Both exceed the CERT-In 180-day floor for headers; the 90-day body
  period is a deliberate data-minimisation choice.
- Threat intel: **free tiers only** — VirusTotal public API (4 requests/min), URLhaus (free,
  no key), PhishTank (free). Plus manual threat-data import via Excel/CSV upload, which is a
  new capability not present in the source's requirement set (consultant, 2026-08-29).
- Training data: **no institutional mail will be donated** — real student and staff mail cannot
  be shared for privacy reasons (consultant, 2026-08-29). Fine-tuning relies entirely on public
  corpora: Nazario phishing corpus, Enron, Kaggle phishing datasets. This voids source
  assumption A-4 and the stated mitigation for risk R-5 — see Open Questions.
- Ledger: **single institution, one node/authority** for the MVP (consultant, 2026-08-29).
  A multi-institution consortium is possible future work if other colleges join.
- Forensic examiner: **none assigned** — not applicable at hackathon/pilot stage (consultant,
  2026-08-29). The system must still emit evidence in a form ready for later certified review
  (hash-verified, tamper-evident logs). Formal admissibility in a real deployment would require
  a CERT-In empanelled forensic examiner. This makes source FR-6.8 (BSA §63 certificate
  template) a forward-compatibility requirement rather than an immediately exercised one.
- SIEM/SOAR: **none at the institution.** The project builds its own lightweight dashboard;
  optional future integration with open-source Wazuh or the ELK stack (consultant, 2026-08-29).
- Other:
  - Data residency — logs and evidence stored within Indian jurisdiction (CERT-In direction, C-1).
  - Enrichment API rate limits require caching and queueing (C-2) — now sharply tighter than
    the source assumed, given the free-tier quotas above.
  - Compliance surface: DPDP Act 2023, CERT-In 2022 directions (6-hour reporting, 180-day log
    retention), BSA 2023 §63 admissibility certificate, IT Act 2000 §43A/§72A, GDPR where EU
    subjects are involved.
  - Stated ethical boundaries, treated as hard scope limits: no deanonymisation of individuals
    (infrastructure attribution only), no offensive action or active probing, no attachment
    detonation in MVP, not a replacement MTA.
  - Geolocation is probabilistic, not evidentiary — every location output must carry an
    explicit confidence band and caveat.
  - Only hashes go to the ledger — never message content, never PII.
  - Performance floor: p95 ≤ 3 s local / ≤ 8 s with enrichment, ≥ 10,000 emails/hour per node,
    99.5% availability, WCAG 2.1 AA.

## Open Questions

All 11 questions carried from the source and from the first pass were answered by the
consultant on 2026-08-29 and are now recorded under Constraints. The client name was confirmed
as "Smart India Hackathon", and the timeline was settled as scope-driven with no fixed
deadline. Two new questions arise from those answers:

1. How is enrichment reconciled with the VirusTotal free-tier quota? — 4 requests/min is
   roughly 5,760/day, against source NFR-2's target of ≥10,000 emails/hour. Per-email live
   enrichment is arithmetically impossible on the free tier. Needs a deliberate decision
   (aggressive caching, sampling, queue-and-defer, local-only verdict with enrichment as
   best-effort, or a revised throughput target). Source risk R-4 anticipated rate limits but
   not a gap of this size.
2. What replaces the institution-donated training data? — source assumption A-4 and the
   mitigation for risk R-5 ("training data does not reflect Indian institutional mail",
   rated High impact) both depended on donated samples, now ruled out for privacy reasons.
   Public corpora alone reintroduce exactly the era-and-encoding bias the source warns about
   in §12.1. R-5 is currently unmitigated.

## Confidence Notes
- Confidence basis: two sources — one written document, plus a consultant Q&A on 2026-08-29
  that answered all 11 outstanding questions. The Extraction Pass definition of MED ("stated
  in only one doc") would flatten every document-derived item to MED and misrepresent a source
  this explicit, so confidence here grades how specifically and unambiguously a thing is
  stated, not cross-document corroboration. Consultant-stated answers are HIGH.
- Timeline: MED — the consultant stated directly that there is no time constraint and the
  target is the full MVP, so the absence of a date is a decision rather than a gap. It remains
  MED rather than HIGH because an unbounded schedule cannot be planned against: any downstream
  sprint plan or estimate will have to assume a window, and that assumption will be the
  planner's, not the client's.
- Budget: HIGH — consultant stated zero budget, free-tier and open-source only.
- Tech: recorded as a source-stated recommendation, not a confirmed decision. The document
  supplies a full stack and a logical architecture (§11, §12); neither was selected here, and
  ARCH_PROPOSER should treat both as input rather than as settled. The zero-budget constraint
  arrived after the document was written, so the stack has not been validated against it.
- Source assumptions now void: A-4 (institution-donated training samples) is contradicted by
  the consultant's answer on privacy; risk R-5's mitigation depended on it and no longer holds.
  Anything downstream that relies on §12.1's data plan should re-derive it rather than inherit it.
- MVP scope: the source proposes its own MVP cut in §16, sized for 36 hours. The consultant has
  since ruled that cut out as too narrow, so §16 is no longer a candidate scope — it is a record
  of what a much shorter build would have contained. MVP_SYNTHESIZER owns the actual cut.
- Priority markers stale: the source's M/S/C/W ratings were assigned against the 36-hour build.
  With scope widened to the full MVP, those ratings should be treated as indicative, not binding.
- Users: no headcount is given for any role beyond the persona's 60–100 mails/day workload.
- Source agreement: the document and the consultant's answers do not contradict each other on
  any point. Where the answers add detail, narrow an option, or void an assumption, they are
  both newer and directly given, so they take precedence over the document.

## Source Docs
- SIH26106_Business_Analysis.md — complete Business Analysis Document v1.0 (~5,885 words, 20
  sections): executive summary, gap analysis, stakeholder register and three personas, business
  goals with six measurable objectives, in/out scope, assumptions-constraints-dependencies,
  ~80 functional requirements across 8 modules with MoSCoW priorities, 14 non-functional
  requirements, 8 user stories with acceptance criteria, process flows, logical architecture,
  recommended stack and ML approach, data requirements, legal/privacy framework, 11-item risk
  register, hackathon MVP cut with demo narrative and team allocation, success metrics, roadmap,
  open questions, traceability matrix.
- Consultant Q&A, 2026-08-29 — Ashutosh Garg answered all 11 open questions in writing during
  this session. Established the zero-budget/free-tier constraint, Gmail API as the ingestion
  path, retention periods, the free-tier threat-intel set plus CSV import, single-institution
  ledger, absence of a certified examiner and of any existing SIEM, and the unavailability of
  institutional training data. Being newer and directly given, these take precedence over the
  document wherever the two differ.
- Naming note: the engagement is named DrishtiMail Forensics; the source document uses
  *MailTrace* as a placeholder working product name. Same project, two names.
