from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-after-the-loss-2026-07')
VERSION = 'v02'
out = root / f'{VERSION}-review-pack'
out.mkdir(parents=True, exist_ok=True)

GILROY_XB = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Extrabold.ttf'
GILROY_REG = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Regular.ttf'
GILROY_BOLD = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Bold.ttf'
WHITE = (246, 248, 251, 255)
BODY = (234, 239, 243, 255)
TEAL = (0, 230, 198, 255)
logo_src = Image.open('/Users/bettybot/clawd/TBT-logos/TBT Logo/White text/The better traders 1_text white.png').convert('RGBA')

def font(size, kind='xb'):
    return ImageFont.truetype({'xb': GILROY_XB, 'bold': GILROY_BOLD, 'reg': GILROY_REG}[kind], size)

def add_gradient(im):
    w, h = im.size
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pix = ov.load()
    for y in range(h):
        for x in range(w):
            left = max(0, 1 - x / 710)
            top = max(0, 1 - y / 560)
            bottom = max(0, (y - 850) / 235)
            a = min(244, int(220 * left + 54 * top + 116 * bottom))
            pix[x, y] = (0, 4, 10, a)
    return Image.alpha_composite(im, ov)

def paste_logo(im):
    logo = logo_src.copy()
    tw = 140
    logo = logo.resize((tw, int(logo.height * tw / logo.width)), Image.Resampling.LANCZOS)
    im.alpha_composite(logo, (54, 56))

def wrap_text(draw, text, maxw, ft):
    lines = []
    for raw in text.split('\n'):
        words, cur = raw.split(), ''
        for word in words:
            test = (cur + ' ' + word).strip()
            if draw.textbbox((0, 0), test, font=ft)[2] <= maxw or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines

def draw_wrapped_fixed(draw, text, x, y, maxw, ft, fill, line_height, shadow=True):
    for line in wrap_text(draw, text, maxw, ft):
        if shadow:
            draw.text((x + 3, y + 3), line, font=ft, fill=(0, 0, 0, 190))
        draw.text((x, y), line, font=ft, fill=fill)
        y += line_height
    return y

def nav(draw, n):
    y = 1018
    draw.text((70, y), f'{n:02d}', font=font(18, 'bold'), fill=TEAL)
    cx, cy, r, sp = 540, y + 9, 5, 22
    for i in range(7):
        color = TEAL if i == n - 1 else WHITE
        x = cx + (i - 3) * sp
        draw.ellipse((x-r, cy-r, x+r, cy+r), fill=color)
    if n != 7:
        draw.text((930, y), 'Swipe ->', font=font(18, 'bold'), fill=TEAL)

bases = {
    1: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_130311_b535ecf4.png'),
    2: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_130455_11bb8af1.png'),
    3: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_130614_974771b6.png'),
    4: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_130727_e808a88a.png'),
    5: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_130844_fb0aa8c6.png'),
    6: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_131144_0a824375.png'),
    7: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260710_140452_938fc3a2.png'),
}

cfg = {
    1: ('THE TRADE\nAFTER THE\nLOSS', 'That voice saying\nmake it back now.', 70, 148, 60, 27, 675),
    2: ('Losses do not\nowe you a\npayback', 'The next trade is not\nrevenge. It is a brand\nnew decision.', 70, 156, 53, 27, 680),
    3: ('Name the urge', 'You cannot manage\nwhat you refuse to admit\nyou are feeling.', 70, 178, 62, 28, 665),
    4: ('Write the\nreset rule', 'A rule decided when\ncalm protects you\nwhen you are not.', 70, 172, 59, 27, 680),
    5: ('Step away\nfrom the desk', 'Water. A slow walk.\nTen minutes of distance\nfrom the feeling.', 70, 170, 57, 27, 680),
    6: ('Return, then\ncheck', 'Does this meet the plan,\nor am I chasing?\nHonest answer first.', 70, 175, 59, 27, 675),
    7: ('Calm is\nthe edge', 'The Better Traders', 70, 175, 63, 29, 690),
}

exports = []
for n, (title, body, x, y, title_size, body_size, maxw) in cfg.items():
    if not bases[n].exists():
        raise FileNotFoundError(bases[n])
    im = Image.open(bases[n]).convert('RGB').resize((1080, 1080), Image.Resampling.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(1.03).convert('RGBA')
    im = add_gradient(im)
    if n in (1, 7):
        paste_logo(im)
    draw = ImageDraw.Draw(im)
    yy = draw_wrapped_fixed(draw, title, x, y, maxw, font(title_size, 'xb'), WHITE, int(title_size * 1.02))
    yy += 22
    draw_wrapped_fixed(draw, body, x, yy, maxw, font(body_size, 'reg'), BODY, int(body_size * 1.22))
    nav(draw, n)
    if n == 7:
        draw.text((70, 1052), 'Educational content only. Not financial advice.', font=font(12, 'reg'), fill=(210, 220, 225, 230))
    dest = out / f'tbt-trade-after-the-loss-slide-{n:02d}-{VERSION}-review.png'
    im.convert('RGB').save(dest, quality=95)
    exports.append(dest)

TW, GAP, LABELH = 360, 34, 45
sheet = Image.new('RGB', (3*TW + 4*GAP, 3*(TW+LABELH) + 4*GAP), (4, 10, 18))
d = ImageDraw.Draw(sheet)
for i, p in enumerate(exports):
    x = GAP + (i % 3) * (TW + GAP)
    y = GAP + (i // 3) * (TW + LABELH + GAP)
    sheet.paste(Image.open(p).resize((TW, TW), Image.Resampling.LANCZOS), (x, y))
    d.text((x, y + TW + 8), f'Slide {i+1:02d}', font=font(26, 'bold'), fill=WHITE)
contact = out / f'tbt-trade-after-the-loss-contact-sheet-{VERSION}-review.png'
sheet.save(contact, quality=95)

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    'title': 'The Trade After the Loss',
    'status': 'REVIEW READY',
    'review_only': True,
    'scheduled': False,
    'created_at': datetime.now(timezone.utc).isoformat(),
    'lead': 'DANI',
    'style_lock': '/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-almost-chased-2026-06/v29-aaron-text-logo-swipe-fix/',
    'copy_gate': 'Slide 07 regenerated per Aaron feedback: Dani keeps the original calm pose/expression with her hand over the Better Traders Journal cover. Slides 01-06 are preserved from v01.',
    'base_images': {str(k): str(v) for k, v in bases.items()},
    'slides': [{'path': str(p), 'sha256': sha256(p), 'dimensions': Image.open(p).size} for p in exports],
    'contact_sheet': str(contact),
    'qa': {
        'dimensions': 'all slides exported 1080x1080; contact sheet rendered',
        'logo': 'transparent stacked TBT logo only on slide 1 and slide 7',
        'nav': 'bottom counter and centered dots on all slides; Swipe -> omitted on final slide',
        'visuals': 'Dani remains the protagonist with varied tension, reflection, rule-writing, reset, and calm-resolution beats',
        'copy': 'exact The Better Traders naming preserved; no em or en dashes',
        'compliance': 'process and risk-management education only; no tickers, prices, P&L, broker UI, signal claims, or profit guarantees',
        'review_gate': 'review-only; not scheduled'
    }
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('CONTACT', contact)
for p in exports:
    print('SLIDE', p)
print('MANIFEST', out / 'manifest.json')
