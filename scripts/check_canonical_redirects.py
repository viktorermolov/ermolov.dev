#!/usr/bin/env python3
"""Check the repository canonical-redirect definition.

No network requests or credentials are used. CI checks the recorded ruleset
only; it does not read or change Cloudflare.
"""
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES_REF = 'ermolov_notes_removed'
RULE_ORDER = (
    'ermolov_index_canonical',
    NOTES_REF,
    'ermolov_trailing_slash',
    'ermolov_www_canonical',
)
NOTES_PATHS = (
    '/notes/dependable-automation',
    '/notes/dependable-automation/',
    '/notes/does-this-need-ai',
    '/notes/does-this-need-ai/',
    '/notes/first-saas-release',
    '/notes/first-saas-release/',
)
UNMATCHED_NOTES_PATHS = (
    '/notes',
    '/notes/',
    '/notes/__probe-notes-unlock__',
    '/notes/__probe-notes-unlock__/',
    '/notes/dependable-automation/extra',
)
NOTES_EXPRESSION = re.compile(
    r'\(http\.host in \{"ermolov\.dev" "www\.ermolov\.dev"\}\) and '
    r'\(http\.request\.method in \{"GET" "HEAD"\}\) and '
    r'\(http\.request\.uri\.path in \{(?P<paths>.*)\}\)'
)
NOTES_ACTION = {
    'from_value': {
        'status_code': 301,
        'target_url': {'value': 'https://ermolov.dev/'},
        'preserve_query_string': False,
    }
}
OTHER_RULES = {
    'ermolov_index_canonical': {
        'ref': 'ermolov_index_canonical',
        'description': 'Canonical homepage without index.html',
        'expression': '(http.host in {"ermolov.dev" "www.ermolov.dev"}) and (http.request.method in {"GET" "HEAD"}) and http.request.uri.path eq "/index.html"',
        'action': 'redirect',
        'action_parameters': {
            'from_value': {
                'status_code': 301,
                'target_url': {'value': 'https://ermolov.dev/'},
                'preserve_query_string': True,
            }
        },
        'enabled': True,
    },
    'ermolov_trailing_slash': {
        'ref': 'ermolov_trailing_slash',
        'description': 'Directory pages without trailing slash to slash version',
        'expression': '(http.host in {"ermolov.dev" "www.ermolov.dev"}) and (http.request.method in {"GET" "HEAD"}) and (http.request.uri.path in {"/clipstay" "/pagestay" "/clipstay/alternatives" "/pagestay/alternatives" "/clipstay/privacy" "/pagestay/privacy" "/clipstay/refunds" "/pagestay/refunds"})',
        'action': 'redirect',
        'action_parameters': {
            'from_value': {
                'status_code': 301,
                'target_url': {
                    'expression': 'concat("https://ermolov.dev", http.request.uri.path, "/")'
                },
                'preserve_query_string': True,
            }
        },
        'enabled': True,
    },
    'ermolov_www_canonical': {
        'ref': 'ermolov_www_canonical',
        'description': 'Canonical apex for public pages and assets',
        'expression': 'http.host eq "www.ermolov.dev" and (http.request.method in {"GET" "HEAD"}) and not starts_with(http.request.uri.path, "/api/") and not starts_with(http.request.uri.path, "/cdn-cgi/")',
        'action': 'redirect',
        'action_parameters': {
            'from_value': {
                'status_code': 301,
                'target_url': {
                    'expression': 'concat("https://ermolov.dev", http.request.uri.path)'
                },
                'preserve_query_string': True,
            }
        },
        'enabled': True,
    },
}


def notes_paths(expression):
    match = NOTES_EXPRESSION.fullmatch(expression)
    assert match, 'notes redirect must keep the apex/www GET/HEAD scope and an exact path list'
    quoted = ' '.join(json.dumps(path) for path in NOTES_PATHS)
    assert match.group('paths') == quoted, (
        'notes redirect must list only the three removed slugs, with and without a trailing slash'
    )
    return tuple(json.loads(item) for item in match.group('paths').split(' '))


def check_definition(ruleset):
    assert ruleset.get('name') == 'ermolov.dev canonical URLs', 'Redirect ruleset name changed'
    assert ruleset.get('kind') == 'zone', 'Redirect ruleset must remain zone-scoped'
    assert ruleset.get('phase') == 'http_request_dynamic_redirect', 'Wrong redirect phase'
    assert set(ruleset) == {'name', 'kind', 'phase', 'rules'}, 'Unexpected redirect ruleset fields'
    rules = ruleset.get('rules')
    assert [rule.get('ref') for rule in rules] == list(RULE_ORDER), 'Redirect rule order changed'
    for rule in rules:
        assert set(rule) == {
            'ref', 'description', 'expression', 'action', 'action_parameters', 'enabled'
        }, f"Unexpected fields on {rule.get('ref')}"
        if rule['ref'] == NOTES_REF:
            paths = notes_paths(rule['expression'])
            assert paths == NOTES_PATHS, f'notes redirect paths changed: {paths}'
            for path in UNMATCHED_NOTES_PATHS:
                assert path not in paths, f'{path} must not 301 to the homepage'
            assert 'starts_with(http.request.uri.path, "/notes/")' not in rule['expression']
            assert rule['description'] == 'Removed notes slugs to homepage'
            assert rule['action'] == 'redirect'
            assert rule['action_parameters'] == NOTES_ACTION
            assert rule['enabled'] is True
        else:
            assert rule == OTHER_RULES[rule['ref']], f"{rule['ref']} changed"


def main():
    ruleset = json.loads((ROOT / 'infrastructure/cloudflare/canonical-redirects.json').read_text())
    check_definition(ruleset)
    print('PASS: canonical redirects keep the narrowed notes rule and the other three rules')


if __name__ == '__main__':
    main()
