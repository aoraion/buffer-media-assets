from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/rule-you-broke-because-you-were-bored-2026-07')
OUT = ROOT / 'v04-claire-poses-locations-review-pack'
OUT.mkdir(parents=True, exist_ok=True)
BASES = [
    Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_154330_6640f20b.png'),
    Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_154453_a903eae1.png'),
    Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_154616_5b1262ba.png'),
    Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_154946_f0773105.png'),
    Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_155142_9d7de7aa.png'),
    Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_155518_de471e69.png'),
    Path('/Users/bettybot/.hermes/cache/images/openai_codex_gpt-image-2-medium_20260721_155642_11ad60c7.png'),
]
for base in BASES:
    with Image.open(base) as image:
        assert image.width == image.height, f'Non-square base: {base} = {image.size}'

w, gap, label_h = 360, 24, 44
sheet = Image.new('RGB', (3 * w + 4 * gap, 3 * (w + label_h) + 4 * gap), (5, 10, 17))
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
for i, base in enumerate(BASES):
    image = Image.open(base).convert('RGB').resize((w, w), Image.Resampling.LANCZOS)
    x = gap + (i % 3) * (w + gap)
    y = gap + (i // 3) * (w + label_h + gap)
    sheet.paste(image, (x, y))
    draw.text((x, y + w + 9), f'BASE {i + 1:02d}', font=font, fill=(246, 248, 251))
sheet.save(OUT / 'base-contact-sheet-v04.png', quality=95)
print('\n'.join(f'{i + 1}: {Image.open(base).size} {base}' for i, base in enumerate(BASES)))
print(OUT / 'base-contact-sheet-v04.png')
