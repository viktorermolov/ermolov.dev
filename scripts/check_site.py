#!/usr/bin/env python3
"""Check generated public artifacts; no network or production submissions.

`--notes-fixture` builds a throwaway copy of the site with temporary notes and
checks that `/notes/index.xml` is generated, linked and valid. Those notes are
not part of the published site.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from email.utils import parsedate_to_datetime
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
        self.text_parts = []

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
        self.text_parts.append(data)
        if self.in_schema:
            self.schema_text.append(data)


SITE = 'https://ermolov.dev/'
BRAND = 'Viktor E.'
NOTES_SECTION = SITE + 'notes/'
NOTES_FEED = SITE + 'notes/index.xml'
ATOM_LINK = '{http://www.w3.org/2005/Atom}link'
GA_MEASUREMENT_ID = 'G-CV3FSD2MY4'
GA_TAG_SRC = f'https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}'
GA_CONFIG = re.compile(r"gtag\(\s*'config'\s*,\s*'([^']*)'\s*(,\s*\{.*?\})?\s*\)", re.DOTALL)


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
    assert metadata.get('og:site_name') == BRAND, f'{url}: consistent site brand'
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


X_PROFILE = 'https://x.com/vikermolov'
FOOTER_NAV = re.compile(r'<nav class="footer-links"[^>]*>(.*?)</nav>', re.DOTALL)
FOOTER_X = re.compile(r'<a href="' + re.escape(X_PROFILE) + r'" rel="me">X</a>')


def check_footer_x_and_homepage_alternatives(root, results):
    """Every footer links the X profile, and every alternatives page stays on its homepage row."""
    html_pages = sorted(root.rglob('*.html'))
    assert html_pages, 'generated HTML'
    for path in html_pages:
        label = path.relative_to(root).as_posix()
        navs = FOOTER_NAV.findall(path.read_text())
        assert len(navs) == 1, f'{label}: one footer link list'
        nav = navs[0]
        assert FOOTER_X.search(nav), f'{label}: footer links to {X_PROFILE} as X'
        assert 'https://ermolov.dev' not in nav and 'http://ermolov.dev' not in nav, (
            f'{label}: footer does not repeat the site URL')

    home_text = results[SITE][0]
    rows = re.findall(r'<article class="project">(.*?)</article>', home_text, re.DOTALL)
    assert rows, 'homepage project rows'
    row_paths = set()
    for row in rows:
        row_paths.update(
            urlsplit(urljoin(SITE, href)).path for href in re.findall(r'href="([^"]*)"', row))
    alternatives = sorted(
        urlsplit(url).path for url in results
        if urlsplit(url).path.rstrip('/').endswith('/alternatives'))
    assert {'/clipstay/alternatives/', '/pagestay/alternatives/'} <= set(alternatives), (
        'Clipstay and Pagestay alternatives pages')
    for path in alternatives:
        assert path in row_paths, f'{SITE}: homepage project row links to {path}'


def check_refund_assurances(root):
    """PR31's owner-directed removal applies to all public pages, including metadata."""
    for path in root.rglob('*.html'):
        page = Page()
        page.feed(path.read_text())
        parts = page.text_parts + [value for _, attrs in page.elements
                                  for key, value in attrs.items()
                                  if key in ('content', 'alt', 'title', 'aria-label') and value]
        normalized = ' '.join(' '.join(parts).casefold().replace('’', "'").split())
        for sentence in re.split(r'(?<=[.!?])\s+', normalized):
            if not re.search(r'\brefund(?:s|ed|ing)?\b', sentence) or not re.search(r'\bpro\b', sentence):
                continue
            negative_deactivation = re.search(
                r"\b(?:does not|doesn't|do not|don't|will not|won't|cannot|can't|never)\b"
                r'.{0,80}\b(?:deactivate|disable|revoke|(?:switch|turn) (?:pro )?off)\b', sentence)
            continued_activation = re.search(
                r'\b(?:stays?|remains?|continues? to be)\s+(?:active|activated|enabled|unlocked)\b', sentence)
            assert not (negative_deactivation or continued_activation), (
                f'{path.relative_to(root)}: owner-prohibited assurance about Pro staying activated after a refund')


def check_not_found(root):
    """The same 404 artifact is served at missing URLs of arbitrary depth."""
    page = Page()
    page.feed((root / '404.html').read_text())
    assert sum(tag == 'h1' for tag, _ in page.elements) == 1, '404: exactly one h1'
    assert any(tag == 'meta' and attrs.get('name') == 'robots' and
               'noindex' in attrs.get('content', '').split(',')
               for tag, attrs in page.elements), '404: must remain noindex'
    for missing in ('old-page', 'clipstay/old-page', 'pagestay/old/page/'):
        url = urljoin(SITE, missing)
        links = [urljoin(url, href) for href in hrefs(page)]
        assert SITE in links and SITE + '#projects' in links, f'{url}: 404 recovery links go home'
        assert SITE + 'clipstay/privacy/' in links and SITE + 'pagestay/privacy/' in links, f'{url}: 404 footer policies'
        for tag, attrs in page.elements:
            for key in ('href', 'src'):
                target = attrs.get(key)
                if not target:
                    continue
                resolved = urlsplit(urljoin(url, target))
                if resolved.netloc != urlsplit(SITE).netloc:
                    continue
                if target.startswith('#'):
                    assert unquote(resolved.fragment) in page.ids, f'{url}: 404 local anchor {target}'
                    continue
                asset = root / unquote(resolved.path).lstrip('/')
                if resolved.path.endswith('/'):
                    asset /= 'index.html'
                assert asset.is_file(), f'{url}: 404 missing target {target}'
                if resolved.fragment:
                    linked = Page()
                    linked.feed(asset.read_text())
                    assert unquote(resolved.fragment) in linked.ids, f'{url}: 404 broken anchor {target}'
        for rel in ('stylesheet', 'preload', 'icon', 'manifest'):
            assert any(tag == 'link' and rel in attrs.get('rel', '').split()
                       for tag, attrs in page.elements), f'{url}: 404 {rel} present'
        assert any(tag == 'script' and attrs.get('src') and
                   urlsplit(urljoin(url, attrs['src'])).netloc == urlsplit(SITE).netloc
                   for tag, attrs in page.elements), f'{url}: 404 theme script present'


def check_google_analytics(root):
    """Every public page loads the existing GA4 stream and leaves campaign parameters to gtag.js."""
    pages = sorted(root.rglob('*.html'))
    assert pages, 'generated HTML'
    required = (
        Path('index.html'),
        Path('clipstay/index.html'),
        Path('pagestay/index.html'),
        Path('clipstay/alternatives/index.html'),
        Path('pagestay/alternatives/index.html'),
        Path('404.html'),
    )
    found = {path.relative_to(root) for path in pages}
    for relative in required:
        assert relative in found, f'{relative.as_posix()}: public page missing'
    for path in pages:
        label = path.relative_to(root).as_posix()
        text = path.read_text()
        page = Page()
        page.feed(text)
        assert any(tag == 'script' and attrs.get('src') == GA_TAG_SRC and 'async' in attrs
                   for tag, attrs in page.elements), f'{label}: official gtag.js for {GA_MEASUREMENT_ID}'
        assert "gtag('js', new Date())" in text, f'{label}: official gtag.js install'
        configs = GA_CONFIG.findall(text)
        assert len(configs) == 1, f'{label}: one gtag config call'
        measurement_id, extra = configs[0]
        assert measurement_id == GA_MEASUREMENT_ID and not extra, (
            f'{label}: default GA4 config keeps page_view and campaign parameters')
        assert 'send_page_view' not in text and 'page_location' not in text, (
            f'{label}: do not replace the default page view')


def rss_links(page):
    """RSS autodiscovery links. Hugo escapes '+' in the type attribute; the parser decodes it."""
    return [attrs.get('href') for tag, attrs in page.elements
            if tag == 'link' and 'alternate' in attrs.get('rel', '').split()
            and attrs.get('type') == 'application/rss+xml']


def feed_text(parent, tag):
    element = parent.find(tag)
    value = (element.text or '').strip() if element is not None else ''
    assert value, f'Notes feed missing {tag}'
    return value


def check_notes_feed(root, results, notes):
    """The only feed is the notes section feed, and only that page links to it."""
    xml_files = sorted(path.relative_to(root).as_posix() for path in root.rglob('*.xml'))
    section = NOTES_SECTION in results
    expected_xml = ['notes/index.xml', 'sitemap.xml'] if section else ['sitemap.xml']
    assert xml_files == expected_xml, f'Unexpected XML files {xml_files}; notes feed is /notes/index.xml'
    pages = list(results.items())
    not_found = Page()
    not_found.feed((root / '404.html').read_text())
    pages.append((SITE + '404.html', (None, not_found, None, None)))
    if not section:
        for url, (_, page, _, _) in pages:
            assert not rss_links(page), f'{url}: no RSS link without a notes section'
        return

    assert (root / 'notes' / 'index.xml').is_file(), 'Notes section requires /notes/index.xml'
    try:
        document = ET.parse(root / 'notes' / 'index.xml')
    except ET.ParseError as error:
        raise AssertionError(f'Notes feed is not valid XML: {error}') from error
    rss = document.getroot()
    assert rss.tag == 'rss' and rss.attrib.get('version') == '2.0', 'Notes feed must be RSS 2.0'
    channels = [element for element in rss if element.tag == 'channel']
    assert len(channels) == 1, 'Notes feed must contain one channel'
    channel = channels[0]
    feed_text(channel, 'title')
    assert feed_text(channel, 'link') == NOTES_SECTION, 'Notes feed channel link is the notes section'
    feed_text(channel, 'description')
    assert feed_text(channel, 'language') == 'en-US', 'Notes feed language'
    self_links = [element.attrib.get('href') for element in channel.findall(ATOM_LINK)
                  if element.attrib.get('rel') == 'self']
    assert self_links == [NOTES_FEED], 'Notes feed self link'
    item_links = []
    for item in channel.findall('item'):
        link = feed_text(item, 'link')
        feed_text(item, 'title')
        feed_text(item, 'description')
        assert feed_text(item, 'guid') == link, f'{link}: notes feed guid must be the note permalink'
        published = feed_text(item, 'pubDate')
        try:
            parsedate_to_datetime(published)
        except (TypeError, ValueError) as error:
            raise AssertionError(f'Notes feed item date is invalid: {published}') from error
        item_links.append(link)
    assert sorted(item_links) == sorted(notes), (
        f'Notes feed lists exactly the published notes: {sorted(item_links)}')
    for url, (_, page, _, _) in pages:
        found = rss_links(page)
        if url == NOTES_SECTION:
            assert found == [NOTES_FEED], 'Notes list must link to the RSS feed /notes/index.xml'
        else:
            assert not found, f'{url}: RSS autodiscovery stays on the notes list page'


def check(root):
    root = Path(root).resolve()
    check_refund_assurances(root)
    check_not_found(root)
    check_google_analytics(root)
    pages = sorted(path for path in root.rglob('index.html'))
    results = {url: (text, page, metadata, nodes) for url, text, page, metadata, nodes in (check_page(root, path) for path in pages)}
    canonical = SITE

    # Rules for every page: no inquiry form, no leftover consulting copy, no internal review status.
    for url, (text, page, _, _) in results.items():
        assert not any(tag == 'form' for tag, _ in page.elements), f'{url}: the site has no contact form'
        assert 'pending review' not in text.lower(), f'{url}: never show the internal review status'
        assert '/api/' not in text, f'{url}: no references to the retired inquiry API'
        assert not any(phrase in text for phrase in ('US-based', 'Based in the US', 'in the US.')), f'{url}: no location line'
    notes = [url for url in results if url.startswith(NOTES_SECTION) and url != NOTES_SECTION]
    home_ids = results[SITE][1].ids
    assert ('notes' in home_ids) == bool(notes), 'Homepage notes section appears exactly when notes exist'
    check_notes_feed(root, results, notes)

    text, page, metadata, nodes = results[canonical]
    assert set(nodes) == {'Person', 'WebSite', 'WebPage'}, 'Expected structured data entities'
    graph = list(nodes.values())
    assert all(node.get('url') == canonical for node in graph), 'Schema URLs match canonical'
    assert nodes['WebSite'].get('name') == nodes['Person'].get('alternateName') == metadata['og:site_name'], 'Brand agrees across schema and social metadata'
    assert nodes['Person'].get('name') and nodes['Person']['name'] != nodes['Person']['alternateName'], 'Person keeps the full name; the brand is its alternate name'
    assert nodes['WebSite'].get('alternateName') == 'ermolov.dev', 'Domain is an alternate site name'
    assert 'email' not in nodes['Person'], 'Do not duplicate contact email in structured data'
    assert nodes['WebPage'].get('inLanguage') == nodes['WebSite'].get('inLanguage') == 'en-US', 'Explicit structured data language'
    for section in ('projects', 'contact'):
        assert section in page.ids, f'Homepage section #{section}'
    assert 'mailto:viktor@ermolov.dev' in text, 'Email contact'

    project_urls = sorted(url for url, (_, _, _, page_nodes) in results.items() if 'SoftwareApplication' in page_nodes)
    assert project_urls, 'At least one project page'
    rows = sum(1 for tag, attrs in page.elements if tag == 'article' and 'project' in attrs.get('class', '').split())
    assert rows == len(project_urls), 'Every project page has exactly one homepage row'
    home_links = {urlsplit(urljoin(canonical, href)).path for href in hrefs(page)}
    for url in project_urls:
        assert urlsplit(url).path in home_links, f'{url}: linked from the homepage'
    check_footer_x_and_homepage_alternatives(root, results)

    privacy_url = canonical + PRIVACY_PATH.lstrip('/')
    assert privacy_url in results, f'Privacy policy must stay at {PRIVACY_PATH}'
    privacy_text = results[privacy_url][0]
    assert 'Add clipboard when the popup opens' in privacy_text, f'{privacy_url}: documents the popup clipboard setting'
    # Every product keeps its policy at <product page>privacy/ (listed in its store listing); each is a dated page that
    # separates the extension from the website's analytics.
    assert canonical + 'clipstay/' in project_urls, 'Clipstay keeps its product page'
    for url in project_urls:
        product_privacy = url + 'privacy/'
        assert product_privacy in results, f'{url}: privacy policy must exist at {product_privacy}'
        policy_text, _, _, policy_nodes = results[product_privacy]
        assert 'Last updated' in policy_text and 'WebPage' in policy_nodes, f'{product_privacy}: dated policy page'
        assert 'Cloudflare Web Analytics' in policy_text, f'{product_privacy}: distinguishes the website from the extension'
        assert 'Google Analytics 4' in policy_text and GA_MEASUREMENT_ID in policy_text, (
            f'{product_privacy}: discloses the website GA4 measurement ID')

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
            assert urlsplit(url).path + 'privacy/' in {urlsplit(urljoin(url, link)).path for link in links}, f'{url}: links to its privacy policy'
            assert 'mailto:viktor@ermolov.dev' in page_text, f'{url}: support email'
            assert PROJECT_SECTIONS <= page_obj.ids, f'{url}: product page sections {PROJECT_SECTIONS - page_obj.ids}'
            store_links = [link for link in links if STORE_HOST in link]
            if 'Coming soon to the' in page_text:
                assert not store_links and 'installUrl' not in app and STORE_HOST not in page_text, f'{url}: no store link until the product is live'
            else:
                assert store_links and app.get('installUrl') in store_links, f'{url}: live product links to the store'
                assert f'{STORE_HOST}/detail/' in app['installUrl'], f'{url}: store listing URL'
            continue
        if url == NOTES_SECTION:
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
        for asset_path in ('css/main.css', 'js/app.js', 'fonts/BricolageGrotesque-Latin.woff2', 'fonts/Newsreader-Latin.woff2', 'og/og-default.png'):
            assert robots.can_fetch(crawler, canonical + asset_path), f'Render asset remains crawlable: {asset_path}'
    for asset in ('og/og-default.png', 'og/og-clipstay.png', 'img/favicon.ico', 'img/favicon.svg', 'img/apple-touch-icon.png'):
        assert (root / asset).is_file(), f'Missing asset: {asset}'
    print(f'PASS: {len(results)} pages; {len(project_urls)} project page(s), anchors, local assets, SEO and structured data')


FIXTURE_SECTION = """---
title: Engineering notes
description: Temporary section used to verify the engineering notes feed.
---
"""

FIXTURE_NOTES = {
    'check-site-feed-fixture.md': """---
title: Feed fixture
description: Temporary note used to verify the engineering notes feed.
date: 2026-01-15
---

Temporary body for the feed check.
""",
    'check-site-feed-fixture-two.md': """---
title: Second feed fixture
description: Second temporary note used to verify every published note is in the feed.
date: 2026-02-02
---

Second temporary body for the feed check.
""",
}

FIXTURE_DRAFT = """---
title: Draft feed fixture
description: Unpublished fixture that must stay out of the feed.
date: 2026-01-15
draft: true
---

This draft must not be published or included in the feed.
"""


def expect_feed_failure(root, label):
    try:
        check(root)
    except AssertionError as error:
        message = str(error)
        assert 'feed' in message.lower() or 'rss' in message.lower() or 'notes/index.xml' in message, (
            f'{label}: unexpected failure: {message}')
        return
    raise AssertionError(f'{label}: checker accepted an invalid notes feed')


def check_notes_fixture():
    """Published notes come from a temporary content directory and are not committed."""
    hugo = shutil.which('hugo')
    if not hugo:
        raise SystemExit('hugo is required for the notes feed fixture')
    repo = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        content = tmp / 'content'
        shutil.copytree(repo / 'content', content)
        notes = content / 'notes'
        notes.mkdir(exist_ok=True)
        section = notes / '_index.md'
        if not section.exists():
            section.write_text(FIXTURE_SECTION, encoding='utf-8')
        for name, body in FIXTURE_NOTES.items():
            (notes / name).write_text(body, encoding='utf-8')
        (notes / 'check-site-draft-fixture.md').write_text(FIXTURE_DRAFT, encoding='utf-8')
        dest = tmp / 'site'
        built = subprocess.run(
            [hugo, '--environment', 'production', '--destination', str(dest), '--contentDir', str(content)],
            cwd=repo, capture_output=True, text=True)
        if built.returncode != 0:
            sys.stderr.write(built.stdout)
            sys.stderr.write(built.stderr)
            raise SystemExit(f'hugo fixture build failed ({built.returncode})')
        assert not (dest / 'notes' / 'check-site-draft-fixture' / 'index.html').exists(), 'Draft notes stay unpublished'
        check(dest)
        feed = dest / 'notes' / 'index.xml'
        notes_html = dest / 'notes' / 'index.html'
        original_feed = feed.read_text(encoding='utf-8')
        original_html = notes_html.read_text(encoding='utf-8')
        assert 'Draft feed fixture' not in original_feed, 'Draft notes stay out of the feed'
        for name in FIXTURE_NOTES:
            slug = name.removesuffix('.md')
            assert f'{NOTES_SECTION}{slug}/' in original_feed, f'{slug}: fixture note missing from the feed'
        feed.write_text('<rss', encoding='utf-8')
        expect_feed_failure(dest, 'invalid XML')
        feed.write_text(original_feed.replace(
            f'{NOTES_SECTION}check-site-feed-fixture/', f'{SITE}clipstay/'), encoding='utf-8')
        expect_feed_failure(dest, 'feed item that is not a note')
        feed.write_text(original_feed, encoding='utf-8')
        notes_html.write_text(
            ''.join(line for line in original_html.splitlines(keepends=True) if 'application/rss' not in line),
            encoding='utf-8')
        expect_feed_failure(dest, 'notes list without a feed link')
        notes_html.write_text(original_html, encoding='utf-8')
        feed.unlink()
        expect_feed_failure(dest, 'missing feed file')
    print('PASS: notes RSS fixture (/notes/index.xml)')


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--notes-fixture':
        assert len(sys.argv) == 2, 'usage: check_site.py [--notes-fixture | DESTINATION]'
        check_notes_fixture()
        return
    check(sys.argv[1] if len(sys.argv) > 1 else 'public')


if __name__ == '__main__':
    main()
