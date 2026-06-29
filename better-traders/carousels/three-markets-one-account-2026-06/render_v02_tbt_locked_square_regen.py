from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path
import json
from datetime import datetime

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/three-markets-one-account-2026-06')
out = root / 'v02-square-regeneration-review-pack'
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
            left = max(0, 1 - x / 710)
            top = max(0, 1 - y / 520)
            bottom = max(0, (y - 850) / 235)
            a = min(224, int(178 * left + 52 * top + 94 * bottom))
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
    1: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260629_133230_655472d8.png'),
    2: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260629_133544_b43b6486.png'),
    3: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260629_133858_b4c759cc.png'),
    4: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260629_134234_365fbbc5.png'),
    5: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260629_134553_bb764697.png'),
    6: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260629_134932_e81fb0a4.png'),
    7: Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260629_150729_999c1968.png'),
}

cfg = {
    1: ('THE EASY\nMONTHS', 'When the market runs up,\nalmost any plan looks smart.\nJess thought she had it\nfigured out.', 70, 185, 58, 27, 640),
    2: ('Same plan,\ndifferent weather', 'Then the market turned down.\nThe exact moves that felt\neasy started to hurt.', 70, 188, 56, 28, 660),
    3: ('The chop', 'A sideways market does not\ncrash or climb. It just\ngrinds, and it punishes\nimpatience.', 70, 192, 61, 28, 650),
    4: ('Three moods', 'Up, down, and sideways.\nThe market is always in\none of them, and it does\nnot ask permission.', 70, 188, 60, 28, 650),
    5: ('One plan\nproblem', 'Most people learn one way\nto trade, then run it in\nevery condition and wonder\nwhy it breaks.', 70, 190, 58, 27, 660),
    6: ('Right tool,\nright weather', 'Different conditions ask\nfor different tools.\nKnowing which one fits is\nthe actual skill.', 70, 188, 57, 28, 660),
    7: ('The Better\nTraders', 'Our courses teach you\nhow to read the conditions\nand trade with a plan in\nany market.', 70, 178, 59, 28, 660),
}

exports = []
for n, (title, body, x, y, ts, bs, maxw) in cfg.items():
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
    dest = out / f'tbt-three-markets-one-account-slide-{n:02d}-v02-square-review.png'
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
contact = out / 'tbt-three-markets-one-account-contact-sheet-v02-square-review.png'
sheet.save(contact, quality=95)
manifest = {
    'title': 'Three Markets, One Account',
    'status': 'REVIEW READY - V02 SQUARE REGENERATION',
    'review_only': True,
    'scheduled': False,
    'created_at': datetime.utcnow().isoformat() + 'Z',
    'revision_note': 'V02 regenerated all base images natively as 1:1 square; slide 5 desk cards made explicit/clear per Aaron feedback.',
    'lead': 'JESS',
    'style_lock': '/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/trade-almost-chased-2026-06/v29-aaron-text-logo-swipe-fix/',
    'slides': [str(p) for p in exports],
    'contact_sheet': str(contact),
    'qa': {
        'dimensions': 'all generated bases are native square 1024x1024; exports are 1080x1080',
        'logo': 'transparent stacked TBT logo only on slide 1 and slide 7',
        'nav': 'bottom counter and dots on all slides; Swipe -> omitted on final slide',
        'compliance': 'educational market-conditions framing; no real tickers, prices, P&L, broker UI, profit claims, or signal claims',
        'copy_gate': 'Claude Opus copy pass completed; Hermes enforced brand/compliance constraints',
        'journal_rule': 'no Better Traders Journal cover used or composited in this carousel',
        'aaron_feedback': 'corrected non-square prompt issue; slide 5 now shows clear strategy/weather cards instead of vague filler'
    }
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print('CONTACT', contact)
for p in exports:
    print('SLIDE', p)
print('MANIFEST', out / 'manifest.json')
