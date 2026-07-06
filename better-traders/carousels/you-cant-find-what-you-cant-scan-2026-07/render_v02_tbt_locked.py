from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/you-cant-find-what-you-cant-scan-2026-07')
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
    if pix is None:
        raise RuntimeError('Could not access overlay pixels')
    for y in range(h):
        for x in range(w):
            left = max(0, 1 - x / 705)
            top = max(0, 1 - y / 555)
            bottom = max(0, (y - 850) / 235)
            a = min(242, int(204 * left + 54 * top + 105 * bottom))
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
                draw.text((x + 3, y + 3), line, font=ft, fill=(0, 0, 0, 185))
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
    1: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_130441_b1a43ec6.png'),
    2: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_130625_fd2a1ca5.png'),
    3: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_134030_b9eab7ce.png'),
    4: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_134141_1a95ed7e.png'),
    5: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_134229_d02e24a3.png'),
    6: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_134346_fa13b650.png'),
    7: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260706_134450_6e97bd93.png'),
}

cfg = {
    1: ('YOU HAVE\nMEMORIZED\nSIX CHARTS', 'You open the same few\ncharts every day.\nStaring harder does not\ncreate a setup.', 70, 164, 52, 27, 650),
    2: ('Flat is not\na setup', 'Some days your watchlist\nis just quiet. No trigger.\nNo structure. No reason.', 70, 178, 61, 28, 650),
    3: ('Boredom writes\nbad trades', 'When there is nothing\nto do, your brain starts\ninventing something.', 70, 174, 58, 28, 670),
    4: ('The setup might\nbe somewhere else', 'Real candidates can form\non charts you never open.\nYou cannot study what\nyou never see.', 70, 166, 54, 27, 700),
    5: ('Scan by rules,\nnot mood', 'The Better Crypto Scanner\nfilters the market by your\ncriteria. It finds candidates,\nnot winners.', 70, 168, 56, 26, 690),
    6: ('Stop hunting.\nStart filtering.', 'Hunting is emotional.\nFiltering gives you a\nshorter list to actually\nstudy.', 70, 170, 58, 27, 670),
    7: ('Find candidates.\nDo the work.', 'Use the Better Crypto Scanner\nand TBT Volume Converter\nto narrow the field, then\nbring your plan. That is\nhow The Better Traders\nbuild process.', 70, 156, 54, 24, 720),
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
    dest = out / f'tbt-you-cant-find-what-you-cant-scan-slide-{n:02d}-{VERSION}-review.png'
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
contact = out / f'tbt-you-cant-find-what-you-cant-scan-contact-sheet-{VERSION}-review.png'
sheet.save(contact, quality=95)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    'title': "You Can't Find What You Can't Scan",
    'status': 'REVIEW READY',
    'review_only': True,
    'scheduled': False,
    'created_at': datetime.now(timezone.utc).isoformat(),
    'lead': 'THEO',
    'style_lock': '/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-almost-chased-2026-06/v29-aaron-text-logo-swipe-fix/',
    'copy_gate': 'Claude Opus copy pass completed; Hermes tightened overlay copy, preserved exact The Better Traders brand name, and enforced scanner finds candidates not winners compliance.',
    'slides': [{'path': str(p), 'sha256': sha256(p), 'dimensions': Image.open(p).size} for p in exports],
    'contact_sheet': str(contact),
    'qa': {
        'dimensions': 'all slides exported 1080x1080; contact sheet rendered',
        'logo': 'transparent stacked TBT logo only on slide 1 and slide 7',
        'nav': 'bottom counter and dots on all slides; Swipe -> omitted on final slide',
        'compliance': 'Better Crypto Scanner/TBT Volume Converter education; no real tickers, prices, P&L, broker UI, profit claims, signal guarantees, or winner claims',
        'journal_rule': 'no Better Traders Journal cover used or composited in this carousel',
        'review_gate': 'review-only; not scheduled'
    }
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('CONTACT', contact)
for p in exports:
    print('SLIDE', p)
print('MANIFEST', out / 'manifest.json')
