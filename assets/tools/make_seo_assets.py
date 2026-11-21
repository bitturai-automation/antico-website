"""Generate favicons + Open Graph / Twitter share images. Run from project root:  python3 tools/make_seo_assets.py
Needs Pillow. Fonts: Manrope (ExtraBold/Bold) + Inter, paths below."""
import json, re, os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MAN8, MAN7 = '/tmp/fnt/Manrope-800.ttf', '/tmp/fnt/Manrope-700.ttf'
INTER, INTER_SB = '/usr/share/fonts/opentype/inter/Inter-Medium.otf', '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
F = lambda p, s: ImageFont.truetype(p, s)

# ---------- favicons ----------
logo = Image.open('images/logo.png').convert('RGBA')
mark = Image.open('images/logo-mark.png').convert('RGBA')   # official 'A' mark (transparent PNG)
def icon(size, pad=0.2, bg=(255, 255, 255, 255), radius=0.22):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, size - 1, size - 1), int(size * radius), fill=bg)
    m = mark.copy(); box = int(size * (1 - 2 * pad)); m.thumbnail((box, box), Image.LANCZOS)
    im.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2)); return im
icon(512, 0.2).save('images/icon-512.png'); icon(192, 0.2).save('images/icon-192.png')
icon(180, 0.16, radius=0).convert('RGB').save('images/apple-touch-icon.png')
# browser-tab icons: blue mark on a transparent background, almost full-bleed so it stays readable at 16px
icon(64, 0.03, bg=(0, 0, 0, 0)).save('favicon.png')
icon(256, 0.03, bg=(0, 0, 0, 0)).save('favicon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

# ---------- OG images ----------
W, H = 1200, 630
def canvas():
    base = Image.new('RGB', (W, H), (7, 26, 47))
    px = base.load()
    glow = Image.new('RGB', (W, H), (0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse((-420, -520, 640, 420), fill=(2, 99, 204)); g.ellipse((620, 260, 1560, 1100), fill=(38, 128, 240))
    glow = glow.filter(ImageFilter.GaussianBlur(170))
    base = Image.blend(base, Image.composite(glow, base, Image.new('L', (W, H), 255)), 0.55)
    d = ImageDraw.Draw(base, 'RGBA')
    return base
def white_logo(width):
    l = Image.open('images/logo-white.png').convert('RGBA'); h = int(l.height * width / l.width); return l.resize((width, h), Image.LANCZOS)
def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
def chip(d, xy, text, font):
    x, y = xy; w = d.textlength(text, font=font)
    d.rounded_rectangle((x, y, x + w + 36, y + 44), 22, fill=(2, 99, 204, 255)); d.text((x + 18, y + 9), text, font=font, fill='white'); return x + w + 36

def card(title, sub, chiptxt, out, photo=None):
    im = canvas(); d = ImageDraw.Draw(im, 'RGBA')
    im.paste(white_logo(380), (64, 56), white_logo(380))
    tw = 600 if photo else 960
    size = 66
    while True:
        f = F(MAN8, size); lines = wrap(d, title, f, tw)
        if len(lines) <= 3 and size >= 40 or size <= 40: break
        if len(lines) <= 3: break
        size -= 4
    y = 190
    cx = 64
    if chiptxt: chip(d, (64, y), chiptxt.upper(), F(INTER_SB, 20)); y += 74
    for ln in lines: d.text((64, y), ln, font=f, fill='white'); y += int(size * 1.14)
    y += 14
    for ln in wrap(d, sub, F(INTER, 28), tw)[:3]: d.text((64, y), ln, font=F(INTER, 28), fill=(190, 214, 245)); y += 40
    d.line((64, 560, W - 64, 560), fill=(143, 192, 255, 70), width=1)
    d.text((64, 578), 'PTFE · PFA · FEP lined flow systems', font=F(INTER_SB, 22), fill=(143, 192, 255))
    t = 'Vadodara, Gujarat, India'; d.text((W - 64 - d.textlength(t, font=F(INTER, 22)), 578), t, font=F(INTER, 22), fill=(190, 214, 245))
    if photo:
        p = Image.open(photo).convert('RGB'); box = 430
        p.thumbnail((box - 40, box - 40), Image.LANCZOS)
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        x0, y0 = 700, 100; sd.rounded_rectangle((x0, y0 + 14, x0 + box, y0 + box + 14), 34, fill=(0, 0, 0, 120))
        sh = sh.filter(ImageFilter.GaussianBlur(24)); im = Image.alpha_composite(im.convert('RGBA'), sh).convert('RGB')
        d = ImageDraw.Draw(im); d.rounded_rectangle((x0, y0, x0 + box, y0 + box), 34, fill='white')
        im.paste(p, (x0 + (box - p.width) // 2, y0 + (box - p.height) // 2))
    im.save(out, 'JPEG', quality=66, optimize=True, subsampling=2)

TAG = 'Engineered to resist corrosion'
card(TAG + '.', 'High-performance PTFE, PFA & FEP lined pipes, fittings, valves, bellows and sight flow indicators.', '', 'images/og/default.jpg')
pages = {
 'about': ('About Antico Flow System', 'In-house manufacturer of fluoropolymer lined flow systems for demanding chemical and process industries.', 'About us'),
 'contact': ('Request a quote', 'Send your drawings, media and duty conditions. Our engineers respond with a proposal.', 'Contact'),
 'blog': ('Insights on lined flow systems', 'Practical notes on corrosion-resistant PTFE, PFA and FEP lined equipment.', 'Blog'),
 'applications': ('Applications by industry', 'Lined flow systems for chemical, pharmaceutical, petrochemical, fertilizer and process industries.', 'Applications'),
 'products': ('Lined pipes, fittings, valves & bellows', 'The complete Antico product range, with sizes, linings and technical drawings.', 'Products'),
}
for k, (t, s, c) in pages.items(): card(t, s, c, f'images/og/{k}.jpg')
apps = {'chemical-processing': 'Chemical Processing', 'fertilizer': 'Fertilizer', 'petrochemical': 'Petrochemical', 'pharmaceutical': 'Pharmaceutical', 'process-manufacturing': 'Process Manufacturing', 'specialty-chemicals': 'Specialty Chemicals'}
for k, t in apps.items(): card(f'Lined flow systems for {t}', 'Corrosion-resistant PTFE, PFA and FEP lined equipment built for your process.', 'Applications', f'images/og/app-{k}.jpg')
S = open('js/products-data.js', encoding='utf-8').read()
P = json.loads(re.search(r'window\.PRODUCTS=(\[.*?\]);', S, re.S).group(1))
G = json.loads(re.search(r'PRODUCT_GROUPS\s*=\s*(\{.*?\});', S, re.S).group(1))
for p in P:
    card(p['name'], 'Fluoropolymer lined, made in-house to your approved drawing and tested before dispatch.', G.get(p['grp'], 'Product'), f"images/og/{p['id']}.jpg", photo=f"images/products/{p['images'][0]}")
print('done', len(os.listdir('images/og')), 'og images')
