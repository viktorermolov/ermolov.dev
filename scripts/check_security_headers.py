#!/usr/bin/env python3
"""Check the scoped header definition, optionally against a live API export.

No network requests or credentials are used. CI checks the repository definition;
--live-ruleset compares an independently retrieved Cloudflare ruleset snapshot.
"""
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = 'ermolov_static_security'
EXPRESSION = (
    '(http.host in {"ermolov.dev" "www.ermolov.dev"}) '
    'and not starts_with(http.request.uri.path, "/cdn-cgi/")'
)
HEADERS = {
    'content-security-policy': "base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; upgrade-insecure-requests",
    'x-content-type-options': 'nosniff',
    'x-frame-options': 'DENY',
    'referrer-policy': 'strict-origin-when-cross-origin',
    'permissions-policy': 'camera=(), microphone=(), geolocation=()',
    'strict-transport-security': 'max-age=31536000',
}
RESPONSE_ONLY_FIELDS = {'id', 'version', 'last_updated'}


def scoped_rule(ruleset):
    assert ruleset.get('kind') == 'zone', 'Security headers must remain zone-scoped'
    assert ruleset.get('phase') == 'http_response_headers_transform', 'Wrong header transform phase'
    matches = [rule for rule in ruleset.get('rules', []) if rule.get('ref') == REF]
    assert len(matches) == 1, f'Expected exactly one rule with ref {REF}'
    return matches[0]


def check_definition(ruleset):
    rule = scoped_rule(ruleset)
    assert rule.get('enabled') is True, 'Security header rule must be enabled'
    assert rule.get('action') == 'rewrite', 'Security header rule must rewrite responses'
    assert rule.get('expression') == EXPRESSION, 'Keep exact apex/www scope; /api/ 404s must receive headers'
    headers = {name: {'operation': 'set', 'value': value} for name, value in HEADERS.items()}
    headers.update({name: {'operation': 'remove'} for name in ('x-do-app-origin', 'x-rgw-object-type')})
    assert rule.get('action_parameters') == {'headers': headers}, 'Security header operations or values changed'
    return rule


def check_live_ruleset(expected, live):
    # Accept either the Cloudflare response envelope or its result object.
    if 'result' in live:
        assert live.get('success') is True, 'Cloudflare export reports an unsuccessful request'
        live = live['result']
    actual = scoped_rule(live)
    actual = {key: value for key, value in actual.items() if key not in RESPONSE_ONLY_FIELDS}
    assert actual == expected, f'Live {REF} rule differs from the repository definition'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-ruleset', type=Path, help='Fresh read-only Cloudflare ruleset JSON export')
    args = parser.parse_args()
    ruleset = json.loads((ROOT / 'infrastructure/cloudflare/security-headers.json').read_text())
    expected = check_definition(ruleset)
    if args.live_ruleset:
        check_live_ruleset(expected, json.loads(args.live_ruleset.read_text()))
        print('PASS: repository security headers and exported live scoped rule match')
    else:
        print('PASS: repository security header scope and all eight operations')


if __name__ == '__main__':
    main()
