#!/usr/bin/env python3
"""Check generated public artifacts; no network or production submissions."""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.robotparser import RobotFileParser
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
    canonical = 'https://ermolov.dev/'
    canonical_links = [attrs.get('href') for tag, attrs in page.elements if tag == 'link' and 'canonical' in attrs.get('rel', '').split()]
    assert canonical_links == [canonical], 'Exactly one absolute canonical URL'
    assert any(tag == 'meta' and attrs.get('name') == 'description' and attrs.get('content') for tag, attrs in page.elements), 'Description'
    metadata = {attrs.get('property') or attrs.get('name'): attrs.get('content', '') for tag, attrs in page.elements if tag == 'meta'}
    assert metadata.get('og:url') == canonical, 'Open Graph canonical URL'
    assert metadata.get('og:site_name') == 'Viktor Ermolov', 'Consistent site brand'
    for tag, attrs in page.elements:
        if tag == 'meta' and attrs.get('name', '').lower() in ('robots', 'googlebot', 'bingbot', 'googlebot-news'):
            directives = {part.strip().lower() for part in attrs.get('content', '').split(',')}
            assert not directives.intersection({'noindex', 'nofollow', 'none'}), 'Homepage must be indexable and followable'
    assert 'max-image-preview:large' in metadata.get('robots', '').split(','), 'Allow large search image previews'
    schema = json.loads(''.join(page.schema_text))
    assert schema.get('@context') == 'https://schema.org', 'Valid structured data'
    graph = schema.get('@graph', [])
    nodes = {node.get('@type'): node for node in graph}
    assert set(nodes) == {'Person', 'Service', 'WebSite', 'WebPage'}, 'Expected structured data entities'
    graph_ids = {node.get('@id') for node in graph}
    assert len(graph_ids) == len(graph) and all(isinstance(value, str) and value.startswith(canonical + '#') for value in graph_ids), 'Unique canonical entity IDs'

    def check_schema_references(value):
        if isinstance(value, dict):
            if '@id' in value:
                assert value['@id'] in graph_ids, f"Broken structured data reference {value['@id']}"
            for item in value.values():
                check_schema_references(item)
        elif isinstance(value, list):
            for item in value:
                check_schema_references(item)

    check_schema_references(graph)
    assert all(node.get('url') == canonical for node in graph), 'Schema URLs match canonical'
    assert nodes['WebSite'].get('name') == nodes['Person'].get('name') == metadata['og:site_name'], 'Schema and social site names agree'
    assert nodes['WebSite'].get('alternateName') == 'ermolov.dev', 'Domain is an alternate site name'
    assert 'email' not in nodes['Person'], 'Do not duplicate contact email in structured data'
    assert nodes['WebPage'].get('inLanguage') == nodes['WebSite'].get('inLanguage') == 'en-US', 'Explicit structured data language'
    assert any(tag == 'html' and attrs.get('lang') == 'en' for tag, attrs in page.elements), 'Matching document language'
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
    sitemap_urls = [element.text for element in sitemap.iter() if element.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}loc']
    assert sitemap_urls == [canonical], 'Sitemap contains only the canonical homepage'
    robots = RobotFileParser()
    robots.parse((root / 'robots.txt').read_text().splitlines())
    assert robots.site_maps() == [canonical + 'sitemap.xml'], 'Robots references the canonical sitemap'
    for crawler in ('Googlebot', 'bingbot', '*'):
        assert robots.can_fetch(crawler, canonical), 'Homepage remains crawlable'
        assert not robots.can_fetch(crawler, canonical + 'api/leads'), 'API excluded from crawl'
        for asset_path in ('css/main.css', 'js/app.js', 'fonts/InterVariable-Latin.woff2', 'og/og-default.png'):
            assert robots.can_fetch(crawler, canonical + asset_path), f'Render asset remains crawlable: {asset_path}'
    assert (root / 'og/og-default.png').is_file(), 'Social preview'
    print('PASS: generated site, form, anchors, local assets, SEO, and fallback')


if __name__ == '__main__':
    main()
