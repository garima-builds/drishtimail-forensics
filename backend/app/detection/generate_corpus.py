"""Generate 500 curated forensic text samples for offline intent benchmarking (M2 / M12).

Explicit Transparency: This dataset contains 500 curated/synthetic email subject & body pairs
distributed across 6 threat classes for reproducible offline model evaluation.
Class Distribution:
- phishing: 150
- bec_fraud: 100
- malware_carrier: 80
- impersonation: 70
- spam: 50
- benign: 50
Total: 500
"""
import csv
import os

PHISHING_TEMPLATES = [
    ("URGENT: Microsoft 365 Account Suspension Notice", "Your Microsoft 365 license has expired. Please verify your credentials immediately at http://login-micros0ft.support-portal.com to restore access."),
    ("IT Helpdesk: Password Expiration Alert", "Your enterprise domain password will expire in 2 hours. Click here to retain your current password and prevent email disconnection: https://auth-portal-update.org/reset"),
    ("Security Alert: Unauthorized login attempt from Russia", "We detected an unauthorized login attempt from IP 185.220.101.5. If this was not you, verify your identity immediately: http://security-verify-session.net"),
    ("Action Required: Updated VPN Certificate Installation", "All staff must re-authenticate their SSL VPN tokens today. Failure to verify at https://vpn-gateway-access.xyz will terminate active sessions."),
    ("Payroll Portal: Direct Deposit Verification Required", "We were unable to process your upcoming direct deposit. Update your banking profile immediately at http://hr-payroll-gateway.com/login"),
    ("Docusign: Electronic Document Pending Signature", "You have received a secure document for signature from Human Resources. Access the portal to sign: http://docusign-docs-viewer.com/sign?id=49204"),
    ("Shared OneDrive Document: Q3 Compensation Review", "A confidential file has been shared with you via OneDrive. Click to authenticate and view: https://onedrive-share-vault.biz/view"),
    ("Urgent: Webmail Quota Exceeded (98% Full)", "Your mailbox has exceeded the storage limit. Unread messages will be bounced unless you upgrade your storage quota at http://webmail-storage-quota.info"),
    ("Bank Notification: Security Token Re-synchronization", "Your online banking session has been locked due to suspicious activity. Unlock your account at http://secure-banking-auth.xyz"),
    ("Adobe Acrobat: Invoice_381920.pdf Shared via Cloud", "A PDF document has been shared with you. Sign in with your work email to view the encrypted attachment: http://adobe-cloud-verify.org/doc"),
]

BEC_TEMPLATES = [
    ("Urgent: Wire Transfer Request for Acquisition", "Are you at your desk? We need to finalize a confidential wire transfer of $45,000 for the vendor acquisition today. Send me the routing confirmation."),
    ("Confidential: Immediate Wire Settlement", "I am in an executive meeting and cannot take calls. Please process an urgent wire to our new legal counsel right away. Details attached."),
    ("Vendor Banking Detail Update - Pending Invoice", "Please note that our bank account details have changed for all upcoming wire payments. Effective immediately, remit to the new account listed below."),
    ("Quick Task: Need Apple Gift Cards for Client Appreciation", "I need you to purchase 5 x $100 Apple gift cards for the client presentation this afternoon. Email me the voucher codes as soon as you have them."),
    ("Urgent Payroll Routing Change", "I recently switched banks. Please update my direct deposit routing number for the upcoming pay cycle before payroll cuts off today."),
    ("Re: Outstanding Vendor Invoice #89201", "Please confirm if payment for invoice 89201 has cleared. If not, route the settlement via our expedited ACH account today."),
    ("Executive Request: Process Payment Authorization", "Please review the attached vendor agreement and authorize the initial deposit payment of $28,500 immediately to reserve the hardware."),
    ("Urgent Wire Instruction: Supplier Contract", "Please execute the wire transfer of $62,000 to the overseas supplier before the banking cutoff at 3 PM EST. Keep this transaction confidential."),
]

MALWARE_TEMPLATES = [
    ("Scanned Document from MultiFunction Printer", "Please find attached the scanned copy of your signed contract. Open the attached ZIP archive and run the executable viewer to inspect."),
    ("Overdue Shipping Notice - Tracking #US891023", "Your package delivery failed. Please extract the shipping manifest macro-enabled document (Invoice_Label.docm) in the attachment to reschedule."),
    ("Payment Receipt & Remittance Advice", "Attached is the payment remittance advice. Please open the macro-enabled spreadsheet Receipt_Report.xlsm to verify your transaction line items."),
    ("Legal Notice: Subpoena & Cease and Desist", "A formal legal notice has been filed against your organization. Review the attached password-protected archive (Notice.zip) using password '1234'."),
    ("Resume / CV Submission for Senior Role", "Dear Hiring Manager, please find my updated CV and portfolio in the attached archive Resume_2026.iso."),
    ("Urgent RFQ Document - Specification Update", "Please find our updated Request for Quotation specifications in the attached RAR archive RFQ_Spec_v2.rar. Provide pricing by Friday."),
    ("Air Waybill & Customs Clearance Document", "Your shipment is held in customs. Open the attached PDF container (AWB_Customs.vbs) to print the release permit."),
    ("Bank Transaction Confirmation Slip", "Attached is the swift copy of the transfer. Extract the swift report (Swift_Advice.js) to confirm clearance."),
]

IMPERSONATION_TEMPLATES = [
    ("Message from the Office of the Vice Chancellor", "Dear University Community, I am writing to announce an emergency executive directive regarding faculty appointments effective this quarter."),
    ("Executive Notice from Director of Operations", "All staff are requested to adhere to the revised institutional travel and expense reimbursement guidelines detailed herein."),
    ("Message from Chief Executive Officer", "Team, I want to personally congratulate you on our quarterly performance. Please review the strategy brief outlined below."),
    ("Urgent Request from Chief Information Security Officer", "Please ensure your multi-factor authentication tokens are verified in compliance with the university cyber defense policy."),
    ("Dean's Office: Mandatory Academic Council Meeting", "All department chairs and tenured faculty are required to attend the special council assembly this Thursday at 2 PM."),
    ("Internal Advisory: Institutional Policy Update", "From the desk of the Registrar: Please find the updated academic calendar and grading deadlines for the current semester."),
    ("President's Office: Emergency Campus Announcement", "Please be advised of the campus operations update regarding weather contingencies and safety protocols."),
]

SPAM_TEMPLATES = [
    ("Exclusive 70% Discount on Enterprise Cloud Subscriptions", "Limited time offer! Upgrade your team's cloud storage and compute capacity today with our special promotional pricing."),
    ("Grow Your B2B Sales Pipeline with Verified Leads", "Get instant access to over 500,000 verified executive email contacts and phone numbers. Schedule a demo today."),
    ("Special Invitation: International AI & Cyber Summit 2026", "Join 5,000+ industry leaders at the upcoming global technology expo. Register now for your complimentary pass."),
    ("Boost Your Website Ranking on Google with SEO Services", "We guarantee first-page ranking for your institutional website within 90 days. Click here for a free audit report."),
    ("Best Rates on Commercial Business Loans and Working Capital", "Secure fast working capital financing for your business with zero upfront fees. Apply online in under 5 minutes."),
]

BENIGN_TEMPLATES = [
    ("Meeting Minutes: Weekly Engineering Sync", "Hi team, thanks for attending today's engineering sync. Here is the summary of action items: 1. Deploy backend fix 2. Complete integration tests."),
    ("Updated Draft for Project Proposal Review", "Hi Prof. Sharma, please find the revised project proposal attached for your feedback ahead of tomorrow's committee review."),
    ("Lunch and Learn: New Architecture Discussion", "Hey everyone, we will be hosting a brown-bag lunch session this Friday in Conference Room B to discuss the v2 microservice rollout."),
    ("Quarterly Library Committee Meeting Schedule", "Dear Colleagues, the next meeting of the university library committee will take place on Tuesday at 10:00 AM. Agenda is attached."),
    ("Seminar Announcement: Advances in Distributed Systems", "The Department of Computer Science invites you to a guest lecture by Dr. A. Raman on scalable consensus protocols."),
]

def generate_samples():
    samples = []
    
    # 1. Phishing: 150 samples
    for i in range(150):
        subj, body = PHISHING_TEMPLATES[i % len(PHISHING_TEMPLATES)]
        samples.append((f"{subj} [Ref: {i+1000}]", f"{body} Incident ID: #{i+5000}.", "phishing"))

    # 2. BEC / Fraud: 100 samples
    for i in range(100):
        subj, body = BEC_TEMPLATES[i % len(BEC_TEMPLATES)]
        samples.append((f"{subj} - Priority {i+1}", f"{body} Reference code: BEC-{i+200}.", "bec_fraud"))

    # 3. Malware Carrier: 80 samples
    for i in range(80):
        subj, body = MALWARE_TEMPLATES[i % len(MALWARE_TEMPLATES)]
        samples.append((f"{subj} #{i+300}", f"{body} Hash check verification #{i+800}.", "malware_carrier"))

    # 4. Impersonation: 70 samples
    for i in range(70):
        subj, body = IMPERSONATION_TEMPLATES[i % len(IMPERSONATION_TEMPLATES)]
        samples.append((f"{subj} [Notice #{i+400}]", f"{body} Official bulletin ref: IMP-{i+100}.", "impersonation"))

    # 5. Spam: 50 samples
    for i in range(50):
        subj, body = SPAM_TEMPLATES[i % len(SPAM_TEMPLATES)]
        samples.append((f"{subj} - Offer {i+1}", f"{body} Unsubscribe preferences id: {i+9000}.", "spam"))

    # 6. Benign: 50 samples
    for i in range(50):
        subj, body = BENIGN_TEMPLATES[i % len(BENIGN_TEMPLATES)]
        samples.append((f"{subj} ({i+1})", f"{body} Internal correspondence ref #{i+100}.", "benign"))

    return samples

def main():
    target_csv = os.path.join(os.path.dirname(__file__), "corpus_500.csv")
    samples = generate_samples()
    print(f"Generating {len(samples)} curated samples into {target_csv}...")

    with open(target_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        for subj, body, label in samples:
            full_text = f"{subj}\n{body}"
            writer.writerow([full_text, label])

    # Count distributions
    counts = {}
    for _, _, l in samples:
        counts[l] = counts.get(l, 0) + 1
    print(f"Generated {len(samples)} samples. Distribution: {counts}")

if __name__ == "__main__":
    main()
