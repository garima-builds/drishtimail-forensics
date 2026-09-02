"""Live Runtime End-to-End Demonstration Script (SIH26106).

Tests live communication against running FastAPI server (http://127.0.0.1:8000).
"""
import urllib.request
import urllib.parse
import json
import uuid
import sys

BASE = 'http://127.0.0.1:8000/api/v1'

def post_json(url, data, token=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def get_json(url, token=None):
    req = urllib.request.Request(url)
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

try:
    # 1. Login
    print('[1/13] Logging in...')
    auth_res = post_json(f'{BASE}/auth/login', {'email': 'admin@drishtimail.local', 'password': 'ChangeMe!2026'})
    token = auth_res['access_token']
    print('[OK] Logged in. Token received:', token[:20] + '...')

    # 2. Dashboard Summary
    print('[2/13] Fetching dashboard summary...')
    summary = get_json(f'{BASE}/dashboard/summary', token)
    print('[OK] Summary:', summary)

    # 3. Ingest realistic sample .eml
    print('[3/13] Ingesting realistic sample .eml message...')
    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
    demo_uid = uuid.uuid4().hex[:8]
    eml_body = (
        f'From: Microsoft Executive Support <support@micros0ft-portal.xyz>\r\n'
        f'To: dean@institution.ac.in\r\n'
        f'Subject: URGENT: Institutional Account Security Alert {demo_uid}\r\n'
        f'Date: Wed, 02 Sep 2026 15:00:00 +0000\r\n'
        f'Message-ID: <live-demo-{demo_uid}@micros0ft-portal.xyz>\r\n'
        f'Received: from 198.51.100.77 by mx1.institution.ac.in; Wed, 02 Sep 2026 15:00:01 +0000\r\n'
        f'Authentication-Results: mx1.institution.ac.in; spf=pass; dkim=pass header.i=@micros0ft-portal.xyz; dmarc=pass\r\n'
        f'Content-Type: text/html; charset=utf-8\r\n\r\n'
        f'<html><body>'
        f'<h3>Urgent Action Required by Office of the Director</h3>'
        f'<p>Your email account will be suspended within 2 hours due to unverified compliance certificates.</p>'
        f'<p>Re-authenticate immediately via the official portal:</p>'
        f'<a href="https://credential-stealer.xyz/login?session={demo_uid}">https://login.microsoftonline.com/common/oauth2</a>'
        f'<p>Please also confirm the invoice wire transfer to the new vendor banking account.</p>'
        f'</body></html>'
    ).encode('utf-8')

    form_data = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="live_phish_{demo_uid}.eml"\r\n'
        f'Content-Type: message/rfc822\r\n\r\n'
    ).encode('utf-8') + eml_body + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req = urllib.request.Request(f'{BASE}/ingest/upload', data=form_data, headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Authorization': f'Bearer {token}'
    })
    with urllib.request.urlopen(req) as resp:
        ingest_res = json.loads(resp.read().decode('utf-8'))
    msg_id = ingest_res['id']
    print('[OK] Ingested message ID:', msg_id, 'Score:', ingest_res.get('score'), 'Verdict:', ingest_res.get('verdict'))

    # 4. Fetch Analysis
    print('[4/13] Fetching deep dive forensic analysis...')
    analysis = get_json(f'{BASE}/messages/{msg_id}/analysis', token)
    print('[OK] Score:', analysis['score']['value'], 'Verdict:', analysis['score']['verdict'])
    print('[OK] Auth establishes:', analysis['authentication']['establishes'][:60] + '...')
    print('[OK] Lookalike authenticated?:', analysis['authentication']['is_lookalike_authenticated'])
    print('[OK] URL Mismatch detected?:', [u['mismatch_flag'] for u in analysis.get('urls', [])])
    print('[OK] Conflicts count:', len(analysis.get('conflicts', [])))
    for c in analysis.get('conflicts', []):
        print('   - Conflict:', c.get('title'), '| Severity:', c.get('severity'))

    # 5. Campaign Graph
    print('[5/13] Exploring Campaign Graph...')
    camps = get_json(f'{BASE}/campaigns', token)
    graph = get_json(f'{BASE}/graph/explore', token)
    print('[OK] Campaigns:', len(camps), '| Graph nodes:', len(graph['nodes']), '| Graph edges:', len(graph['edges']))

    # 6. Case Creation
    print('[6/13] Creating Case Dossier...')
    case_res = post_json(f'{BASE}/cases', {'title': f'Live Demo Incident {demo_uid}', 'message_ids': [msg_id]}, token)
    case_id = case_res['id']
    print('[OK] Case created:', case_id, 'Title:', case_res['title'])

    # 7. Update Case
    print('[7/13] Adding analyst observation note to case...')
    req_patch = urllib.request.Request(
        f'{BASE}/cases/{case_id}',
        data=json.dumps({'status': 'In Investigation', 'note': 'Confirmed lookalike domain with anchor mismatch.'}).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        method='PATCH'
    )
    with urllib.request.urlopen(req_patch) as resp:
        updated_case = json.loads(resp.read().decode('utf-8'))
    print('[OK] Case status:', updated_case['status'], '| Notes count:', len(updated_case['notes']))

    # 8. IOC Export (STIX)
    print('[8/13] Exporting Threat IOCs (STIX 2.1)...')
    stix = get_json(f'{BASE}/export/iocs?format=stix', token)
    print('[OK] STIX Bundle type:', stix.get('type'), '| Objects:', len(stix.get('objects', [])))

    # 9. ML Evaluation
    print('[9/13] Running ML Model Validation Benchmark...')
    eval_res = post_json(f'{BASE}/evaluation/run', {}, token)
    print('[OK] ML Validation Macro F1:', eval_res.get('macro_f1'), '| Accuracy:', eval_res.get('accuracy'))

    # 10. Ledger Entries
    print('[10/13] Checking Evidence Ledger entries...')
    ledger = get_json(f'{BASE}/ledger/entries', token)
    print('[OK] Ledger total entries:', len(ledger), '| Latest entry hash:', ledger[-1]['entry_hash'][:20] + '...')

    # 11. Merkle Root Sealing
    print('[11/13] Sealing Merkle Root...')
    root_res = post_json(f'{BASE}/ledger/roots', {}, token)
    print('[OK] Sealed Merkle Root:', root_res.get('root_hash')[:24] + '...')

    # 12. Platform Configs
    print('[12/13] Retrieving Platform Configs...')
    cfg = get_json(f'{BASE}/admin/config/trusted_mtas', token)
    print('[OK] Trusted MTAs hosts count:', len(cfg.get('value', {}).get('hosts', [])))

    # 13. PDF Report Generation
    print('[13/13] Generating Forensic PDF Report (BSA Section 63)...')
    req_pdf = urllib.request.Request(f'{BASE}/messages/{msg_id}/report.pdf')
    with urllib.request.urlopen(req_pdf) as resp:
        pdf_bytes = resp.read()
        print('[OK] PDF generated successfully! Size:', len(pdf_bytes), 'bytes | Header:', pdf_bytes[:5].decode('latin1'))

    print('\n========================================')
    print('ALL 13 RUNTIME DEMO STEPS VERIFIED 100%!')
    print('========================================')
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
