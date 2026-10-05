#!/usr/bin/env python3
"""Check generated public artifacts; no network or production submissions."""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
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


SITE = 'https://ermolov.dev/'


def check_page(root, path):
    """Checks shared by every generated page; returns parsed state for page-specific checks."""
    relative = path.relative_to(root).as_posix()
    url = SITE + relative[:-len('index.html')]
    text = path.read_text()
    page = Page()
    page.feed(text)
    assert not page.duplicates, f'{url}: duplicate IDs {page.duplicates}'
    assert sum(tag == 'h1' for tag, _ in page.elements) == 1, f'{url}: exactly one h1 required'
    canonical_links = [attrs.get('href') for tag, attrs in page.elements if tag == 'link' and 'canonical' in attrs.get('rel', '').split()]
    assert canonical_links == [url], f'{url}: exactly one absolute self-canonical URL'
    metadata = {attrs.get('property') or attrs.get('name'): attrs.get('content', '') for tag, attrs in page.elements if tag == 'meta'}
    assert metadata.get('description'), f'{url}: description'
    assert metadata.get('og:url') == url, f'{url}: Open Graph canonical URL'
    assert metadata.get('og:site_name') == 'Viktor Ermolov', f'{url}: consistent site brand'
    for tag, attrs in page.elements:
        if tag == 'meta' and attrs.get('name', '').lower() in ('robots', 'googlebot', 'bingbot', 'googlebot-news'):
            directives = {part.strip().lower() for part in attrs.get('content', '').split(',')}
            assert not directives.intersection({'noindex', 'nofollow', 'none'}), f'{url}: must be indexable and followable'
    assert 'max-image-preview:large' in metadata.get('robots', '').split(','), f'{url}: allow large search image previews'
    assert any(tag == 'html' and attrs.get('lang') == 'en' for tag, attrs in page.elements), f'{url}: document language'
    schema = json.loads(''.join(page.schema_text))
    assert schema.get('@context') == 'https://schema.org', f'{url}: valid structured data'
    graph = schema.get('@graph', [])
    graph_ids = {node.get('@id') for node in graph}
    assert len(graph_ids) == len(graph) and all(isinstance(value, str) and value.startswith(SITE) and '#' in value for value in graph_ids), f'{url}: unique entity IDs'

    def check_schema_references(value):
        if isinstance(value, dict):
            if '@id' in value:
                assert value['@id'] in graph_ids, f"{url}: broken structured data reference {value['@id']}"
            for item in value.values():
                check_schema_references(item)
        elif isinstance(value, list):
            for item in value:
                check_schema_references(item)

    check_schema_references(graph)
    for tag, attrs in page.elements:
        for key in ('href', 'src'):
            target = attrs.get(key)
            if not target:
                continue
            resolved = urlsplit(urljoin(url, target))
            if resolved.netloc != urlsplit(SITE).netloc or resolved.path.startswith('/api/'):
                continue
            if resolved.path == urlsplit(url).path and resolved.fragment:
                assert unquote(resolved.fragment) in page.ids, f'{url}: broken anchor {target}'
                continue
            asset = root / unquote(resolved.path).lstrip('/')
            if resolved.path.endswith('/'):
                asset /= 'index.html'
            assert asset.is_file(), f'{url}: missing local target {target}'
            if resolved.fragment and asset.suffix == '.html':
                linked = Page()
                linked.feed(asset.read_text())
                assert unquote(resolved.fragment) in linked.ids, f'{url}: broken cross-page anchor {target}'
    return url, text, page, metadata, {node.get('@type'): node for node in graph}


PROJECT_SECTIONS = {'features', 'privacy', 'plan', 'good-to-know', 'support'}
STORE_HOST = 'chromewebstore.google.com'
PRIVACY_PATH = '/clipstay/privacy/'  # Listed in the Chrome Web Store: this address must never change.


def hrefs(page):
    return [attrs.get('href') for tag, attrs in page.elements if tag == 'a' and attrs.get('href')]


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'public').resolve()
    pages = sorted(path for path in root.rglob('index.html'))
    results = {url: (text, page, metadata, nodes) for url, text, page, metadata, nodes in (check_page(root, path) for path in pages)}
    canonical = SITE

    # Rules for every page: no inquiry form, no leftover consulting copy, no internal review status.
    for url, (text, page, _, _) in results.items():
        assert not any(tag == 'form' for tag, _ in page.elements), f'{url}: the site has no contact form'
        assert 'pending review' not in text.lower(), f'{url}: never show the internal review status'
        assert '/api/' not in text, f'{url}: no references to the retired inquiry API'

    text, page, metadata, nodes = results[canonical]
    assert set(nodes) == {'Person', 'WebSite', 'WebPage'}, 'Expected structured data entities'
    graph = list(nodes.values())
    assert all(node.get('url') == canonical for node in graph), 'Schema URLs match canonical'
    assert nodes['WebSite'].get('name') == nodes['Person'].get('name') == metadata['og:site_name'], 'Schema and social site names agree'
    assert nodes['WebSite'].get('alternateName') == 'ermolov.dev', 'Domain is an alternate site name'
    assert 'email' not in nodes['Person'], 'Do not duplicate contact email in structured data'
    assert nodes['WebPage'].get('inLanguage') == nodes['WebSite'].get('inLanguage') == 'en-US', 'Explicit structured data language'
    for section in ('projects', 'approach', 'notes', 'about', 'contact'):
        assert section in page.ids, f'Homepage section #{section}'
    assert 'mailto:viktor@ermolov.dev' in text, 'Email contact'

    project_urls = sorted(url for url, (_, _, _, page_nodes) in results.items() if 'SoftwareApplication' in page_nodes)
    assert project_urls, 'At least one project page'
    rows = sum(1 for tag, attrs in page.elements if tag == 'article' and 'project' in attrs.get('class', '').split())
    assert rows == len(project_urls), 'Every project page has exactly one homepage row'
    home_links = {urlsplit(urljoin(canonical, href)).path for href in hrefs(page)}
    for url in project_urls:
        assert urlsplit(url).path in home_links, f'{url}: linked from the homepage'

    privacy_url = canonical + PRIVACY_PATH.lstrip('/')
    assert privacy_url in results, f'Privacy policy must stay at {PRIVACY_PATH}'
    privacy_text, _, _, privacy_nodes = results[privacy_url]
    assert 'Last updated' in privacy_text and 'WebPage' in privacy_nodes, f'{privacy_url}: dated policy page'
    assert 'Add clipboard when the popup opens' in privacy_text, f'{privacy_url}: documents the popup clipboard setting'
    assert 'Cloudflare Web Analytics' in privacy_text, f'{privacy_url}: distinguishes the website from the extension'

    sitemap = ET.parse(root / 'sitemap.xml')
    sitemap_urls = [element.text for element in sitemap.iter() if element.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}loc']
    assert sorted(sitemap_urls) == sorted(results), 'Sitemap lists exactly the generated pages'

    for url, (page_text, page_obj, page_metadata, page_nodes) in results.items():
        if url == canonical:
            continue
        links = hrefs(page_obj)
        if url in project_urls:
            assert set(page_nodes) == {'Person', 'WebSite', 'WebPage', 'SoftwareApplication'}, f'{url}: product structured data'
            app = page_nodes['SoftwareApplication']
            assert app.get('url') == url and app.get('name') and app.get('description'), f'{url}: application identity'
            assert app.get('applicationCategory') == 'BrowserApplication', f'{url}: browser application category'
            assert app.get('operatingSystem') == 'Chrome', f'{url}: Chrome operating system'
            assert app.get('screenshot') and app.get('featureList') and app.get('image'), f'{url}: screenshots, features and icon'
            assert app.get('author', {}).get('@id') == nodes['Person'].get('@id'), f'{url}: author is the site owner'
            assert page_nodes['WebPage'].get('mainEntity', {}).get('@id') == app.get('@id'), f'{url}: page describes the application'
            assert page_metadata.get('og:type') == 'website', f'{url}: Open Graph website type'
            assert PRIVACY_PATH in {urlsplit(urljoin(url, link)).path for link in links}, f'{url}: links to its privacy policy'
            assert 'mailto:viktor@ermolov.dev' in page_text, f'{url}: support email'
            assert PROJECT_SECTIONS <= page_obj.ids, f'{url}: product page sections {PROJECT_SECTIONS - page_obj.ids}'
            store_links = [link for link in links if STORE_HOST in link]
            if 'Coming soon to the' in page_text:
                assert not store_links and 'installUrl' not in app and STORE_HOST not in page_text, f'{url}: no store link until the product is live'
            else:
                assert store_links and app.get('installUrl') in store_links, f'{url}: live product links to the store'
                assert f'{STORE_HOST}/detail/' in app['installUrl'], f'{url}: store listing URL'
            continue
        if url == canonical + 'notes/':
            assert set(page_nodes) == {'Person', 'WebSite', 'CollectionPage'}, f'{url}: collection structured data'
        elif 'WebPage' in page_nodes:
            assert set(page_nodes) == {'Person', 'WebSite', 'WebPage'}, f'{url}: standalone page structured data'
            assert page_nodes['WebPage'].get('url') == url, f'{url}: standalone page URL'
            assert page_metadata.get('og:type') == 'website', f'{url}: Open Graph website type'
        else:
            article = page_nodes.get('BlogPosting')
            assert article and article.get('url') == url and article.get('headline') and article.get('datePublished'), f'{url}: article structured data'
            assert page_metadata.get('og:type') == 'article', f'{url}: Open Graph article type'
    robots = RobotFileParser()
    robots.parse((root / 'robots.txt').read_text().splitlines())
    assert robots.site_maps() == [canonical + 'sitemap.xml'], 'Robots references the canonical sitemap'
    for crawler in ('Googlebot', 'bingbot', '*'):
        assert robots.can_fetch(crawler, canonical), 'Homepage remains crawlable'
        assert not robots.can_fetch(crawler, canonical + 'api/leads'), 'API excluded from crawl'
        for asset_path in ('css/main.css', 'js/app.js', 'fonts/BricolageGrotesque-Latin.woff2', 'fonts/Newsreader-Latin.woff2', 'og/og-default.png'):
            assert robots.can_fetch(crawler, canonical + asset_path), f'Render asset remains crawlable: {asset_path}'
    for asset in ('og/og-default.png', 'og/og-clipstay.png', 'img/favicon.ico', 'img/favicon.svg', 'img/apple-touch-icon.png'):
        assert (root / asset).is_file(), f'Missing asset: {asset}'
    print(f'PASS: {len(results)} pages; {len(project_urls)} project page(s), anchors, local assets, SEO and structured data')


if __name__ == '__main__':
    main()
