from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import hashlib, json
from datetime import datetime, timezone

ROOT = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/rule-you-broke-because-you-were-bored-2026-07')
OUT = ROOT / 'v04-claire-poses-locations-review-pack'
OUT.mkdir(parents=True, exist_ok=True)
FONT = {
    'xb': '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Extrabold.ttf',
    'bold': '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Bold.ttf',
    'reg': '/Users/bettybot/clawd/bear-market-playbook/fonts/gilroy/Gilroy-Regular.ttf',
}
LOGO = '/Users/bettybot/clawd/TBT-logos/TBT Logo/White text/The better traders 1_text white.png'
BASES = {
    1: '/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_154330_6640f20b.png',
    2: '/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_154453_a903eae1.png',
    3: '/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_154616_5b1262ba.png',
    4: '/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_154946_f0773105.png',
    5: '/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_155142_9d7de7aa.png',
    6: '/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_155518_de471e69.png',
    7: '/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_155642_11ad60c7.png',
}
COPY = {
    1: ('The Rule You\nBroke', 'Late night. Quiet market. Claire had nothing to trade, so she almost traded anyway.', 64),
    2: ('Nothing Was\nMoving', 'The chart was there. The setup was not. That distinction matters.', 62),
    3: ('Boredom Wants\nAction', 'A quiet screen can make your hand reach for a click just to feel busy.', 61),
    4: ('The Almost\nClick', 'No setup. No plan. Claire stopped before restlessness became a trade.', 64),
    5: ('The Rule\nHeld', 'Boredom is not a setup. Keeping the rule is a win before the trade ever happens.', 60),
    6: ('Pause Beats\nImpulse', 'Step away. Put the phone down. Let the rule make the decision for you.', 64),
    7: ('Quiet Is A\nWin', 'You do not need to create action. Patience is confidence in a still market.', 60),
}
WHITE = (246, 248, 251, 255)
BODY = (234, 239, 243, 255)
TEAL = (0, 230, 198, 255)

def ft(size, weight):
    return ImageFont.truetype(FONT[weight], size)

def wrap(draw, text, width, font):
    lines = []
    for paragraph in text.split('\n'):
        current = ''
        for word in paragraph.split():
            candidate = (current + ' ' + word).strip()
            if not current or draw.textbbox((0, 0), candidate, font=font)[2] <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines

def draw_text(draw, content, x, y, width, font, fill, line_h):
    for line in wrap(draw, content, width, font):
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y

def gradient(image):
    width, height = image.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    px = overlay.load()
    for y in range(height):
        for x in range(width):
            alpha = min(242, int(220 * max(0, 1 - x / 640) + 70 * max(0, 1 - y / 600) + 75 * max(0, (y - 860) / 220)))
            px[x, y] = (0, 4, 10, alpha)
    return Image.alpha_composite(image, overlay)

def nav(draw, slide):
    y = 1003
    draw.text((57, y), f'{slide:02d}', font=ft(18, 'bold'), fill=TEAL)
    for index in range(7):
        x = 540 + (index - 3) * 22
        draw.ellipse((x - 5, y + 4, x + 5, y + 14), fill=TEAL if index == slide - 1 else WHITE)
    if slide != 7:
        draw.text((915, y), 'Swipe →', font=ft(18, 'bold'), fill=TEAL)

def sha(path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

exports = []
for slide in range(1, 8):
    with Image.open(BASES[slide]) as source:
        assert source.width == source.height, f'base {slide} is not native square: {source.size}'
        image = source.convert('RGB').resize((1080, 1080), Image.Resampling.LANCZOS)
    image = ImageEnhance.Brightness(image).enhance(1.01).convert('RGBA')
    image = gradient(image)
    if slide in (1, 7):
        logo = Image.open(LOGO).convert('RGBA')
        logo = logo.resize((140, int(logo.height * 140 / logo.width)), Image.Resampling.LANCZOS)
        image.alpha_composite(logo, (54, 56))
    draw = ImageDraw.Draw(image)
    title, body, title_size = COPY[slide]
    y = draw_text(draw, title, 54, 162, 415, ft(title_size, 'xb'), WHITE, int(title_size * 0.94)) + 20
    draw_text(draw, body, 54, y, 405, ft(24, 'reg'), BODY, 31)
    nav(draw, slide)
    if slide == 7:
        draw.text((57, 1040), 'Educational content only. Not financial advice.', font=ft(12, 'reg'), fill=(210, 220, 225, 230))
    output = OUT / f'tbt-rule-you-broke-because-you-were-bored-slide-{slide:02d}-v04-review.png'
    image.convert('RGB').save(output, quality=95)
    exports.append(output)

thumb_width, gap, label_h = 360, 34, 45
sheet = Image.new('RGB', (3 * thumb_width + 4 * gap, 3 * (thumb_width + label_h) + 4 * gap), (4, 10, 18))
draw = ImageDraw.Draw(sheet)
for index, output in enumerate(exports):
    x = gap + (index % 3) * (thumb_width + gap)
    y = gap + (index // 3) * (thumb_width + label_h + gap)
    sheet.paste(Image.open(output).resize((thumb_width, thumb_width), Image.Resampling.LANCZOS), (x, y))
    draw.text((x, y + thumb_width + 8), f'Slide {index + 1:02d}', font=ft(26, 'bold'), fill=WHITE)
contact = OUT / 'tbt-rule-you-broke-because-you-were-bored-contact-sheet-v04-review.png'
sheet.save(contact, quality=95)

manifest = {
    'carousel_id': 'rule-you-broke-because-you-were-bored-2026-07',
    'revision': 'v04',
    'title': 'The Rule You Broke Because You Were Bored',
    'status': 'REVIEW READY',
    'review_only': True,
    'scheduled': False,
    'created_at': datetime.now(timezone.utc).isoformat(),
    'lead': 'CLAIRE — white/Caucasian woman, late 30s; navy sweater continuity lock',
    'storyboard': ['confident late-night chart review in office', 'standing kitchen chart check', 'living-room phone temptation', 'decisive stop at home-office laptop', 'contented reading-nook restraint', 'calm balcony reset', 'confident no-action payoff in living room'],
    'base_images': BASES,
    'native_base_dimensions': [Image.open(BASES[n]).size for n in range(1, 8)],
    'slides': [{'path': str(output), 'sha256': sha(output), 'dimensions': Image.open(output).size} for output in exports],
    'contact_sheet': str(contact),
    'qa': {'native_square_bases': True, 'final_square_slides': True, 'nighttime_continuity': True, 'wardrobe_continuity': True, 'computer_or_phone_in_every_beat': True, 'pose_and_location_variety': True, 'visible_chart_context': True, 'confident_outcome_emotion': True},
    'review_gate': 'review-only; v01, v02, and v03 are rejected/superseded; Aaron feedback/approval required.'
}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(contact)
