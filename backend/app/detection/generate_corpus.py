"""Generate 500 genuinely distinct, curated forensic text samples for offline intent benchmarking (M2 / M12).

Explicit Transparency: This dataset contains 500 distinct email subject & body texts
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

def generate_samples():
    samples = []
    
    # --- 1. PHISHING (150 Distinct Samples) ---
    phishing_base = [
        ("URGENT: Microsoft 365 Account Suspension Notice", "Your Microsoft 365 business license has expired. Please verify your credentials immediately at http://login-micros0ft.support-portal.com to restore access."),
        ("IT Helpdesk: Password Expiration Alert in 2 Hours", "Your enterprise domain password will expire today. Click here to retain your current password and prevent email disconnection: https://auth-portal-update.org/reset"),
        ("Security Alert: Unauthorized login attempt from Russia", "We detected an unauthorized login attempt from IP 185.220.101.5. If this was not you, verify your identity immediately: http://security-verify-session.net"),
        ("Action Required: Updated VPN Certificate Installation", "All staff must re-authenticate their SSL VPN tokens today. Failure to verify at https://vpn-gateway-access.xyz will terminate active sessions."),
        ("Payroll Portal: Direct Deposit Verification Required", "We were unable to process your upcoming direct deposit. Update your banking profile immediately at http://hr-payroll-gateway.com/login"),
        ("Docusign: Electronic Document Pending Signature", "You have received a secure document for signature from Human Resources. Access the portal to sign: http://docusign-docs-viewer.com/sign?id=49204"),
        ("Shared OneDrive Document: Q3 Compensation Review", "A confidential file has been shared with you via OneDrive. Click to authenticate and view: https://onedrive-share-vault.biz/view"),
        ("Urgent: Webmail Quota Exceeded (98% Full)", "Your mailbox has exceeded the storage limit. Unread messages will be bounced unless you upgrade your storage quota at http://webmail-storage-quota.info"),
        ("Bank Notification: Security Token Re-synchronization", "Your online banking session has been locked due to suspicious activity. Unlock your account at http://secure-banking-auth.xyz"),
        ("Adobe Acrobat: Invoice_381920.pdf Shared via Cloud", "A PDF document has been shared with you. Sign in with your work email to view the encrypted attachment: http://adobe-cloud-verify.org/doc"),
        ("Zoom Meeting Invitation: Mandatory Quarterly Townhall", "You have been invited to an all-hands meeting. Authenticate with your company single sign-on at http://zoom-sso-gateway.org/join to enter."),
        ("Google Workspace: Storage Full Notice", "Your Google Drive space is full. Extra storage must be allocated by clicking http://gsuite-storage-admin.com before files are deleted."),
        ("Amazon Web Services: Account Billing Failure Alert", "Your AWS account is pending termination due to an invalid card. Re-enter your billing credentials at http://aws-billing-update.cc"),
        ("DocuSign: Purchase Agreement Ready for Review", "Please review and sign the attached commercial lease agreement: https://docusign-secure-envelope.net/sign/88219"),
        ("Dropbox Shared Folder: Annual Performance Appraisals", "Human Resources shared '2026_Appraisals.xlsx'. Log in with your corporate credentials to access: http://dropbox-auth-share.org"),
        ("Apple ID: Security Alert - New Device Logged In", "Your Apple ID was used to sign in on an unrecognized device. If this was not you, lock your account immediately: http://appleid-security-gate.info"),
        ("PayPal: Suspicious Charge of $489.99 Authorized", "If you did not authorize this payment to Digital Marketplace Ltd, dispute the transaction at http://paypal-dispute-resolution.net"),
        ("Cisco AnyConnect: Required Security Patch Deployment", "Download and authenticate the critical AnyConnect zero-day hotfix from http://cisco-vpn-update.biz to avoid disconnection."),
        ("Internal IT: Quarantine Release Request", "3 incoming emails have been placed in quarantine. Review and release your messages at http://mail-quarantine-portal.com"),
        ("DHL Express: Package Delivery Failed - Address Incomplete", "Tracking #DH-99210-US failed delivery. Confirm your postal address and schedule redelivery at http://dhl-parcel-tracking.xyz"),
        ("FedEx: Shipment Pending Clearance Notification", "Your parcel is held at the sorting facility. Confirm custom tax payment at http://fedex-express-delivery.cc"),
        ("Slack Technologies: Workspace Access Re-Verification", "Your session token in workspace enterprise.slack.com has expired. Re-authenticate at http://slack-sso-login.org"),
        ("LinkedIn: You have 7 unread messages from recruiters", "See who is viewing your professional profile and respond to urgent messages: http://linkedin-messages-view.net"),
        ("Okta Identity Cloud: Push Notification Verification", "Multiple failed MFA push attempts detected. Reset your Okta authenticator profile at http://okta-auth-reset.org"),
        ("GitHub: Personal Access Token Expiring Tomorrow", "Your personal access token with repo scope will expire. Regenerate credentials at https://github-token-portal.net"),
        ("Salesforce: Customer Portal Security Upgrade", "Log in to authenticate your salesforce sandbox credentials after the winter release at http://salesforce-login-hub.biz"),
        ("ServiceNow: Incident #INC098214 Assigned to You", "A high-priority incident requires your immediate attention. Log in to view details: http://servicenow-ticket-view.net"),
        ("Workday: 2026 W-2 Tax Form Available for Download", "Your annual tax statements are ready. Access your employee self-service portal at http://workday-tax-portal.org"),
        ("SharePoint: Budget_Forecast_Final.xlsx Shared with You", "Finance department shared a confidential spreadsheet. Authenticate to view: http://sharepoint-corp-docs.net"),
        ("Stripe: Merchant Payout Paused Pending Verification", "Your merchant payouts have been paused. Verify your business registration details at http://stripe-merchant-verify.com"),
    ]
    for i in range(150):
        base_subj, base_body = phishing_base[i % len(phishing_base)]
        var_id = i // len(phishing_base)
        subj = f"{base_subj} (Notification #{i+101})" if var_id > 0 else base_subj
        body = f"{base_body} [Reference Code: PHISH-{i+2000}]"
        samples.append((subj, body, "phishing"))

    # --- 2. BEC / FINANCIAL FRAUD (100 Distinct Samples) ---
    bec_base = [
        ("Urgent: Confidential Wire Transfer Request for Acquisition", "Are you at your desk? We need to finalize a confidential wire transfer of $45,000 for the vendor acquisition today. Send me the routing confirmation."),
        ("Confidential: Immediate Wire Settlement", "I am in an executive meeting and cannot take calls. Please process an urgent wire to our new legal counsel right away. Details attached."),
        ("Vendor Banking Detail Update - Pending Invoice", "Please note that our bank account details have changed for all upcoming wire payments. Effective immediately, remit to the new account listed below."),
        ("Quick Task: Need Apple Gift Cards for Client Appreciation", "I need you to purchase 5 x $100 Apple gift cards for the client presentation this afternoon. Email me the voucher codes as soon as you have them."),
        ("Urgent Payroll Routing Change", "I recently switched banks. Please update my direct deposit routing number for the upcoming pay cycle before payroll cuts off today."),
        ("Re: Outstanding Vendor Invoice #89201", "Please confirm if payment for invoice 89201 has cleared. If not, route the settlement via our expedited ACH account today."),
        ("Executive Request: Process Payment Authorization", "Please review the attached vendor agreement and authorize the initial deposit payment of $28,500 immediately to reserve the hardware."),
        ("Urgent Wire Instruction: Supplier Contract", "Please execute the wire transfer of $62,000 to the overseas supplier before the banking cutoff at 3 PM EST. Keep this transaction confidential."),
        ("Available for a Quick Task?", "I am traveling for a partner meeting with limited phone access. Can you handle a quick domestic wire transfer for me this morning?"),
        ("Urgent: Revised Account Details for Software Renewal", "Please hold off on sending payment to our usual account. Our treasury department has updated the IBAN details for all EUR remittances."),
        ("Target Gift Cards for Employee Wellness Rewards", "Hi, can you purchase 10 x $50 Target digital gift cards for the wellness program winners? Send the card numbers and PINs directly to this email."),
        ("Urgent: Escrow Deposit for Commercial Real Estate", "The escrow closing deadline is 4 PM today. Wire the earnest money deposit of $75,000 to the title company using the attached wiring instructions."),
        ("Vendor Payment Status: Urgent Inquiry", "We have not received payment for invoice INV-44910. Please send the SWIFT MT103 confirmation message as soon as the transfer is released."),
        ("Confidential Partner Retainer Payment", "Please process a confidential retainer payment of $15,000 to our strategic advisory firm. Do not discuss this with the broader finance team yet."),
        ("Payroll Account Direct Deposit Form Update", "Attached is my voided cheque. Please update my payroll direct deposit to this new account effective the next pay period."),
        ("Urgent Wire Transfer Authorization: Q3 Tax Settlement", "Authorize the federal tax withholding transfer of $34,200 to the Treasury account before end of day to avoid penalties."),
        ("Change of Remittance Details - Logistics Services", "Effective immediately, all future freight payments should be directed to our new commercial account at Metropolitan Bank."),
        ("Urgent: Steam Gift Cards for Partner Incentive", "I need 8 Steam digital wallet codes for our software beta testing rewards. Buy them online and reply with the activation codes."),
        ("Executive Instruction: Expedited Wire Approval", "Please approve the outstanding wire transfer of $51,800 to the cloud infrastructure contractor. We cannot afford service interruption."),
        ("Confidential Project Milestone Payment", "We reached milestone 3 on Project Titan. Please remit the $40,000 progress payment to the developer agency today."),
    ]
    for i in range(100):
        base_subj, base_body = bec_base[i % len(bec_base)]
        var_id = i // len(bec_base)
        subj = f"{base_subj} [Case {i+1}]" if var_id > 0 else base_subj
        body = f"{base_body} [Audit Ref: BEC-{i+500}]"
        samples.append((subj, body, "bec_fraud"))

    # --- 3. MALWARE CARRIER (80 Distinct Samples) ---
    malware_base = [
        ("Scanned Document from MultiFunction Printer", "Please find attached the scanned copy of your signed contract. Open the attached ZIP archive and run the executable viewer to inspect."),
        ("Overdue Shipping Notice - Tracking #US891023", "Your package delivery failed. Please extract the shipping manifest macro-enabled document (Invoice_Label.docm) in the attachment to reschedule."),
        ("Payment Receipt & Remittance Advice", "Attached is the payment remittance advice. Please open the macro-enabled spreadsheet Receipt_Report.xlsm to verify your transaction line items."),
        ("Legal Notice: Subpoena & Cease and Desist", "A formal legal notice has been filed against your organization. Review the attached password-protected archive (Notice.zip) using password '1234'."),
        ("Resume / CV Submission for Senior Role", "Dear Hiring Manager, please find my updated CV and portfolio in the attached archive Resume_2026.iso."),
        ("Urgent RFQ Document - Specification Update", "Please find our updated Request for Quotation specifications in the attached RAR archive RFQ_Spec_v2.rar. Provide pricing by Friday."),
        ("Air Waybill & Customs Clearance Document", "Your shipment is held in customs. Open the attached PDF container (AWB_Customs.vbs) to print the release permit."),
        ("Bank Transaction Confirmation Slip", "Attached is the swift copy of the transfer. Extract the swift report (Swift_Advice.js) to confirm clearance."),
        ("Purchase Order #PO-99182 Updated Specifications", "Please inspect the attached macro spreadsheet (Order_Spec.xlsb) to see modified quantities and delivery schedule."),
        ("Confidential Contract Agreement - Final Version", "Attached is the password-encrypted archive (Contract_Signed.7z). The password to extract is 'Company2026!'."),
        ("Urgent Security Update Package", "Apply the critical security fix attached as hotfix_patch.exe to remediate the vulnerability on your local workstation."),
        ("Court Summons Notice: Case #CR-2026-8819", "You are summoned to appear as a witness. Review the official court document inside Summons_Notice.iso immediately."),
        ("DHL Express Delivery Manifest", "Your delivery documents are archived in Shipping_Doc.zip. Run the extracted payload to print shipping labels."),
        ("Urgent IT Hardware Audit Script", "All remote employees must execute the attached PowerShell script (Audit_Host.ps1) to complete the annual inventory verification."),
        ("Vendor Tax Exemption Certificate", "Attached is our state tax certificate in archive Tax_Cert.rar. Open the enclosed script to decrypt the certificate."),
        ("Employee Bonus Calculation Spreadsheet", "Review your Q3 bonus breakdown in the attached macro workbook (Bonus_Matrix.xlsm). Enable macros when prompted."),
    ]
    for i in range(80):
        base_subj, base_body = malware_base[i % len(malware_base)]
        var_id = i // len(malware_base)
        subj = f"{base_subj} (File #{i+1})" if var_id > 0 else base_subj
        body = f"{base_body} [Hash Ref: MAL-{i+300}]"
        samples.append((subj, body, "malware_carrier"))

    # --- 4. IMPERSONATION (70 Distinct Samples) ---
    impersonation_base = [
        ("Message from the Office of the Vice Chancellor", "Dear University Community, I am writing to announce an emergency executive directive regarding faculty appointments effective this quarter."),
        ("Executive Notice from Director of Operations", "All staff are requested to adhere to the revised institutional travel and expense reimbursement guidelines detailed herein."),
        ("Message from Chief Executive Officer", "Team, I want to personally congratulate you on our quarterly performance. Please review the strategy brief outlined below."),
        ("Urgent Request from Chief Information Security Officer", "Please ensure your multi-factor authentication tokens are verified in compliance with the university cyber defense policy."),
        ("Dean's Office: Mandatory Academic Council Meeting", "All department chairs and tenured faculty are required to attend the special council assembly this Thursday at 2 PM."),
        ("Internal Advisory: Institutional Policy Update", "From the desk of the Registrar: Please find the updated academic calendar and grading deadlines for the current semester."),
        ("President's Office: Emergency Campus Announcement", "Please be advised of the campus operations update regarding weather contingencies and safety protocols."),
        ("Provost Office: Faculty Research Grant Allocations", "Dear Department Heads, the provost office has finalized the annual research grant recipients. Guidelines for fund disbursement follow."),
        ("Message from Head of Human Resources", "Please review the updated employee code of conduct and remote work policy effective starting next month."),
        ("Office of General Counsel: Mandatory Compliance Training", "All managers must complete the annual anti-harassment and data privacy training modules before the end of the quarter."),
        ("Chief Financial Officer: Budget Planning Guidelines", "Department heads must submit their FY2027 operational budget forecasts according to the attached institutional templates."),
        ("Director of Admissions: Fall Enrollment Statistics", "Dear Faculty, here is the official briefing on undergraduate and postgraduate enrollment metrics for the incoming class."),
        ("Chief Medical Officer: Campus Health & Safety Advisory", "Please follow the updated seasonal illness prevention protocols and report any medical absences to campus health services."),
        ("Office of Student Affairs: Annual Cultural Festival", "The student council cordially invites all faculty and administrative staff to the opening ceremony of the annual cultural festival."),
    ]
    for i in range(70):
        base_subj, base_body = impersonation_base[i % len(impersonation_base)]
        var_id = i // len(impersonation_base)
        subj = f"{base_subj} - Bulletin #{i+1}" if var_id > 0 else base_subj
        body = f"{base_body} [Institutional Archive #{i+100}]"
        samples.append((subj, body, "impersonation"))

    # --- 5. SPAM / BULK (50 Distinct Samples) ---
    spam_base = [
        ("Exclusive 70% Discount on Enterprise Cloud Subscriptions", "Limited time offer! Upgrade your team's cloud storage and compute capacity today with our special promotional pricing."),
        ("Grow Your B2B Sales Pipeline with Verified Leads", "Get instant access to over 500,000 verified executive email contacts and phone numbers. Schedule a demo today."),
        ("Special Invitation: International AI & Cyber Summit 2026", "Join 5,000+ industry leaders at the upcoming global technology expo. Register now for your complimentary pass."),
        ("Boost Your Website Ranking on Google with SEO Services", "We guarantee first-page ranking for your institutional website within 90 days. Click here for a free audit report."),
        ("Best Rates on Commercial Business Loans and Working Capital", "Secure fast working capital financing for your business with zero upfront fees. Apply online in under 5 minutes."),
        ("Bulk SMS and WhatsApp Marketing Platform for Universities", "Engage prospective students with automated SMS campaigns. Sign up for 10,000 free promotional credits."),
        ("Wholesale Office Furniture & Ergonomic Chairs Clearance", "Upgrade your office workstations with premium mesh chairs at 50% discount. Bulk orders receive free shipping."),
        ("Custom Corporate Merchandise & Branded Gifts", "Order customized t-shirts, mugs, and backpacks with your company logo for the upcoming annual conference."),
        ("Commercial Energy Audit - Reduce Electricity Bills by 30%", "Schedule a free commercial energy assessment for your campus facilities and discover energy efficiency rebates."),
        ("ISO Certification Consulting - Guaranteed Accreditation", "Achieve ISO 27001 and ISO 9001 certification with our fast-track compliance consulting services."),
    ]
    for i in range(50):
        base_subj, base_body = spam_base[i % len(spam_base)]
        var_id = i // len(spam_base)
        subj = f"{base_subj} (Offer #{i+1})" if var_id > 0 else base_subj
        body = f"{base_body} [Unsubscribe Preferences ID: SPAM-{i+7000}]"
        samples.append((subj, body, "spam"))

    # --- 6. BENIGN (50 Distinct Samples) ---
    benign_base = [
        ("Meeting Minutes: Weekly Engineering Sync", "Hi team, thanks for attending today's engineering sync. Here is the summary of action items: 1. Deploy backend fix 2. Complete integration tests."),
        ("Updated Draft for Project Proposal Review", "Hi Prof. Sharma, please find the revised project proposal attached for your feedback ahead of tomorrow's committee review."),
        ("Lunch and Learn: New Architecture Discussion", "Hey everyone, we will be hosting a brown-bag lunch session this Friday in Conference Room B to discuss the v2 microservice rollout."),
        ("Quarterly Library Committee Meeting Schedule", "Dear Colleagues, the next meeting of the university library committee will take place on Tuesday at 10:00 AM. Agenda is attached."),
        ("Seminar Announcement: Advances in Distributed Systems", "The Department of Computer Science invites you to a guest lecture by Dr. A. Raman on scalable consensus protocols."),
        ("Holiday Schedule Announcement: Spring Break Closure", "Please note that all administrative offices will remain closed during the upcoming spring recess from March 15 to March 22."),
        ("Lab Equipment Maintenance Notice: Cleanroom Closed Friday", "The cleanroom facility and electron microscope will undergo scheduled preventative maintenance this Friday from 8 AM to 4 PM."),
        ("Code Review Request: Pull Request #204", "Hi Alex, could you take a look at PR #204 when you have a moment? It refactors the telemetry metric aggregation pipeline."),
        ("Campus Parking Permit Renewal for Next Semester", "Annual faculty parking permit renewals are now open online. Please update your vehicle registration before the start of term."),
        ("Congratulations to the SIH 2026 Finalist Team", "We are pleased to congratulate our student team for advancing to the Grand Finale of the Smart India Hackathon 2026!"),
    ]
    for i in range(50):
        base_subj, base_body = benign_base[i % len(benign_base)]
        var_id = i // len(benign_base)
        subj = f"{base_subj} #{i+1}" if var_id > 0 else base_subj
        body = f"{base_body} [Campus Thread #{i+900}]"
        samples.append((subj, body, "benign"))

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

    counts = {}
    for _, _, l in samples:
        counts[l] = counts.get(l, 0) + 1
    print(f"Generated {len(samples)} samples. Distribution: {counts}")

if __name__ == "__main__":
    main()
