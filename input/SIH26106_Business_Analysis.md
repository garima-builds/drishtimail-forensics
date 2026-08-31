# SIH26106 — AI-Powered Email Threat Detection, GeoLocation and Forensic Intelligence Platform
### Business Analysis Document (BAD) v1.0

| Field | Value |
|---|---|
| Problem Statement ID | SIH26106 |
| Organization | AICTE — Cyber Security Cell |
| Category | Software |
| Theme | Blockchain & Cybersecurity |
| Document Owner | Business Analyst |
| Status | Draft for team review |
| Working Product Name | *MailTrace* (placeholder) |

---

## 1. Executive Summary

Institutions today can **block** bad email reasonably well. What they cannot do is **explain** it. When a spoofed invoice reaches a finance officer or a credential-harvesting mail impersonates a Registrar, the security team can quarantine the message — but they cannot quickly answer the questions that actually matter to an investigation: *Where did this come from? Which infrastructure sent it? Is this the same actor as last month? Can we hand this to law enforcement in an admissible form?*

This platform closes that gap. It is not another spam filter. It is a **detection + forensics + attribution-support** system that takes a raw email, decides how dangerous it is, reconstructs how it travelled, estimates where it started, links it to previous incidents, and produces a tamper-evident forensic report that an analyst, a legal reviewer, or a cybercrime cell can actually use.

**One-line pitch:** *Detect the fraud, then trace it — and produce evidence that holds up.*

---

## 2. Problem Context and Gap Analysis

### 2.1 Why existing controls fall short

| Existing Control | What it does | Where it fails for SIH26106 |
|---|---|---|
| Spam filters (Bayesian/reputation) | Bulk-mail scoring | Blind to low-volume, targeted BEC with clean reputation |
| Static blacklists | Blocks known-bad IPs/domains | Attackers rotate domains in hours; zero-day domains pass |
| Rule/signature engines | Pattern matching | AI-generated text defeats phrasing rules |
| SPF/DKIM/DMARC | Sender authentication | Widely mis-deployed (`p=none`); an attacker's own domain can pass all three |
| SIEM | Log aggregation | Stores headers but does not *interpret* relay chains or attribute them |
| Manual header analysis | Accurate | Slow, expert-dependent, non-repeatable, non-scalable |

### 2.2 The four capability gaps we are solving

1. **Semantic gap** — no understanding of *intent* (urgency, authority pressure, payment diversion) independent of keywords.
2. **Forensic gap** — headers are stored but not reconstructed into a validated, trust-boundary-aware relay path.
3. **Attribution gap** — each email is treated as an isolated event; no campaign-level clustering across incidents.
4. **Evidentiary gap** — no chain of custody, so findings cannot be relied upon in disciplinary or legal proceedings.

### 2.3 Business impact of the gap
- Direct financial loss via BEC/payment diversion.
- Credential compromise leading to lateral account takeover.
- Reputational damage from domain impersonation of the institution.
- Investigations that stall because evidence quality is inadequate.
- Repeat victimisation by the same campaign, unrecognised as a repeat.

---

## 3. Stakeholders and Personas

### 3.1 Stakeholder register

| Stakeholder | Interest | Influence | Key need |
|---|---|---|---|
| SOC / Security Analyst | Primary daily user | High | Fast triage, low false positives, explainable verdicts |
| Cyber Forensic Investigator | Deep-dive user | High | Relay reconstruction, geolocation, defensible evidence |
| IT / Mail Administrator | Deploys and integrates | High | Easy integration, low latency, no mail-flow breakage |
| Institutional Head / Registrar | Sponsor, risk owner | High | Reduced incidents, reportable metrics |
| End User (staff, faculty, student) | Protected party | Low | Clear warnings, easy reporting of suspicious mail |
| Law Enforcement / Cybercrime Cell | Consumer of reports | Medium | Admissible, structured, complete forensic reports |
| Legal / DPO / Compliance | Governance | Medium | Privacy-safe handling, retention control, auditability |
| CERT-In / Nodal Agency | Regulatory reporting | Medium | Timely incident reporting, log retention compliance |

### 3.2 Primary personas

**Ananya — SOC Analyst, University Cyber Cell**
Handles 60–100 flagged mails/day. Needs verdict + reason in under 30 seconds. Pain: current tools say "suspicious" with no *why*, so she re-reads headers manually.
*Success looks like:* one screen with score, top-5 contributing signals, and a one-click escalate.

**Rajeev — Cyber Forensic Investigator**
Gets escalations after a ₹12 lakh payment diversion. Needs the earliest trustworthy hop, ASN/ISP, hosting provider, domain registration age, and links to earlier cases. Pain: manually pastes headers into five different web tools.
*Success looks like:* one export that a cybercrime cell accepts without follow-up questions.

**Suresh — Mail Administrator**
Cares that nothing breaks. Pain: security tools that add seconds to delivery or quarantine the Vice-Chancellor's mail.
*Success looks like:* out-of-band journaling mode, sub-second analysis, no mail-flow risk.

---

## 4. Goals and Objectives

### 4.1 Business goals
- **BG-1** Reduce successful phishing/BEC incidents at the institution.
- **BG-2** Cut the time from "suspicious email reported" to "investigation-ready report".
- **BG-3** Enable campaign-level recognition instead of one-off firefighting.
- **BG-4** Produce evidence that survives legal and audit scrutiny.

### 4.2 Product objectives (measurable)

| ID | Objective | Target |
|---|---|---|
| OBJ-1 | Classification accuracy on held-out phishing corpus | ≥ 95% F1 |
| OBJ-2 | False positive rate on legitimate business mail | ≤ 2% |
| OBJ-3 | End-to-end analysis latency per email | ≤ 3 s (p95), ≤ 8 s with external enrichment |
| OBJ-4 | Time to generate forensic report | ≤ 60 s from analyst request |
| OBJ-5 | Relay path reconstruction where headers permit | ≥ 90% of emails |
| OBJ-6 | Campaign clustering recall on seeded test campaigns | ≥ 85% |

---

## 5. Scope

### 5.1 In scope (MVP + full product)
- Ingestion of `.eml`/`.msg`, IMAP/Graph/Gmail API, and journaling feed.
- NLP + ML classification into: **Legitimate / Suspicious / Phishing / Impersonation / BEC-Fraud / Malware-bearing**.
- Full header forensics: Received chain, Return-Path, Message-ID, Reply-To, Authentication-Results, ARC.
- SPF / DKIM / DMARC / ARC / reverse-DNS validation and alignment checking.
- URL extraction, redirect-chain resolution, shortener expansion, homoglyph/typosquat detection.
- Attachment static analysis (hash, type mismatch, macro/OLE and PDF-JS indicators). **No detonation in MVP.**
- Originating-IP extraction with trust-boundary logic; IP geolocation, ASN, ISP, hosting/VPN/TOR/proxy classification.
- Domain intelligence: WHOIS/RDAP, domain age, registrar, nameservers, MX, passive DNS.
- Threat-intel correlation and IOC extraction (STIX 2.1 export).
- Graph-based correlation and campaign clustering.
- Analyst dashboard, geo trace map, alerting, case management.
- Forensic report (PDF) with hash-based chain of custody and ledger anchoring.
- RBAC, audit logging, retention and masking policies.

### 5.2 Out of scope
- Acting as the primary MTA or replacing the institution's mail gateway.
- Full dynamic malware sandbox / detonation chamber (integration hook only).
- Endpoint (EDR) telemetry, network packet capture.
- Offensive actions: takedown, hack-back, active probing of attacker infrastructure.
- **Deanonymising individuals.** The system supports *infrastructure* attribution and produces confidence-scored investigative leads. It does not claim to identify a named person, and the UI must never present it that way.
- Encrypted-body decryption (S/MIME, PGP) without the institution's own keys.

### 5.3 Scope boundary note — an honest constraint to state in the pitch
IP geolocation is **probabilistic, not evidentiary**. City-level accuracy is unreliable; country-level is generally sound. Cloud, VPN, TOR, and relay-hosted senders resolve to *infrastructure* location, not actor location. Every geolocation output must carry an explicit confidence band and this caveat. Judges reward teams that state this; they penalise teams that claim to "find the hacker's house."

---

## 6. Assumptions, Constraints, Dependencies

**Assumptions**
- A-1 The institution can provide journaling/BCC access or mailbox API credentials.
- A-2 Raw RFC 5322 headers are preserved end-to-end (not stripped by an upstream gateway).
- A-3 Outbound access to enrichment APIs is permitted, or an offline DB is provisioned.
- A-4 Labelled training data is obtainable from public corpora plus institution-donated samples.

**Constraints**
- C-1 Data residency: logs and evidence stored within Indian jurisdiction (CERT-In direction).
- C-2 Enrichment API rate limits (VirusTotal, WHOIS) require caching and queueing.
- C-3 Analysis must not delay mail delivery — default to out-of-band mode.
- C-4 Hackathon constraint: buildable and demoable within 36 hours by 6 members.

**Dependencies**
- D-1 Geolocation DB (MaxMind GeoLite2 / IP2Location LITE) — licence terms respected.
- D-2 Threat-intel feeds: AbuseIPDB, VirusTotal, PhishTank, OpenPhish, URLhaus, Spamhaus.
- D-3 RDAP/WHOIS availability; note GDPR redaction of registrant fields.
- D-4 Pretrained transformer weights (DistilBERT/RoBERTa) available offline for demo.

---

## 7. Functional Requirements

Priority: **M** = Must (MVP), **S** = Should, **C** = Could, **W** = Won't (this release)

### 7.1 Module 1 — Ingestion and Normalisation

| ID | Requirement | Pri |
|---|---|---|
| FR-1.1 | Accept `.eml` and `.msg` upload (single and bulk ZIP) via web UI | M |
| FR-1.2 | Accept raw pasted headers for quick analysis | M |
| FR-1.3 | Poll mailbox via IMAP; connect via Microsoft Graph / Gmail API | S |
| FR-1.4 | Consume journaling/BCC stream for near-real-time institutional coverage | S |
| FR-1.5 | Parse MIME tree; extract headers, bodies (text/HTML), attachments, inline objects | M |
| FR-1.6 | Compute SHA-256 of raw message at ingest, before any transformation | M |
| FR-1.7 | Store raw original immutably (WORM/object-lock); all analysis works on copies | M |
| FR-1.8 | Handle malformed/non-compliant MIME without crashing; flag as anomaly | M |
| FR-1.9 | Deduplicate by Message-ID + body hash | S |
| FR-1.10 | REST API endpoint `POST /analyze` for third-party integration | S |

### 7.2 Module 2 — Fraudulent Email Detection Engine (NLP/ML)

| ID | Requirement | Pri |
|---|---|---|
| FR-2.1 | Classify each email into: Legitimate, Suspicious, Phishing, Impersonation, BEC-Fraud, Malware-bearing | M |
| FR-2.2 | Output a calibrated fraud risk score 0–100 with confidence band | M |
| FR-2.3 | Detect social-engineering cues: urgency, authority pressure, secrecy, financial instruction, threat of consequence | M |
| FR-2.4 | Detect BEC sub-patterns: payment/bank-detail change, fake invoice, gift-card request, payroll diversion, credential harvest, executive impersonation | M |
| FR-2.5 | Detect display-name spoofing (display name matches a known internal VIP, envelope domain does not) | M |
| FR-2.6 | Detect lookalike/typosquat domains: homoglyph, IDN/punycode, Levenshtein ≤ 2 vs. protected domain list, TLD swap | M |
| FR-2.7 | Extract and analyse URLs: shortener expansion, redirect chain, mismatch between anchor text and href, credential-form landing pages, IP-literal URLs, `@`-obfuscation, excessive subdomains | M |
| FR-2.8 | Static attachment analysis: true type vs. extension mismatch, double extension, hash reputation, macro/OLE presence, PDF embedded JS/OpenAction, archive-in-archive | S |
| FR-2.9 | Detect HTML tricks: hidden text, zero-width chars, invisible fonts, tracking pixels, text-as-image body | S |
| FR-2.10 | Detect thread hijacking (`Re:`/`Fwd:` on a thread with no prior legitimate history) | C |
| FR-2.11 | **Explainability**: return ranked contributing features with weights for every verdict | M |
| FR-2.12 | Analyst feedback loop: mark verdict correct/incorrect; feed retraining queue | S |
| FR-2.13 | Multilingual body analysis (English + at least one Indian language) | C |

### 7.3 Module 3 — Header and Protocol Analysis

| ID | Requirement | Pri |
|---|---|---|
| FR-3.1 | Parse full `Received:` chain in correct order (bottom = earliest hop) | M |
| FR-3.2 | Apply **trust-boundary logic**: walk down from the institution's own trusted MTAs; the first hop below the boundary is the earliest *reliable* node. Everything below it is attacker-controllable and must be labelled "unverified" | M |
| FR-3.3 | Validate SPF (RFC 7208) including alignment with `From` domain | M |
| FR-3.4 | Validate DKIM signature(s) (RFC 6376): presence, selector, key retrieval, d= alignment | M |
| FR-3.5 | Evaluate DMARC (RFC 7489) policy, alignment mode, and pass/fail outcome | M |
| FR-3.6 | Parse existing `Authentication-Results` and cross-check against own computation; flag disagreement | S |
| FR-3.7 | Evaluate ARC chain (RFC 8617) for forwarded/mailing-list mail to avoid false positives | C |
| FR-3.8 | Detect header anomalies: `From` vs `Return-Path` mismatch, `Reply-To` pointing to unrelated domain, malformed/duplicated Message-ID, Message-ID domain ≠ sender domain, timestamp regression or impossible hop delays, missing/forged hostnames, non-standard `X-Mailer` | M |
| FR-3.9 | Detect suspicious relay characteristics: open relay, residential IP as originator, mismatched reverse DNS, hop count anomalies | S |
| FR-3.10 | Produce a per-hop table: hop #, timestamp, claimed host, real IP, rDNS, TLS used, delay, trust status | M |

### 7.4 Module 4 — Origin Traceability and Location Analysis

| ID | Requirement | Pri |
|---|---|---|
| FR-4.1 | Extract all candidate originating IPs (Received chain, `X-Originating-IP`, `X-Sender-IP`) | M |
| FR-4.2 | Select the earliest **reliable** originating IP per FR-3.2, with justification text | M |
| FR-4.3 | Resolve IP → country, region, city, lat/long, accuracy radius | M |
| FR-4.4 | Resolve IP → ASN, ISP/organisation, network range | M |
| FR-4.5 | Classify IP infrastructure type: residential, business, datacenter/cloud, VPN, proxy, TOR exit, known open relay, botnet/bulletproof host | M |
| FR-4.6 | Attach **explicit confidence level** (High/Medium/Low) and the geolocation caveat to every location output | M |
| FR-4.7 | Render hop-by-hop trace on an interactive world map with polylines | M |
| FR-4.8 | Domain intelligence: WHOIS/RDAP registrar, creation/expiry date, domain age in days, registrant country (where not redacted), nameservers, MX, A/AAAA, SOA, TXT | M |
| FR-4.9 | Flag high-risk domain traits: age < 30 days, privacy-protected registration, free/abused TLD, recently changed NS, no MX, parked page | M |
| FR-4.10 | Passive DNS / historical resolution lookup | C |
| FR-4.11 | Cache all enrichment results with TTL to respect API rate limits | M |

### 7.5 Module 5 — Identity Correlation and Attribution Support

| ID | Requirement | Pri |
|---|---|---|
| FR-5.1 | Extract IOCs: sender addresses, domains, IPs, URLs, file hashes, Message-ID patterns | M |
| FR-5.2 | Correlate IOCs against threat-intel feeds and internal historical incidents | M |
| FR-5.3 | Build a property graph: `Email → Sender → Domain → IP → ASN → URL → Hash → Campaign` | M |
| FR-5.4 | Cluster related emails into campaigns using shared infrastructure, template similarity (MinHash/SimHash on body), and timing | S |
| FR-5.5 | Run community detection (e.g. Louvain) to surface infrastructure clusters | C |
| FR-5.6 | Classify the *origin scenario* with confidence: (a) spoofed domain, (b) compromised legitimate account, (c) lookalike domain registered by actor, (d) anonymised infrastructure (VPN/TOR), (e) bulk mail service abuse, (f) direct actor-controlled server | M |
| FR-5.7 | Produce an attribution summary as a **confidence-scored investigative lead**, never as an identity assertion | M |
| FR-5.8 | Export IOCs in STIX 2.1 / MISP-compatible JSON and plain CSV | S |
| FR-5.9 | Interactive graph explorer with pivot-on-node | S |

### 7.6 Module 6 — Alerting, Dashboard, Reporting

| ID | Requirement | Pri |
|---|---|---|
| FR-6.1 | Real-time alert on high-risk verdict, before user interaction where journaling permits | M |
| FR-6.2 | Configurable alert channels: dashboard, email, webhook, Slack/Teams; configurable score thresholds | S |
| FR-6.3 | Analyst dashboard: queue, filters (score, verdict, date, sender, campaign), sort, bulk action | M |
| FR-6.4 | Email detail view: verdict + score, top contributing signals, auth results panel, hop table, geo map, domain intel panel, URL/attachment panel, linked cases | M |
| FR-6.5 | Executive dashboard: volume trends, verdict distribution, top targeted departments, top spoofed brands, campaign timeline | S |
| FR-6.6 | Generate structured forensic report (PDF) containing: case ID, evidence hashes, ingestion timestamp, full header dump, analysis findings, relay table, geolocation with caveats, domain intel, IOC list, attribution assessment with confidence, examiner and tool version, chain-of-custody log | M |
| FR-6.7 | Include an evidence-integrity page: SHA-256 of original message, report hash, ledger anchor reference | M |
| FR-6.8 | Include a **Section 63 BSA / Section 65B IEA style certificate template** for electronic-record admissibility | S |
| FR-6.9 | Case management: create case, attach multiple emails, assign owner, status workflow (New → Triage → Investigating → Escalated → Closed), notes, timeline | M |
| FR-6.10 | Full-text and IOC search across all historical emails and cases | S |
| FR-6.11 | End-user "Report Phishing" intake path feeding directly into the queue | C |

### 7.7 Module 7 — Privacy, Legal, Compliance, Evidence Integrity

| ID | Requirement | Pri |
|---|---|---|
| FR-7.1 | Role-based access control: Viewer, Analyst, Investigator, Admin, Auditor | M |
| FR-7.2 | Immutable, append-only audit log of every view, export, and modification (who, what, when) | M |
| FR-7.3 | Configurable PII masking in the UI (recipient names, body content) with explicit "reveal" action that is itself audited | S |
| FR-7.4 | Configurable retention policy per data class; automated purge with purge log | S |
| FR-7.5 | Chain of custody: hash at ingest, hash on every export, custody transfer log | M |
| FR-7.6 | **Blockchain evidence anchoring** — periodically anchor a Merkle root of evidence hashes to a permissioned ledger (Hyperledger Fabric) so any post-hoc alteration is detectable by an independent party | M (theme fit) |
| FR-7.7 | Verification tool: given a report or `.eml`, recompute hash and verify against the ledger anchor | M |
| FR-7.8 | Data residency enforcement; 180-day minimum log retention (CERT-In) | S |
| FR-7.9 | Legal-hold flag preventing purge of an active case | C |

### 7.8 Module 8 — Administration

| ID | Requirement | Pri |
|---|---|---|
| FR-8.1 | Manage protected-brand/VIP list used for impersonation detection | M |
| FR-8.2 | Manage trusted internal MTA list (drives the trust boundary) | M |
| FR-8.3 | Allowlist/blocklist management with expiry | S |
| FR-8.4 | Configure scoring weights and verdict thresholds | S |
| FR-8.5 | Model registry: version, training date, metrics; rollback capability | C |

---

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Performance | p95 analysis latency ≤ 3 s (local analysis), ≤ 8 s with external enrichment |
| NFR-2 | Throughput | ≥ 10,000 emails/hour on a single node; horizontally scalable via queue workers |
| NFR-3 | Availability | 99.5% for the analysis service; degrade gracefully to local-only analysis if enrichment APIs are down |
| NFR-4 | Scalability | Stateless workers behind a message queue; independently scalable enrichment pool |
| NFR-5 | Security | TLS 1.3 in transit, AES-256 at rest, secrets in a vault, MFA for Investigator/Admin roles |
| NFR-6 | Isolation | Attachment parsing runs in a sandboxed, network-isolated container; never auto-fetch remote content from a suspicious email (no tracking-pixel callbacks) |
| NFR-7 | Usability | Analyst reaches a verdict decision in ≤ 30 s from opening an email; verdict reason visible without scrolling |
| NFR-8 | Explainability | No verdict is ever surfaced without contributing-feature attribution |
| NFR-9 | Auditability | 100% of privileged actions logged, tamper-evident |
| NFR-10 | Portability | Fully containerised; single `docker compose up` for on-prem deployment |
| NFR-11 | Reliability | Analysis failure on one email must not block the queue; failed items go to a dead-letter queue with reason |
| NFR-12 | Maintainability | Detection rules and weights configurable without redeployment |
| NFR-13 | Compliance | DPDP Act 2023 alignment; CERT-In log retention; evidence handling per BSA 2023 |
| NFR-14 | Accessibility | WCAG 2.1 AA for dashboard; map data also available in table form |

---

## 9. Key User Stories with Acceptance Criteria

**US-01 — Rapid triage**
*As a SOC analyst, I want a verdict with reasons the moment I open a flagged email, so that I can triage without manual header reading.*
**AC:** Given a flagged email, when I open the detail view, then I see a verdict label, a 0–100 score, and the top 5 contributing signals with weights, rendered within 2 s.

**US-02 — Trust-aware origin trace**
*As an investigator, I want the earliest reliable originating IP, so that I do not chase a forged hop.*
**AC:** Given an email with 6 Received hops of which 3 are below the configured trust boundary, when I open the trace, then the system marks hops 1–3 "unverified — attacker-controllable", identifies the earliest reliable node, and states the reasoning in plain language.

**US-03 — Honest geolocation**
*As an investigator, I want geolocation with explicit confidence, so that I do not overstate findings in a report.*
**AC:** Given an originating IP that resolves to a cloud datacenter, when geolocation runs, then the result shows infrastructure type = "Datacenter/Cloud", confidence = "Low for actor location", and the caveat text is included in the exported report.

**US-04 — Campaign recognition**
*As an analyst, I want related emails grouped, so that I recognise a repeat campaign.*
**AC:** Given 12 emails sharing an ASN and a body SimHash within threshold, when clustering runs, then all 12 appear under one campaign ID with the shared indicators listed.

**US-05 — Defensible report**
*As a compliance officer, I want a tamper-evident report, so that it can be relied on in proceedings.*
**AC:** Given a closed case, when I export the forensic report, then the PDF contains evidence hashes, chain-of-custody entries, tool version, and a ledger anchor reference that the verification tool confirms as matching.

**US-06 — Non-disruptive deployment**
*As a mail administrator, I want out-of-band analysis, so that mail delivery is never delayed.*
**AC:** Given journaling mode, when the platform is stopped, then mail flow continues unaffected and unanalysed messages queue for later processing.

**US-07 — Impersonation catch**
*As a finance officer, I want executive impersonation flagged, so that I do not act on a fake instruction.*
**AC:** Given a mail whose display name matches a VIP-list entry but whose envelope domain is external and unaligned, when analysed, then verdict = Impersonation with score ≥ 80 and a high-priority alert is raised.

**US-08 — Feedback loop**
*As an analyst, I want to correct a wrong verdict, so that the model improves.*
**AC:** Given a false positive, when I mark it "incorrect — legitimate" with a reason, then the item enters the retraining queue and the correction is visible in the audit log.

---

## 10. Process Flows

### 10.1 Core analysis pipeline

```
[Ingest]  .eml / IMAP / Graph / Journal
    ↓  hash + immutable store  (FR-1.6, FR-1.7)
[Parse]   MIME tree → headers, bodies, URLs, attachments
    ↓
    ├──► [Header & Auth Analysis]  SPF · DKIM · DMARC · ARC · anomalies
    ├──► [NLP/ML Classifier]       intent · BEC patterns · impersonation
    ├──► [URL Analyzer]            expand · redirect chain · homoglyph
    └──► [Attachment Analyzer]     type · hash · macro/JS indicators
    ↓
[Trace]   trust-boundary walk → earliest reliable IP
    ↓
[Enrich]  geo · ASN · infra type · WHOIS/RDAP · passive DNS · threat intel   (cached)
    ↓
[Score]   weighted fusion → verdict + confidence + feature attribution
    ↓
[Correlate] graph upsert → campaign clustering → origin-scenario classification
    ↓
[Act]     alert · dashboard · case · forensic report (+ ledger anchor)
```

### 10.2 Investigation workflow

```
Alert / Analyst report
   → Triage (verdict + top signals)
      → Low risk  → Close with note
      → High risk → Open Case
         → Attach related emails (campaign suggestions)
         → Deep trace + enrichment review
         → Attribution assessment (confidence-scored)
         → Generate forensic report → anchor hash
         → Escalate: institutional action / legal / CERT-In / cybercrime cell
         → Close with outcome
```

### 10.3 Chain of custody

```
Ingest → SHA-256(raw) → WORM store → every access logged
      → Merkle batch (hourly) → root anchored to permissioned ledger
      → Export → SHA-256(report) → custody entry
      → Verify: recompute hash → compare to anchored root → PASS / FAIL
```

---

## 11. Solution Architecture (Logical)

```
┌───────────────────────────────────────────────────────────┐
│ Presentation:  React dashboard · Map view · Graph explorer │
│                Case view · Report viewer · Admin console   │
└───────────────────────────────────────────────────────────┘
                          │ REST / WebSocket
┌───────────────────────────────────────────────────────────┐
│ API Gateway:  FastAPI · AuthN/AuthZ (JWT + RBAC) · Audit   │
└───────────────────────────────────────────────────────────┘
                          │
┌───────────────────────────────────────────────────────────┐
│ Orchestration:  Celery / RQ workers over Redis queue       │
├───────────────────────────────────────────────────────────┤
│ Analysis Services                                          │
│  · Parser        · Header/Auth      · NLP Classifier       │
│  · URL Analyzer  · Attachment (sandboxed)                  │
│  · Tracer        · Enrichment (cached)   · Correlator      │
│  · Scorer        · Report Generator                        │
└───────────────────────────────────────────────────────────┘
                          │
┌───────────────────────────────────────────────────────────┐
│ Data                                                       │
│  PostgreSQL (cases, verdicts, metadata)                    │
│  Elasticsearch/OpenSearch (full-text + IOC search)         │
│  Neo4j (correlation graph)                                 │
│  MinIO/S3 object-lock (raw .eml, reports — WORM)           │
│  Redis (cache, rate-limit tokens, queue)                   │
│  Hyperledger Fabric (evidence anchors only — no PII)       │
└───────────────────────────────────────────────────────────┘
                          │
┌───────────────────────────────────────────────────────────┐
│ External: MaxMind · AbuseIPDB · VirusTotal · PhishTank     │
│           OpenPhish · URLhaus · RDAP/WHOIS · Passive DNS   │
└───────────────────────────────────────────────────────────┘
```

**Design principles**
1. **Never trust the email.** No remote resource fetch during analysis; sandbox all parsing.
2. **Original is sacred.** Analysis on copies only; original write-once.
3. **Explainable by construction.** Every score carries its contributing features.
4. **Graceful degradation.** External API down ⇒ local analysis still yields a verdict, flagged "enrichment incomplete".
5. **Privacy by design.** Masking default-on; reveal is an audited action.

---

## 12. Recommended Technology Stack

| Layer | Choice | Rationale |
|---|---|---|
| Backend | Python 3.11 + FastAPI | Best email/forensics library ecosystem; async I/O for enrichment |
| Email parsing | `email` stdlib, `mail-parser`, `extract-msg` | Handles RFC 5322 and Outlook `.msg` |
| Auth checks | `dkimpy`, `pyspf`, `checkdmarc`, `dnspython` | Standards-compliant, avoids re-implementation |
| Attachments | `oletools`, `pdfid`/`pdf-parser`, `python-magic`, `yara-python` | Static indicators without detonation |
| NLP/ML | scikit-learn (baseline), HuggingFace Transformers (DistilBERT), XGBoost (feature fusion), SHAP | Baseline + deep model; SHAP gives FR-2.11 explainability |
| Graph | Neo4j + `networkx` | Native pivoting; Louvain for clustering |
| Search | OpenSearch | Full-text + IOC queries |
| Queue | Redis + Celery | Simple, proven, scales horizontally |
| Frontend | React + TypeScript, TailwindCSS, Leaflet (maps), Cytoscape.js (graph), Recharts | Fast to build, strong viz libraries |
| Reports | WeasyPrint / ReportLab | Templated PDF with hashes |
| Ledger | Hyperledger Fabric (or Ethereum testnet for demo) | Permissioned, no gas cost, multi-party verifiable |
| Storage | PostgreSQL + MinIO (object-lock) | WORM-capable evidence store |
| Deploy | Docker Compose (demo) → Kubernetes (production) | On-prem friendly |

### 12.1 ML approach

**Feature fusion model** — three feature families concatenated into a gradient-boosted classifier, with a transformer providing text embeddings:

1. **Text features** — DistilBERT embedding of subject + body; urgency/authority/financial-instruction lexical scores; readability; imperative-verb density.
2. **Header features** — SPF/DKIM/DMARC results, alignment flags, hop count, timestamp anomalies, Reply-To mismatch, Message-ID domain mismatch, `X-Mailer` rarity.
3. **Infrastructure features** — domain age, TLD risk, IP reputation score, infra type, ASN abuse history, URL count, shortener presence, homoglyph distance to protected brands.

**Why fusion rather than text-only:** text-only models are precisely what AI-generated phishing defeats. Header and infrastructure features are far harder for an attacker to fake, so they anchor the verdict. This is a defensible design point in the pitch.

**Candidate datasets:** SpamAssassin public corpus (ham/spam), Nazario phishing corpus, Enron (legitimate business mail), CEAS 2008, TREC 2007, PhishTank/OpenPhish URL feeds, UCI Phishing Websites. Supplement with synthetically generated BEC samples for the rarest class — and *label them as synthetic* in the model card.

**Guard against the obvious trap:** these public corpora differ in era and encoding, so a naive model learns "old headers = ham". Mitigate by stripping corpus-specific headers, stratified splitting, and reporting per-class metrics rather than overall accuracy.

---

## 13. Data Requirements

| Data element | Source | Sensitivity | Retention |
|---|---|---|---|
| Raw `.eml` | Ingestion | High (may contain PII) | Per policy; legal hold overrides |
| Headers | Parsed | Medium | 180 days min (CERT-In) |
| Body text | Parsed | High | Masked by default |
| Attachments | Parsed | High | Hash retained; binary per policy |
| Verdict + features | Generated | Low | Long-term (analytics) |
| Enrichment results | External APIs | Low | Cached, TTL 24 h–7 d |
| IOCs | Extracted | Low | Long-term |
| Audit log | Generated | Medium | Immutable, long-term |
| Evidence hashes | Generated | Low (no PII) | Permanent, on ledger |

**Note:** only *hashes* go to the ledger — never message content, never PII. State this explicitly; it is both the correct design and a question judges ask.

---

## 14. Legal, Privacy and Ethical Framework

| Area | Requirement | Implementation |
|---|---|---|
| DPDP Act 2023 (India) | Lawful purpose, data minimisation, security safeguards | Purpose limited to institutional security; masking default-on; encryption at rest |
| CERT-In Directions (2022) | 6-hour incident reporting; 180-day ICT log retention in India | Reporting export template; residency-enforced storage |
| BSA 2023 §63 (formerly IEA §65B) | Certificate for admissibility of electronic records | Auto-generated certificate template with report |
| IT Act 2000 §43A, §72A | Reasonable security practices; no unlawful disclosure | RBAC + audit + access controls |
| GDPR (if EU data subjects) | Lawful basis, subject rights | Configurable retention, purge, export |
| Ethical boundary | No deanonymisation claims | UI language enforced: "probable infrastructure", "investigative lead", confidence bands |
| Ethical boundary | No active probing of attacker infrastructure | Passive enrichment only |

**Position to state clearly in the pitch:** the platform produces *investigative leads about infrastructure*, and preserves evidence integrity so that a lawful authority can take attribution further through proper legal process. It deliberately stops short of asserting identity. That restraint is a feature, not a limitation.

---

## 15. Risk Register

| ID | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| R-1 | False positives block legitimate mail | High | Medium | Out-of-band mode by default; tuneable thresholds; allowlists; feedback loop |
| R-2 | Geolocation misleads an investigation | High | High | Mandatory confidence bands and caveats; infra-type classification; never single-source |
| R-3 | Forged Received headers mislead the tracer | High | High | Trust-boundary logic (FR-3.2); label everything below boundary as unverified |
| R-4 | Enrichment API rate limits / outages | Medium | High | Aggressive caching, offline GeoLite DB, graceful degradation |
| R-5 | Training data does not reflect Indian institutional mail | High | Medium | Fine-tune on donated institutional samples; per-class metrics; drift monitoring |
| R-6 | Malicious attachment escapes analysis sandbox | High | Low | Network-isolated container, static-only parsing, resource limits, no auto-execution |
| R-7 | PII exposure via the dashboard itself | High | Medium | Masking default-on, RBAC, audited reveal |
| R-8 | Model drift as attacker tactics evolve | Medium | High | Retraining pipeline, drift alerts, rule layer for fast response |
| R-9 | Blockchain component seen as bolted-on | Medium | Medium | Scope it narrowly and defensibly: hashes only, solves a real tamper-evidence need |
| R-10 | Scope overrun in hackathon window | High | High | Strict MVP cut (§16); mocked enrichment fallback prepared in advance |
| R-11 | Encrypted or header-stripped mail yields nothing | Medium | Medium | Detect and report explicitly as "insufficient data" rather than guessing |

---

## 16. MVP Scope for the Hackathon (36 hours)

### 16.1 Must demo — the spine
1. Upload `.eml` → parse → hash → store.
2. Classifier producing verdict + score + **top contributing features**.
3. Full SPF/DKIM/DMARC evaluation with alignment.
4. Received-chain table with trust-boundary marking.
5. Earliest reliable IP → geolocation + ASN + infra type, with confidence band.
6. WHOIS/RDAP domain age and registrar; high-risk domain flags.
7. Interactive trace map.
8. Graph view linking ≥ 2 emails into one campaign (seeded demo data).
9. PDF forensic report with evidence hashes.
10. Ledger anchor + working "Verify Integrity" button.

### 16.2 Deliberately deferred
IMAP/Graph live integration · sandbox detonation · multilingual NLP · passive DNS · ARC evaluation · executive dashboard · end-user reporting plugin · Kubernetes deployment.

### 16.3 Demo narrative (5–6 minutes)
1. **Hook (30 s)** — "This email cost a university ₹12 lakh. Here is what our platform sees that a spam filter does not."
2. **Detect (60 s)** — upload the BEC sample; verdict = BEC-Fraud, score 94; show the top five signals, including DMARC fail and a 4-day-old lookalike domain.
3. **Trace (90 s)** — hop table; point out the two forged hops below the trust boundary and explain why the tool ignores them; land on the earliest reliable IP; map view; infra type = VPS, confidence banner visible.
4. **Correlate (60 s)** — graph shows this email shares an ASN with three earlier incidents → same campaign.
5. **Prove (60 s)** — export report; alter one byte of the file; hit Verify → **FAIL**; restore → **PASS**. *This is the moment that wins the room.*
6. **Close (30 s)** — impact numbers, honest limitations, roadmap.

### 16.4 Team allocation (6 members)
| Member | Ownership |
|---|---|
| 1 | Ingestion, parsing, header/auth engine |
| 2 | NLP/ML classifier + explainability |
| 3 | Tracer, geolocation, enrichment, caching |
| 4 | Graph correlation + campaign clustering |
| 5 | Frontend: dashboard, map, graph, case view |
| 6 | Report generation, ledger anchoring, integration, demo script |

**Rule for the room:** the demo dataset is prepared and cached in advance. Nothing in the live demo should depend on an external API responding.

---

## 17. Success Metrics

**Product KPIs**
- Detection F1 ≥ 0.95; FPR ≤ 2%
- p95 latency ≤ 3 s
- Relay reconstruction success ≥ 90%
- Campaign clustering recall ≥ 85%
- Report generation ≤ 60 s

**Business KPIs (post-deployment)**
- Reduction in successful phishing incidents (baseline vs. 6 months)
- Mean time to investigate: target ≥ 70% reduction
- % of incidents escalated with complete forensic evidence
- Number of campaigns identified that would previously have been isolated events
- Financial loss avoided (blocked BEC attempts × average transaction value)

---

## 18. Roadmap

| Phase | Duration | Deliverable |
|---|---|---|
| Phase 0 — Hackathon | 36 h | MVP per §16 |
| Phase 1 — Pilot | 4–6 weeks | Live IMAP/Graph integration, single-institution pilot, model fine-tuned on real mail |
| Phase 2 — Hardening | 8–10 weeks | Sandbox integration, ARC, multilingual NLP, RBAC/audit completion, Kubernetes |
| Phase 3 — Scale | 3–4 months | Multi-tenant, federated threat sharing across institutions, MISP/STIX exchange |
| Phase 4 — Ecosystem | 6+ months | CERT-In reporting integration, cross-institution campaign intelligence, SOAR playbooks |

---

## 19. Open Questions

1. Which mail platform does the pilot institution use (Exchange, M365, Google Workspace, on-prem Postfix)? Determines the ingestion path.
2. Is out-of-band journaling acceptable, or is inline blocking required?
3. What is the approved retention period for message bodies vs. headers?
4. Which threat-intel feeds are licensed/available, and at what quota?
5. Who is the designated examiner for forensic reports, and what certification is required for admissibility?
6. Is the permissioned ledger to be operated by the institution, or by a consortium of institutions? Consortium is stronger evidentially but harder to stand up.
7. What volume of labelled institutional mail can be donated for fine-tuning?
8. Are there existing SIEM/SOAR tools the platform must integrate with?

---

## 20. Traceability Matrix (Problem Statement → Requirements)

| Problem statement component | Covered by |
|---|---|
| Fraudulent Email Detection Engine | FR-2.1 – FR-2.13 |
| Email Header and Protocol Analysis | FR-3.1 – FR-3.10 |
| Origin Traceability and Location Analysis | FR-4.1 – FR-4.11 |
| Identity Correlation and Attribution Support | FR-5.1 – FR-5.9 |
| Alerting, Dashboard, Forensic Reporting | FR-6.1 – FR-6.11 |
| Privacy, Legal, Compliance Safeguards | FR-7.1 – FR-7.9 |
| Expected Outcome: early accurate detection | OBJ-1, OBJ-2, FR-2.x, FR-6.1 |
| Expected Outcome: trace origin paths | OBJ-5, FR-3.2, FR-4.1 – FR-4.7 |
| Expected Outcome: enhanced investigation | FR-4.8, FR-5.x, FR-6.9 |
| Expected Outcome: reduced loss | BG-1, FR-2.4, FR-6.1 |
| Expected Outcome: incident-response readiness | FR-6.6, FR-7.5, FR-7.6 |
| Theme: Blockchain & Cybersecurity | FR-7.6, FR-7.7 |

---

*End of document — v1.0*
