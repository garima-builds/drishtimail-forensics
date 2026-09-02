"""F5: Authentication Semantics Lookup Table & Engine.

Given the tuple (SPF, DKIM, DMARC, SPF-Alignment, DKIM-Alignment, Forwarding-Status),
synthesizes three authored, unambiguous prose explanations:
1. Establishes: What the technical cryptographic checks actually prove.
2. Does Not Establish: Explicit negative boundaries (e.g. DMARC pass on an attacker domain does NOT prove benign intent).
3. Effect on Investigation: Concrete actionable instructions for the forensic investigator.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AuthSemanticsResult:
    spf: str
    dkim: str
    dmarc: str
    spf_aligned: bool
    dkim_aligned: bool
    forwarding_detected: bool
    semantics_key: str
    establishes: str
    does_not_establish: str
    investigation_effect: str
    is_lookalike_authenticated: bool = False


def evaluate_auth_semantics(
    *,
    spf: str,
    dkim: str,
    dmarc: str,
    spf_aligned: bool = False,
    dkim_aligned: bool = False,
    forwarding_detected: bool = False,
    is_lookalike_domain: bool = False,
) -> AuthSemanticsResult:
    """Evaluate technical authentication results and produce explanatory forensics prose."""
    spf = (spf or "none").lower()
    dkim = (dkim or "none").lower()
    dmarc = (dmarc or "none").lower()

    key = (
        f"spf:{spf}|dkim:{dkim}|dmarc:{dmarc}|"
        f"spf_aln:{int(spf_aligned)}|dkim_aln:{int(dkim_aligned)}|fwd:{int(forwarding_detected)}"
    )

    # Lookalike Domain Special Case (Attacker authenticated their own lookalike domain)
    if is_lookalike_domain and (dmarc == "pass" or (spf == "pass" and spf_aligned) or (dkim == "pass" and dkim_aligned)):
        return AuthSemanticsResult(
            spf=spf,
            dkim=dkim,
            dmarc=dmarc,
            spf_aligned=spf_aligned,
            dkim_aligned=dkim_aligned,
            forwarding_detected=forwarding_detected,
            semantics_key=f"{key}|lookalike:1",
            establishes="The sending MTA holds valid cryptographic authority and DNS publishing control over the lookalike sending domain.",
            does_not_establish="Authentication of a lookalike domain does NOT establish that the message originates from the legitimate institutional brand or organization it resembles.",
            investigation_effect="Flag as deliberate deceptive infrastructure. The passing authentication confirms the attacker properly configured their infrastructure, not that the email is benign.",
            is_lookalike_authenticated=True,
        )

    # Valid Forwarding or Mailing List Scenario
    if forwarding_detected:
        if dmarc == "pass" or dkim == "pass":
            return AuthSemanticsResult(
                spf=spf,
                dkim=dkim,
                dmarc=dmarc,
                spf_aligned=spf_aligned,
                dkim_aligned=dkim_aligned,
                forwarding_detected=True,
                semantics_key=key,
                establishes="A valid forwarding chain (ARC or surviving DKIM signature) exists from an upstream forwarder/mailing list.",
                does_not_establish="Does not establish that SPF failure at the final boundary indicates direct header spoofing.",
                investigation_effect="Account for intermediary relay modifications; rely on DKIM/ARC validity and content integrity rather than SPF.",
            )
        else:
            return AuthSemanticsResult(
                spf=spf,
                dkim=dkim,
                dmarc=dmarc,
                spf_aligned=spf_aligned,
                dkim_aligned=dkim_aligned,
                forwarding_detected=True,
                semantics_key=key,
                establishes="Delivery hop analysis indicates email forwarding, which commonly breaks SPF and unaligned DKIM.",
                does_not_establish="Does not confirm whether the original sender before forwarding was authentic.",
                investigation_effect="Inspect the ARC seal chain and earliest reliable hop before the forwarding MTA.",
            )

    # Strong Aligned DMARC Pass (Legitimate Sender Domain or Compromised Account)
    if dmarc == "pass" and (spf_aligned or dkim_aligned):
        return AuthSemanticsResult(
            spf=spf,
            dkim=dkim,
            dmarc=dmarc,
            spf_aligned=spf_aligned,
            dkim_aligned=dkim_aligned,
            forwarding_detected=forwarding_detected,
            semantics_key=key,
            establishes="The message conforms to the published DMARC policy of the Header From domain with aligned SPF or DKIM verification.",
            does_not_establish="Authentication does NOT establish that the sender's account has not been compromised, nor that message content, embedded URLs, or attachments are harmless.",
            investigation_effect="Treat sender domain ownership as technically authenticated. Focus forensic investigation on account compromise indicators, anomalous payload destinations, and social engineering cues.",
        )

    # Unaligned Pass (SPF/DKIM pass on 3rd party domain, DMARC fail/none)
    if (spf == "pass" or dkim == "pass") and not (spf_aligned or dkim_aligned):
        return AuthSemanticsResult(
            spf=spf,
            dkim=dkim,
            dmarc=dmarc,
            spf_aligned=False,
            dkim_aligned=False,
            forwarding_detected=forwarding_detected,
            semantics_key=key,
            establishes="A third-party sending service or envelope domain authenticated the transmission, but it does NOT align with the visible Header From domain.",
            does_not_establish="Does not establish authorization by the visible From header organization.",
            investigation_effect="Scrutinize sender alignment. Check whether the third-party infrastructure is an authorized SaaS vendor or an unauthorized spoofing channel.",
        )

    # Direct Authentication Failure
    if any(val in {"fail", "softfail", "permerror", "temperror"} for val in (spf, dkim, dmarc)):
        return AuthSemanticsResult(
            spf=spf,
            dkim=dkim,
            dmarc=dmarc,
            spf_aligned=spf_aligned,
            dkim_aligned=dkim_aligned,
            forwarding_detected=forwarding_detected,
            semantics_key=key,
            establishes="The sending MTA failed one or more cryptographic or policy checks published by the claimed domain owner.",
            does_not_establish="A technical failure alone does not pinpoint the exact identity of the attacker or conclusively prove malicious intent (could result from misconfigured DNS).",
            investigation_effect="Elevate suspicion on sender identity. Trace originating MTA IP against threat intelligence and inspect message payload for hostile actions.",
        )

    # Neutral / None / Missing
    return AuthSemanticsResult(
        spf=spf,
        dkim=dkim,
        dmarc=dmarc,
        spf_aligned=spf_aligned,
        dkim_aligned=dkim_aligned,
        forwarding_detected=forwarding_detected,
        semantics_key=key,
        establishes="The message lacks conclusive cryptographic sender verification records or the domain has no published DMARC/SPF policy.",
        does_not_establish="Absence of authentication records does not by itself prove maliciousness, but leaves the sender identity unverified.",
        investigation_effect="Maintain limited identity confidence. Rely on independent signals such as delivery path hops, domain age, and content analysis.",
    )
