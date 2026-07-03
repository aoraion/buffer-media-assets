#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path
from PIL import Image

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/15-minute-setup-skipped-2026-07')
out = root / 'buffer-schedule-v01'
out.mkdir(parents=True, exist_ok=True)
branch = 'tbt-15-minute-setup-skipped-20260703-v01'
base_raw = f'https://raw.githubusercontent.com/aoraion/buffer-media-assets/{branch}/better-traders/carousels/15-minute-setup-skipped-2026-07/v01-review-pack'
caption = (
    "The most expensive trading shortcut is usually the boring one you skipped.\n\n"
    "Passwords. 2FA. API permissions. Terminal layout. None of it feels exciting when the chart is moving, but that foundation matters most when pressure hits.\n\n"
    "Set it up before you need it. Limit access, keep the workspace clean, and make the first fifteen minutes protect every session after it.\n\n"
    "Educational content only. Not financial advice.\n\n"
    "#TheBetterTraders #CryptoTrading #TradingEducation #TradingPlan"
)
slides = []
for i in range(1, 8):
    local = root / 'v01-review-pack' / f'tbt-15-minute-setup-skipped-slide-{i:02d}-v01-review.png'
    im = Image.open(local)
    assert im.size == (1080, 1080), (local, im.size)
    url = f'{base_raw}/tbt-15-minute-setup-skipped-slide-{i:02d}-v01-review.png'
    req = urllib.request.Request(url, method='HEAD')
    with urllib.request.urlopen(req, timeout=20) as r:
        assert 200 <= r.status < 300, (url, r.status)
        ctype = r.headers.get('content-type', '')
        assert 'image' in ctype or 'octet-stream' in ctype, (url, ctype)
    slides.append({
        "image": {
            "url": url,
            "metadata": {
                "altText": f"The 15-Minute Setup You Skipped carousel slide {i} of 7",
                "dimensions": {"width": 1080, "height": 1080}
            }
        }
    })

common = {
    "schedulingType": "automatic",
    "mode": "addToQueue",
    "text": caption,
    "assets": slides,
    "source": "hermes-tbt-15-minute-setup-carousel-v01",
    "aiAssisted": False,
}
payloads = {
    'instagram': {
        **common,
        "channelId": "69d8a6b3031bfa423ceb17b5",
        "metadata": {"instagram": {"type": "post", "shouldShareToFeed": True}},
    },
    'facebook': {
        **common,
        "channelId": "69d8a6e8031bfa423ceb1857",
        "metadata": {"facebook": {"type": "post"}},
    },
}
for name, payload in payloads.items():
    (out / f'payload-{name}.json').write_text(json.dumps(payload, indent=2))
asset_manifest = {
    "repository": "https://github.com/aoraion/buffer-media-assets.git",
    "branch": branch,
    "raw_urls_verified": len(slides),
    "dimensions": "1080x1080 each",
    "assets": [s['image']['url'] for s in slides],
}
(out / 'asset-manifest.json').write_text(json.dumps(asset_manifest, indent=2))
print(json.dumps(asset_manifest, indent=2))
