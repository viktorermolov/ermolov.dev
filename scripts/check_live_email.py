#!/usr/bin/env python3
"""Fetch live HTML and fail if Email Address Obfuscation rewrote mailto links.

Run this after a deploy. It is not part of the required site CI job: production
keeps the rewrite until the email_off templates are published. No Cloudflare
API calls and no zone changes.
"""
import sys
import time
import urllib.error
import urllib.request


USER_AGENT = 'ermolov-release-check/1.0 (+https://ermolov.dev)'
MAILTO = 'mailto:viktor@ermolov.dev'
REWRITES = (
    '/cdn-cgi/l/email-protection',
    '__cf_email__',
    'email-decode.min.js',
)
# The issue checked these ten documents. Each one carries the footer mailto.
PAGES = (
    'https://ermolov.dev/',
    'https://ermolov.dev/clipstay/',
    'https://ermolov.dev/pagestay/',
    'https://ermolov.dev/clipstay/privacy/',
    'https://ermolov.dev/pagestay/privacy/',
    'https://ermolov.dev/clipstay/refunds/',
    'https://ermolov.dev/pagestay/refunds/',
    'https://ermolov.dev/clipstay/alternatives/',
    'https://ermolov.dev/pagestay/alternatives/',
    'https://ermolov.dev/404.html',
)


def fetch(url):
    request = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT,
        'Cache-Control': 'no-cache',
        'Accept': 'text/html',
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            final_url = response.geturl()
            body = response.read().decode('utf-8')
            content_type = response.headers.get('Content-Type', '')
    except urllib.error.HTTPError as error:
        status = error.code
        final_url = error.geturl()
        body = error.read().decode('utf-8', errors='replace')
        content_type = error.headers.get('Content-Type', '')
    return status, final_url, content_type, body


def main():
    stamp = time.time_ns()
    failures = []
    for page in PAGES:
        url = f'{page}?v={stamp}'
        try:
            status, final_url, content_type, body = fetch(url)
        except urllib.error.URLError as error:
            failures.append(f'{url}: {error.reason}')
            continue
        allowed = (200, 404) if page.endswith('/404.html') else (200,)
        if status not in allowed:
            failures.append(f'{url}: HTTP {status} from {final_url}')
            continue
        if 'text/html' not in content_type:
            failures.append(f'{url}: Content-Type {content_type or "missing"}')
        for marker in REWRITES:
            if marker in body:
                failures.append(f'{url}: still contains {marker}')
        if MAILTO not in body:
            failures.append(f'{url}: missing {MAILTO}')
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        sys.exit(1)
    print(f'PASS: {len(PAGES)} live pages contain {MAILTO} and no email-protection rewrite')


if __name__ == '__main__':
    main()
