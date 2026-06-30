from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/bot-doesnt-get-bored-2026-06')
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
            left = max(0, 1 - x / 720)
            top = max(0, 1 - y / 540)
            bottom = max(0, (y - 850) / 235)
            a = min(230, int(186 * left + 50 * top + 94 * bottom))
            pix[x, y] = (0, 4, 10, a)
    return Image.alpha_composite(im, ov)


def paste_logo(im):
    logo = logo_src.copy()
    tw = 140
    logo = logo.resize((tw, int(logo.height * tw / logo.width)), Image.Resampling.LANCZOS)
    im.alpha_composite(logo, (54, 56))


def draw_wrapped(d, text, x, y, maxw, ft, fill, leading=5, shadow=True):
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
    for line in lines:
        if line:
            if shadow:
                d.text((x + 3, y + 3), line, font=ft, fill=(0, 0, 0, 175))
            d.text((x, y), line, font=ft, fill=fill)
            bb = d.textbbox((x, y), line, font=ft)
            y += bb[3] - bb[1] + leading
        else:
            y += int(ft.size * 0.55)
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
    1: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260630_130233_b96e6db1.png'),
    2: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260630_130614_dc925a17.png'),
    3: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260630_131005_12ecc25f.png'),
    4: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260630_131350_1fd0d5e6.png'),
    5: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260630_131739_eacc645c.png'),
    6: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260630_131920_d48fab85.png'),
    7: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260630_132036_3f1b646c.png'),
}

cfg = {
    1: ('YOU WALKED\nAWAY', 'You stepped away from\nthe screen. Real life\ncalled, so you answered.', 70, 185, 60, 28, 660),
    2: ('It fired\nanyway', 'Your setup triggered\nwithout you watching.\nThe plan ran on schedule.', 70, 188, 60, 28, 660),
    3: ('You are\nonly human', 'Theo still needs sleep,\nlunch, and a life away\nfrom the desk.', 70, 188, 60, 28, 660),
    4: ('The bot does\nnot get bored', 'No fatigue. No second\nguessing. No itch to\nact early.', 70, 180, 57, 28, 675),
    5: ('It follows\nyour rules', 'A bot only does what\nyou told it to do.\nNothing more, nothing less.', 70, 188, 59, 28, 660),
    6: ('Not lazy.\nConsistent.', 'Automation is not\nskipping the work.\nIt is repeating it the\nsame way every time.', 70, 188, 60, 27, 660),
    7: ('You make\nthe call', 'Automate the repetition.\nThe judgment stays\nwith you, at The Better\nTraders.', 70, 174, 59, 27, 660),
}

exports = []
for n, (title, body, x, y, ts, bs, maxw) in cfg.items():
    if not bases[n].exists():
        raise FileNotFoundError(bases[n])
    im = Image.open(bases[n]).convert('RGB').resize((1080, 1080), Image.Resampling.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(1.05).convert('RGBA')
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
    dest = out / f'tbt-bot-doesnt-get-bored-slide-{n:02d}-{VERSION}-review.png'
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
contact = out / f'tbt-bot-doesnt-get-bored-contact-sheet-{VERSION}-review.png'
sheet.save(contact, quality=95)

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

manifest = {
    'title': 'The Bot Does Not Get Bored',
    'status': 'REVIEW READY',
    'review_only': True,
    'scheduled': False,
    'created_at': datetime.now(timezone.utc).isoformat(),
    'lead': 'THEO',
    'style_lock': '/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-almost-chased-2026-06/v29-aaron-text-logo-swipe-fix/',
    'copy_gate': 'Claude Opus copy pass completed; Hermes enforced The Better Traders brand name and compliance constraints.',
    'slides': [{'path': str(p), 'sha256': sha256(p), 'dimensions': Image.open(p).size} for p in exports],
    'contact_sheet': str(contact),
    'qa': {
        'dimensions': 'all slides exported 1080x1080; contact sheet rendered',
        'logo': 'transparent stacked TBT logo only on slide 1 and slide 7',
        'nav': 'bottom counter and dots on all slides; Swipe -> omitted on final slide',
        'compliance': 'education on automation discipline; no real tickers, prices, P&L, broker UI, profit claims, or signal claims',
        'journal_rule': 'no Better Traders Journal cover used or composited in this carousel',
        'review_gate': 'review-only; not scheduled'
    }
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('CONTACT', contact)
for p in exports:
    print('SLIDE', p)
print('MANIFEST', out / 'manifest.json')
