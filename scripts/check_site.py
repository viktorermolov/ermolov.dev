#!/usr/bin/env python3
"""Check generated public artifacts; no network or production submissions."""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.duplicates = set()
        self.elements = []
        self.schema_text = []
        self.in_schema = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.elements.append((tag, attrs))
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                self.duplicates.add(attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_schema = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_schema = False

    def handle_data(self, data):
        if self.in_schema:
            self.schema_text.append(data)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'public').resolve()
    text = (root / 'index.html').read_text()
    page = Page()
    page.feed(text)
    assert not page.duplicates, f'Duplicate IDs: {page.duplicates}'
    assert sum(tag == 'h1' for tag, _ in page.elements) == 1, 'Exactly one h1 required'
    assert any(tag == 'link' and attrs.get('rel') == 'canonical' and attrs.get('href') == 'https://ermolov.dev/' for tag, attrs in page.elements), 'Canonical URL'
    assert any(tag == 'meta' and attrs.get('name') == 'description' and attrs.get('content') for tag, attrs in page.elements), 'Description'
    schema = json.loads(''.join(page.schema_text))
    assert schema.get('@context') == 'https://schema.org', 'Valid structured data'
    assert any(tag == 'form' and attrs.get('id') == 'contact-form' for tag, attrs in page.elements), 'Contact form'
    fields = {attrs.get('name'): attrs for tag, attrs in page.elements if tag in ('input', 'textarea', 'select')}
    assert fields['email'].get('type') == 'email' and 'required' in fields['email'], 'Required email'
    assert fields['message'].get('maxlength') == '2500' and 'required' in fields['message'], 'Bounded required message'
    assert 'mailto:viktor@ermolov.dev' in text, 'Email fallback'
    assert any(tag == 'noscript' for tag, _ in page.elements), 'No-JS fallback'
    for tag, attrs in page.elements:
        for key in ('href', 'src'):
            target = attrs.get(key)
            if not target:
                continue
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            if not url.path:
                if url.fragment:
                    assert unquote(url.fragment) in page.ids, f'Broken anchor {target}'
                continue
            if url.path.startswith('/api/'):
                continue
            asset = root / unquote(url.path).lstrip('/')
            if url.path.endswith('/'):
                asset /= 'index.html'
            assert asset.is_file(), f'Missing local asset {target}'
    sitemap = ET.parse(root / 'sitemap.xml')
    assert any(element.text == 'https://ermolov.dev/' for element in sitemap.iter() if element.tag.endswith('loc')), 'Sitemap canonical'
    assert 'https://ermolov.dev/sitemap.xml' in (root / 'robots.txt').read_text(), 'Robots sitemap'
    assert (root / 'og/og-default.png').is_file(), 'Social preview'
    print('PASS: generated site, form, anchors, local assets, SEO, and fallback')


if __name__ == '__main__':
    main()
