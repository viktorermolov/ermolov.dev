#!/usr/bin/env python3
"""Check email obfuscation stays off and built mailto links are exempt.

No network requests or credentials are used. CI checks the repository
definition and a Hugo build. It does not fetch production: live HTML keeps
the Cloudflare rewrite until the template change is deployed.
scripts/check_live_email.py is the post-deploy fetch and is not part of CI.
"""
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFINITION = {
    'zone_id': '3532291be695455e1ce46639f0a7dcb4',
    'id': 'email_obfuscation',
    'value': 'off',
}
OPEN = '<!--email_off-->'
CLOSE = '<!--/email_off-->'
REGION = re.compile(re.escape(OPEN) + r'(.*?)' + re.escape(CLOSE), re.DOTALL)
MAILTO = 'mailto:viktor@ermolov.dev'
ADDRESS = 'viktor@ermolov.dev'
REQUIRED = (
    'index.html',
    '404.html',
    'clipstay/index.html',
    'pagestay/index.html',
    'clipstay/privacy/index.html',
    'pagestay/privacy/index.html',
    'clipstay/refunds/index.html',
    'pagestay/refunds/index.html',
    'clipstay/alternatives/index.html',
    'pagestay/alternatives/index.html',
)


def check_definition(payload):
    assert payload == DEFINITION, (
        'email-obfuscation.json must record only email_obfuscation=off '
        f'for zone {DEFINITION["zone_id"]}'
    )


def check_page(path, html):
    assert html.count(OPEN) == html.count(CLOSE), f'{path}: unbalanced email_off comments'
    assert OPEN in html, f'{path}: missing email_off exception'
    regions = REGION.findall(html)
    assert regions, f'{path}: email_off comments are not paired'
    for region in regions:
        assert OPEN not in region and CLOSE not in region, f'{path}: nested email_off comments'
    stripped = REGION.sub('', html)
    assert OPEN not in stripped and CLOSE not in stripped, f'{path}: email_off comment left outside a pair'
    assert 'mailto:' not in stripped, f'{path}: mailto link is outside email_off'
    assert ADDRESS not in stripped, f'{path}: contact address is outside email_off'
    assert MAILTO in html, f'{path}: missing {MAILTO}'
    assert '/cdn-cgi/l/email-protection' not in html, f'{path}: built HTML must not contain the edge rewrite'
    assert '__cf_email__' not in html, f'{path}: built HTML must not contain the edge rewrite'


def main():
    if len(sys.argv) != 2:
        sys.exit('usage: python3 scripts/check_email_obfuscation.py <hugo-destination>')
    root = Path(sys.argv[1]).resolve()
    payload = json.loads((ROOT / 'infrastructure/cloudflare/email-obfuscation.json').read_text())
    check_definition(payload)
    pages = sorted(path for path in root.rglob('*.html') if path.is_file())
    assert pages, f'{root}: no HTML pages'
    missing = [rel for rel in REQUIRED if not (root / rel).is_file()]
    assert not missing, f'{root}: missing {missing}'
    for path in pages:
        check_page(path.relative_to(root), path.read_text())
    print(f'PASS: email_obfuscation=off and {len(pages)} HTML pages keep mailto inside email_off')


if __name__ == '__main__':
    main()
