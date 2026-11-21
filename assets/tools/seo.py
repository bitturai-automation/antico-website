"""Inject SEO / social meta into every page. Safe to re-run (replaces its own block).
Usage (from project root):   python3 tools/seo.py https://www.yourdomain.com
"""
import glob, html, json, os, re, sys, datetime

ASSETS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../assets
BASE = os.path.dirname(ASSETS)                                           # site root (holds index.html)
os.chdir(BASE)
K = lambda rel: rel[len('assets/'):] if rel.startswith('assets/') else rel  # path inside assets/ (index.html stays as is)
SITE = (sys.argv[1] if len(sys.argv) > 1 else 'https://www.anticoflowsystem.com').rstrip('/')
NAME = 'Antico Flow System'
TODAY = datetime.date.today().isoformat()
PHONE, EMAIL = '+91 90237 90640', 'mkt.anticoflowsystem@gmail.com'
START, END = '<!-- SEO:START -->', '<!-- SEO:END -->'

S = open('assets/js/products-data.js', encoding='utf-8').read()
PRODUCTS = {p['id']: p for p in json.loads(re.search(r'window\.PRODUCTS=(\[.*?\]);', S, re.S).group(1))}
GROUPS = json.loads(re.search(r'PRODUCT_GROUPS\s*=\s*(\{.*?\});', S, re.S).group(1))
e = lambda s: html.escape(s, quote=True)

TITLE_OVERRIDE = {
    'index.html': 'Antico Flow System — PTFE, PFA & FEP Lined Pipes, Valves & Fittings',
    'pages/products/index.html': 'Lined Pipes, Fittings, Valves & Bellows — Antico Flow System',
    'pages/applications/index.html': 'Applications — Industries We Serve | Antico Flow System',
}
DESC_OVERRIDE = {
    'index.html': 'PTFE, PFA & FEP lined pipes, fittings, valves, bellows and sight flow indicators for chemical and process industries. Based in Vadodara, India.',
}
APP_NAMES = {'chemical-processing': 'Chemical Processing', 'fertilizer': 'Fertilizer', 'petrochemical': 'Petrochemical',
             'pharmaceutical': 'Pharmaceutical', 'process-manufacturing': 'Process Manufacturing', 'specialty-chemicals': 'Specialty Chemicals'}

def trim_desc(d):
    d = re.sub(r'\s+', ' ', html.unescape(d)).strip()
    if len(d) <= 160: return d
    out = ''
    for sent in re.findall(r'[^.!?]+[.!?]+(?:\s|$)', d):
        if len((out + sent).strip()) <= 158: out += sent
        else: break
    out = out.strip()
    if len(out) >= 60: return out
    cut = d[:157].rsplit(' ', 1)[0].rstrip(' ,;:—-')
    return cut + '…'

def page_url(rel):
    if rel == 'index.html': return SITE + '/'
    return SITE + '/' + rel

def crumbs(rel, title_name):
    home = ('Home', SITE + '/')
    full, rel = rel, K(rel)
    if rel == 'index.html': return None
    if rel.startswith('pages/products/') and rel != 'pages/products/index.html':
        pid = os.path.basename(rel)[:-5]; p = PRODUCTS.get(pid)
        grp = GROUPS.get(p['grp'], 'Products') if p else 'Products'
        return [home, ('Products', SITE + '/assets/pages/products/index.html'),
                (grp, SITE + f"/pages/products/index.html?category={p['grp']}" if p else SITE + '/assets/pages/products/index.html'),
                (title_name, page_url(full))]
    if rel.startswith('pages/applications/'):
        if rel == 'pages/applications/index.html': return [home, ('Applications', page_url(full))]
        return [home, ('Applications', SITE + '/assets/pages/applications/index.html'), (title_name, page_url(full))]
    return [home, (title_name, page_url(full))]

def og_image(rel):
    rel = K(rel); b = os.path.basename(rel)[:-5]
    if rel == 'index.html': f = 'default'
    elif rel.startswith('pages/products/'): f = 'products' if b == 'index' else b
    elif rel.startswith('pages/applications/'): f = 'applications' if b == 'index' else 'app-' + b
    elif b in ('about', 'contact', 'blog'): f = b
    else: f = 'default'
    if not os.path.exists(f'assets/images/og/{f}.jpg'): f = 'default'
    return f'{SITE}/assets/images/og/{f}.jpg'

def jld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'

ORG = {
    '@context': 'https://schema.org', '@type': 'Organization', '@id': SITE + '/#organization', 'name': NAME,
    'url': SITE + '/', 'logo': SITE + '/assets/images/icon-512.png', 'image': SITE + '/assets/images/og/default.jpg',
    'description': 'Manufacturer of PTFE, PFA and FEP lined pipes, fittings, valves, bellows and sight flow indicators for chemical and process industries.',
    'email': EMAIL, 'telephone': PHONE,
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Vadodara', 'addressRegion': 'Gujarat', 'addressCountry': 'IN'},
    'contactPoint': [{'@type': 'ContactPoint', 'contactType': 'sales', 'telephone': PHONE, 'email': EMAIL, 'areaServed': 'IN', 'availableLanguage': ['en', 'hi']}],
}
WEBSITE = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': NAME, 'publisher': {'@id': SITE + '/#organization'}, 'inLanguage': 'en-IN'}

files = ['index.html'] + sorted(glob.glob('assets/pages/*.html') + glob.glob('assets/pages/*/*.html'))
report = []
for full in files:
    rel = K(full)
    s = open(full, encoding='utf-8').read()
    s = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', s, flags=re.S)
    depth = rel.count('/'); pre = 'assets/' if full == 'index.html' else '../' * depth

    # title
    m = re.search(r'<title>(.*?)</title>', s, re.S); title = html.unescape(m.group(1)).strip()
    if rel in TITLE_OVERRIDE: title = TITLE_OVERRIDE[rel]
    elif rel.startswith('pages/applications/'):
        n = APP_NAMES.get(os.path.basename(rel)[:-5])
        if n: title = f'{n} Lined Piping & Valves — {NAME}'
    s = s.replace(m.group(0), f'<title>{e(title)}</title>', 1)
    short = re.sub(r'\s*[—|-]\s*Antico Flow System\s*$', '', title)

    # description
    dm = re.search(r'<meta[^>]*name="description"[^>]*>', s)
    desc = DESC_OVERRIDE.get(rel) or trim_desc(re.search(r'content="([^"]*)"', dm.group(0)).group(1))
    s = s.replace(dm.group(0), f'<meta content="{e(desc)}" name="description"/>', 1)

    url = page_url(full); img = og_image(rel)
    alt = f'{short} — {NAME}'
    block = [START,
        f'<link href="{url}" rel="canonical"/>',
        '<meta content="index, follow, max-image-preview:large, max-snippet:-1" name="robots"/>',
        f'<meta content="{NAME}" name="author"/>',
        '<meta content="IN-GJ" name="geo.region"/><meta content="Vadodara" name="geo.placename"/>',
        f'<link href="{url}" hreflang="en-IN" rel="alternate"/><link href="{url}" hreflang="x-default" rel="alternate"/>',
        f'<link href="{pre}favicon.ico" rel="icon" sizes="any"/>',
        f'<link href="{pre}favicon.png" rel="icon" sizes="48x48" type="image/png"/>',
        f'<link href="{pre}images/apple-touch-icon.png" rel="apple-touch-icon"/>',
        f'<link href="{pre}site.webmanifest" rel="manifest"/>',
        '<meta content="website" property="og:type"/>',
        f'<meta content="{NAME}" property="og:site_name"/>',
        '<meta content="en_IN" property="og:locale"/>',
        f'<meta content="{e(title)}" property="og:title"/>',
        f'<meta content="{e(desc)}" property="og:description"/>',
        f'<meta content="{url}" property="og:url"/>',
        f'<meta content="{img}" property="og:image"/><meta content="{img}" property="og:image:secure_url"/>',
        '<meta content="image/jpeg" property="og:image:type"/><meta content="1200" property="og:image:width"/><meta content="630" property="og:image:height"/>',
        f'<meta content="{e(alt)}" property="og:image:alt"/>',
        '<meta content="summary_large_image" name="twitter:card"/>',
        f'<meta content="{e(title)}" name="twitter:title"/>',
        f'<meta content="{e(desc)}" name="twitter:description"/>',
        f'<meta content="{img}" name="twitter:image"/>',
        f'<meta content="{e(alt)}" name="twitter:image:alt"/>',
    ]
    if rel == 'index.html': block += [jld(ORG), jld(WEBSITE)]
    cr = crumbs(full, short)
    if cr:
        block.append(jld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(cr)]}))
    block.append(END)

    # existing product schema -> absolute urls + extra fields
    def fix(mm):
        try: o = json.loads(mm.group(2))
        except Exception: return mm.group(0)
        if o.get('@type') == 'Product':
            pid = os.path.basename(rel)[:-5]
            o['image'] = f'{SITE}/assets/images/products/{PRODUCTS[pid]["images"][0]}' if pid in PRODUCTS else o.get('image')
            o['url'] = url; o['sku'] = pid
            o['brand'] = {'@type': 'Brand', 'name': NAME}
            o['manufacturer'] = {'@id': SITE + '/#organization'}
        return mm.group(1) + json.dumps(o, ensure_ascii=False) + '</script>'
    s = re.sub(r'(<script type="application/ld\+json">)(.*?)</script>', fix, s, flags=re.S)

    s = s.replace('</head>', '\n'.join(block) + '\n</head>', 1)
    open(full, 'w', encoding='utf-8').write(s)
    report.append((full, len(title), len(desc)))

# robots, sitemap, manifest
open('robots.txt', 'w').write(f'User-agent: *\nAllow: /\nDisallow: /assets/tools/\n\nSitemap: {SITE}/sitemap.xml\n')
def prio(rel):
    rel = K(rel)
    if rel == 'index.html': return '1.0'
    if rel == 'pages/products/index.html': return '0.9'
    if rel == 'pages/applications/index.html': return '0.8'
    if rel.startswith('pages/products/'): return '0.8'
    if rel.startswith('pages/applications/') or rel in ('pages/about.html', 'pages/contact.html'): return '0.7'
    if rel == 'pages/blog.html': return '0.5'
    return '0.3'
urls = ''.join(f'  <url>\n    <loc>{page_url(r[0])}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>{prio(r[0])}</priority>\n  </url>\n' for r in report)
open('sitemap.xml', 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
open('assets/site.webmanifest', 'w').write(json.dumps({'name': NAME, 'short_name': 'Antico', 'description': 'PTFE, PFA and FEP lined flow systems.', 'start_url': '/', 'display': 'browser', 'theme_color': '#071A2F', 'background_color': '#ffffff',
    'icons': [{'src': 'images/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': 'images/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'}]}, indent=2))
bad = [r for r in report if r[1] > 70 or r[2] > 165 or r[2] < 50]
print(len(report), 'pages processed; site =', SITE); print('title/desc length outliers:', bad)
