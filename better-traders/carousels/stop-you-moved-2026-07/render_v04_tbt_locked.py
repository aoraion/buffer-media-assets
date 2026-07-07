from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/stop-you-moved-2026-07')
VERSION = 'v04'
out = root / f'{VERSION}-review-pack'
out.mkdir(parents=True, exist_ok=True)

GILROY_XB = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Extrabold.ttf'
GILROY_REG = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Regular.ttf'
GILROY_BOLD = '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Bold.ttf'
HAND_FONT = '/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf'
WHITE = (246, 248, 251, 255)
BODY = (234, 239, 243, 255)
TEAL = (0, 230, 198, 255)
logo_src = Image.open('/Users/bettybot/clawd/TBT-logos/TBT Logo/White text/The better traders 1_text white.png').convert('RGBA')


def font(size, kind='xb'):
    return ImageFont.truetype({'xb': GILROY_XB, 'bold': GILROY_BOLD, 'reg': GILROY_REG}[kind], size)


def hand_font(size):
    return ImageFont.truetype(HAND_FONT, size)


def draw_handwritten_rule(im):
    """Draw Dani's journal rule as handwritten page ink, not typed overlay."""
    text = 'I honor my stop.'
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ink = (38, 28, 20, 232)
    x, y = 615, 552
    # Bradley Hand + a tiny rotation + imperfect underline reads as journal handwriting.
    d.text((x, y), text, font=hand_font(38), fill=ink)
    uy = y + 45
    pts = [(x, uy), (x + 70, uy + 2), (x + 150, uy - 1), (x + 230, uy + 2), (x + 310, uy)]
    for offset in (0, 2):
        d.line([(px, py + offset) for px, py in pts], fill=(34, 24, 17, 220), width=2, joint='curve')
    layer = layer.rotate(-1.8, center=(810, 605), resample=Image.Resampling.BICUBIC)
    return Image.alpha_composite(im, layer)


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
    1: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260707_145534_4bded00a.png'),
    2: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260707_145653_9cb45f30.png'),
    3: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260707_150657_7b65ddd1.png'),
    4: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260707_160529_9de5c49f.png'),
    5: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260707_150223_5afc930e.png'),
    6: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260707_160659_9b884597.png'),
    7: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260707_150503_7a8089c5.png'),
}

cfg = {
    1: ('THE STOP\nYOU MOVED', 'Dani set her risk line\nbefore she entered.\nThen the market walked\nright up to it.', 70, 158, 62, 26, 660),
    2: ('The line\nwas clear', 'Before the trade,\nthe plan felt obvious.\nThis price proves the\nidea wrong. Exit here.', 70, 168, 60, 26, 660),
    3: ('Then the candle\ngot close', 'Price crept toward\nher stop. Her hand\nhovered. Just give it\nmore room.', 70, 166, 58, 26, 670),
    4: ('What moving it\nreally does', 'Sliding the stop does\nnot save the trade.\nIt only delays the\ndecision already made.', 70, 160, 56, 26, 700),
    5: ('The honest\nquestion', 'Is the idea still valid,\nor does she just want\nto be right? The line\nanswers that.', 70, 170, 58, 26, 680),
    6: ('She wrote\nthe rule', 'My invalidation is set\nbefore I enter. I do\nnot move it wider\nonce I am in.', 70, 168, 60, 26, 675),
    7: ('Calmer\nfrom here', 'The decision was made\nbefore the candle arrived.\nDani follows her plan\nand studies the process\nat The Better Traders.', 70, 148, 61, 25, 730),
}

exports = []
for n, (title, body, x, y, title_size, body_size, maxw) in cfg.items():
    if not bases[n].exists():
        raise FileNotFoundError(bases[n])
    im = Image.open(bases[n]).convert('RGB').resize((1080, 1080), Image.Resampling.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(1.04).convert('RGBA')
    im = add_gradient(im)
    if n == 6:
        # Aaron specifically requested a real, legible journal sentence here,
        # not typed overlay or AI scribbles. Use a handwriting font and rough underline.
        im = draw_handwritten_rule(im)
    if n in (1, 7):
        paste_logo(im)
    draw = ImageDraw.Draw(im)
    yy = draw_wrapped_fixed(draw, title, x, y, maxw, font(title_size, 'xb'), WHITE, line_height=int(title_size * 1.02))
    yy += 22
    draw_wrapped_fixed(draw, body, x, yy, maxw, font(body_size, 'reg'), BODY, line_height=int(body_size * 1.22))
    nav(draw, n)
    if n == 7:
        draw.text((70, 1052), 'Educational content only. Not financial advice.', font=font(12, 'reg'), fill=(210, 220, 225, 230))
    dest = out / f'tbt-stop-you-moved-slide-{n:02d}-{VERSION}-review.png'
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
contact = out / f'tbt-stop-you-moved-contact-sheet-{VERSION}-review.png'
sheet.save(contact, quality=95)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    'title': 'The Stop You Moved',
    'status': 'REVIEW READY',
    'review_only': True,
    'scheduled': False,
    'created_at': datetime.now(timezone.utc).isoformat(),
    'lead': 'DANI',
    'style_lock': '/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-almost-chased-2026-06/v29-aaron-text-logo-swipe-fix/',
    'copy_gate': 'Claude Worker creative-director feedback incorporated before rerender; v04 applies Aaron note to redo slide 06 as handwriting, not typed overlay. Slide 04 remains the v03 over-shoulder decision angle.',
    'base_images': {str(k): str(v) for k, v in bases.items()},
    'slides': [{'path': str(p), 'sha256': sha256(p), 'dimensions': Image.open(p).size} for p in exports],
    'contact_sheet': str(contact),
    'qa': {
        'dimensions': 'all slides exported 1080x1080; contact sheet rendered',
        'logo': 'transparent stacked TBT logo only on slide 1 and slide 7',
        'nav': 'bottom counter and dots on all slides; Swipe -> omitted on final slide',
        'visuals': 'Dani remains the protagonist; v04 keeps v03 slide 04 and replaces slide 06 typed-looking journal line with handwriting-styled ink and a rough hand-drawn underline: I honor my stop.',
        'compliance': 'risk/process education only; no real tickers, prices, P&L, broker UI, profit claims, or signal guarantees',
        'journal_rule': 'no Better Traders Journal cover used or composited; notebook pages are generic process props',
        'review_gate': 'review-only; not scheduled'
    }
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('CONTACT', contact)
for p in exports:
    print('SLIDE', p)
print('MANIFEST', out / 'manifest.json')
