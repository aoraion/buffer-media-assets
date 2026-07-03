from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/15-minute-setup-skipped-2026-07')
VERSION = 'v01'
out = root / f'{VERSION}-review-pack'
out.mkdir(parents=True, exist_ok=True)

GILROY_XB = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Extrabold.ttf'
GILROY_REG = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Regular.ttf'
GILROY_BOLD = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Bold.ttf'
WHITE = (246, 248, 251, 255)
BODY = (234, 239, 243, 255)
TEAL = (0, 230, 198, 255)
logo_src = Image.open('/Users/bettybot/clawd/TBT-logos/TBT Logo/White text/The better traders 1_text white.png').convert('RGBA')


def font(s, kind='xb'):
    return ImageFont.truetype({'xb': GILROY_XB, 'bold': GILROY_BOLD, 'reg': GILROY_REG}[kind], s)


def add_gradient(im):
    w, h = im.size
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pix = ov.load()
    if pix is None:
        raise RuntimeError('Could not access overlay pixels')
    for y in range(h):
        for x in range(w):
            left = max(0, 1 - x / 735)
            top = max(0, 1 - y / 545)
            bottom = max(0, (y - 850) / 235)
            a = min(236, int(206 * left + 58 * top + 94 * bottom))
            pix[x, y] = (0, 4, 10, a)
    return Image.alpha_composite(im, ov)


def paste_logo(im):
    logo = logo_src.copy()
    tw = 140
    logo = logo.resize((tw, int(logo.height * tw / logo.width)), Image.Resampling.LANCZOS)
    im.alpha_composite(logo, (54, 56))


def wrap_lines(d, text, maxw, ft):
    lines = []
    for raw in text.split('\n'):
        words = raw.split()
        if not words:
            lines.append('')
            continue
        cur = ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if d.textbbox((0, 0), t, font=ft)[2] <= maxw or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_wrapped(d, text, x, y, maxw, ft, fill, leading=5, shadow=True):
    lines = wrap_lines(d, text, maxw, ft)
    line_h = int(ft.size * 1.08) + leading
    blank_h = int(line_h * 0.55)
    for line in lines:
        if line:
            if shadow:
                d.text((x + 3, y + 3), line, font=ft, fill=(0, 0, 0, 185))
            d.text((x, y), line, font=ft, fill=fill)
            y += line_h
        else:
            y += blank_h
    return y


def nav(d, n):
    y = 1018
    d.text((70, y), f'{n:02d}', font=font(18, 'bold'), fill=TEAL)
    cx = 540
    cy = y + 9
    r = 5
    sp = 22
    for i in range(7):
        col = TEAL if i == n - 1 else WHITE
        x = cx + (i - 3) * sp
        d.ellipse((x - r, cy - r, x + r, cy + r), fill=col)
    if n != 7:
        d.text((930, y), 'Swipe ->', font=font(18, 'bold'), fill=TEAL)


bases = {
    1: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260703_130622_6f0267ea.png'),
    2: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260703_130744_25004baf.png'),
    3: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260703_131047_566bb711.png'),
    4: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260703_131356_d2a7f941.png'),
    5: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260703_131512_9b62227f.png'),
    6: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260703_131807_34ec1ce2.png'),
    7: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260703_131917_2c7c1638.png'),
}

cfg = {
    1: ('YOU WANTED\nTO TRADE\nNOW', 'The chart was moving.\nWaiting felt like losing.\nSo you jumped in.', 70, 166, 58, 27, 690),
    2: ('So you skipped\nthe boring part', 'Setup felt like a\nspeed bump. You told\nyourself you would\nfix it later.', 70, 156, 58, 27, 690),
    3: ('Here is what\nlater means', 'Passwords. 2FA.\nAPI permissions.\nTerminal layout.\nAll the pieces you\nwaved past.', 70, 146, 56, 26, 700),
    4: ('The problem\nshows up later', 'A weak login. A key\nwith too much access.\nA workspace that slows\nyou down.', 70, 150, 56, 26, 700),
    5: ('Build the\nfoundation first', 'Lock the account.\nLimit access. Set up\nthe terminal before\nyou need it.', 70, 152, 58, 27, 690),
    6: ('Fifteen minutes,\none time', 'Done once, that setup\ncan save a much longer\nheadache down the road.', 70, 158, 58, 27, 690),
    7: ('Build the system\nbefore you trade it', 'At The Better Traders,\nthe foundation comes\nfirst. Everything else\nis easier once it is solid.', 70, 144, 52, 25, 720),
}

exports = []
for n, (title, body, x, y, ts, bs, maxw) in cfg.items():
    if not bases[n].exists():
        raise FileNotFoundError(bases[n])
    im = Image.open(bases[n]).convert('RGB').resize((1080, 1080), Image.Resampling.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(1.03).convert('RGBA')
    im = add_gradient(im)
    if n in (1, 7):
        paste_logo(im)
    d = ImageDraw.Draw(im)
    yy = draw_wrapped(d, title, x, y, maxw, font(ts, 'xb'), WHITE, leading=6)
    yy += 22
    draw_wrapped(d, body, x, yy, maxw, font(bs, 'reg'), BODY, leading=5)
    nav(d, n)
    if n == 7:
        d.text((70, 1052), 'Educational content only. Not financial advice.', font=font(12, 'reg'), fill=(210, 220, 225, 230))
    dest = out / f'tbt-15-minute-setup-skipped-slide-{n:02d}-{VERSION}-review.png'
    im.convert('RGB').save(dest, quality=95)
    exports.append(dest)

TW = 360
GAP = 34
LABELH = 45
sheet = Image.new('RGB', (3 * TW + 4 * GAP, 3 * (TW + LABELH) + 4 * GAP), (4, 10, 18))
d = ImageDraw.Draw(sheet)
for i, p in enumerate(exports):
    x = GAP + (i % 3) * (TW + GAP)
    y = GAP + (i // 3) * (TW + LABELH + GAP)
    sheet.paste(Image.open(p).resize((TW, TW), Image.Resampling.LANCZOS), (x, y))
    d.text((x, y + TW + 8), f'Slide {i + 1:02d}', font=font(26, 'bold'), fill=WHITE)
contact = out / f'tbt-15-minute-setup-skipped-contact-sheet-{VERSION}-review.png'
sheet.save(contact, quality=95)

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    'title': 'The 15-Minute Setup You Skipped',
    'status': 'REVIEW READY',
    'review_only': True,
    'scheduled': False,
    'created_at': datetime.now(timezone.utc).isoformat(),
    'lead': 'JESS',
    'style_lock': '/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-almost-chased-2026-06/v29-aaron-text-logo-swipe-fix/',
    'copy_gate': 'Claude Opus copy pass completed; Hermes tightened overlay copy, preserved The Better Traders brand name, and enforced compliance constraints.',
    'slides': [{'path': str(p), 'sha256': sha256(p), 'dimensions': Image.open(p).size} for p in exports],
    'contact_sheet': str(contact),
    'qa': {
        'dimensions': 'all slides exported 1080x1080; contact sheet rendered',
        'logo': 'transparent stacked TBT logo only on slide 1 and slide 7',
        'nav': 'bottom counter and dots on all slides; Swipe -> omitted on final slide',
        'compliance': 'security/process education only; no real tickers, prices, P&L, profit promises, signal claims, broker UI, or exchange logos',
        'journal_rule': 'no Better Traders Journal cover used or composited in this carousel',
        'review_gate': 'review-only; not scheduled'
    }
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('CONTACT', contact)
for p in exports:
    print('SLIDE', p)
print('MANIFEST', out / 'manifest.json')
