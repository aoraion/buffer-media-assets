from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/plan-you-never-wrote-down-2026-07')
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


def font(size, kind='xb'):
    return ImageFont.truetype({'xb': GILROY_XB, 'bold': GILROY_BOLD, 'reg': GILROY_REG}[kind], size)


def add_gradient(im):
    w, h = im.size
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pix = ov.load()
    if pix is None:
        raise RuntimeError('Could not access overlay pixels')
    for y in range(h):
        for x in range(w):
            left = max(0, 1 - x / 710)
            top = max(0, 1 - y / 560)
            bottom = max(0, (y - 850) / 235)
            a = min(244, int(210 * left + 56 * top + 108 * bottom))
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
        words = raw.split()
        if not words:
            lines.append('')
            continue
        cur = ''
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


def draw_wrapped_fixed(draw, text, x, y, maxw, ft, fill, line_height=None, shadow=True):
    lines = wrap_text(draw, text, maxw, ft)
    if line_height is None:
        line_height = int(ft.size * 1.08)
    for line in lines:
        if line:
            if shadow:
                draw.text((x + 3, y + 3), line, font=ft, fill=(0, 0, 0, 190))
            draw.text((x, y), line, font=ft, fill=fill)
        y += line_height
    return y


def nav(draw, n):
    y = 1018
    draw.text((70, y), f'{n:02d}', font=font(18, 'bold'), fill=TEAL)
    cx = 540
    cy = y + 9
    r = 5
    sp = 22
    for i in range(7):
        col = TEAL if i == n - 1 else WHITE
        x = cx + (i - 3) * sp
        draw.ellipse((x - r, cy - r, x + r, cy + r), fill=col)
    if n != 7:
        draw.text((930, y), 'Swipe ->', font=font(18, 'bold'), fill=TEAL)


bases = {
    1: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_191020_61b19c49.png'),
    2: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_191140_02f423f6.png'),
    3: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_191259_7bef8aab.png'),
    4: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_191421_d28e08be.png'),
    5: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_191719_26ffe7db.png'),
    6: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_192026_7b3007d1.png'),
    7: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_192142_ec0b28d5.png'),
}

cfg = {
    1: ('"I HAVE\nA PLAN"', 'Most traders say this.\nAsk them to show it,\nand the room gets quiet.', 70, 166, 62, 27, 650),
    2: ('But it changes\nevery trade', 'A wider stop here.\nOne more entry there.\nIf it bends every time,\nit was not a plan.', 70, 174, 59, 27, 660),
    3: ('Entry rules.\nExit rules.\nRisk rules.', 'When you get in,\nwhen you get out,\nand how much is on\nthe line. Write all three.', 70, 158, 58, 26, 670),
    4: ('If it is not\nwritten, it is\nnegotiable', 'A rule in your head can\nbe talked out of fast.\nA rule on the page\nargues back.', 70, 154, 54, 26, 690),
    5: ('Calm-you\nwrites the rules', 'Before the session.\nClear-headed. Honest.\nThis version thinks in\nprocess, not impulse.', 70, 166, 57, 27, 670),
    6: ('Emotional-you\nfollows them', 'Mid-trade, heart racing,\ntempted to improvise.\nThat version does not\nget a vote.', 70, 170, 57, 27, 670),
    7: ('Plan it. Trade it.\nReview it. Repeat.', 'That loop is the job.\nIf you want a repeatable\nprocess, that is what\nwe work on at\nThe Better Traders.', 70, 152, 51, 25, 720),
}

exports = []
for n, (title, body, x, y, title_size, body_size, maxw) in cfg.items():
    if not bases[n].exists():
        raise FileNotFoundError(bases[n])
    im = Image.open(bases[n]).convert('RGB').resize((1080, 1080), Image.Resampling.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(1.04).convert('RGBA')
    im = add_gradient(im)
    if n in (1, 7):
        paste_logo(im)
    draw = ImageDraw.Draw(im)
    yy = draw_wrapped_fixed(draw, title, x, y, maxw, font(title_size, 'xb'), WHITE, line_height=int(title_size * 1.02))
    yy += 22
    draw_wrapped_fixed(draw, body, x, yy, maxw, font(body_size, 'reg'), BODY, line_height=int(body_size * 1.22))
    nav(draw, n)
    if n == 7:
        draw.text((70, 1052), 'Educational content only. Not financial advice.', font=font(12, 'reg'), fill=(210, 220, 225, 230))
    dest = out / f'tbt-plan-you-never-wrote-down-slide-{n:02d}-{VERSION}-review.png'
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
contact = out / f'tbt-plan-you-never-wrote-down-contact-sheet-{VERSION}-review.png'
sheet.save(contact, quality=95)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    'title': 'The Plan You Never Wrote Down',
    'status': 'REVIEW READY',
    'review_only': True,
    'scheduled': False,
    'created_at': datetime.now(timezone.utc).isoformat(),
    'lead': 'JESS',
    'style_lock': '/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-almost-chased-2026-06/v29-aaron-text-logo-swipe-fix/',
    'copy_gate': 'Claude Opus copy pass completed; Hermes tightened overlay copy, preserved exact The Better Traders brand name, and kept all claims educational/process-only.',
    'base_images': {str(k): str(v) for k, v in bases.items()},
    'slides': [{'path': str(p), 'sha256': sha256(p), 'dimensions': Image.open(p).size} for p in exports],
    'contact_sheet': str(contact),
    'qa': {
        'dimensions': 'all slides exported 1080x1080; contact sheet rendered',
        'logo': 'transparent stacked TBT logo only on slide 1 and slide 7',
        'nav': 'bottom counter and dots on all slides; Swipe -> omitted on final slide',
        'visuals': 'Jess remains the protagonist with varied angles and process/emotion beats across the story',
        'compliance': 'trading plan/process education only; no real tickers, prices, P&L, broker UI, profit claims, or signal guarantees',
        'journal_rule': 'no Better Traders Journal cover used or composited; plan pages are generic/open process props',
        'review_gate': 'review-only; not scheduled'
    }
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('CONTACT', contact)
for p in exports:
    print('SLIDE', p)
print('MANIFEST', out / 'manifest.json')
