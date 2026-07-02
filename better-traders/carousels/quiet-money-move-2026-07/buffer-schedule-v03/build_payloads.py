#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path
from PIL import Image

root = Path('/Users/bettybot/clawd/buffer-media-assets/better-traders/carousels/quiet-money-move-2026-07')
out = root / 'buffer-schedule-v03'
out.mkdir(parents=True, exist_ok=True)
branch = 'tbt-quiet-money-move-20260702-v03'
base_raw = f'https://raw.githubusercontent.com/aoraion/buffer-media-assets/{branch}/better-traders/carousels/quiet-money-move-2026-07/v03-review-pack'
caption = (
    "Profit is not finished just because the trade closed green.\n\n"
    "A win still has to be protected. If every dollar stays exposed by default, one rough move can quietly pull the progress back into the market.\n\n"
    "Sometimes the quiet move is stepping aside first. Preserve the gain, let the emotion settle, then redeploy only when the next setup actually deserves the capital.\n\n"
    "Stablecoins are not a promise and not risk free. They are simply one tool traders may use to pause, think clearly, and avoid forcing the next trade.\n\n"
    "Educational content only. Not financial advice.\n\n"
    "#TheBetterTraders #CryptoTrading #TradingEducation #TradingPlan"
)
slides = []
for i in range(1,8):
    local = root / 'v03-review-pack' / f'tbt-quiet-money-move-slide-{i:02d}-v03-review.png'
    im = Image.open(local)
    assert im.size == (1080,1080), (local, im.size)
    url = f'{base_raw}/tbt-quiet-money-move-slide-{i:02d}-v03-review.png'
    req = urllib.request.Request(url, method='HEAD')
    with urllib.request.urlopen(req, timeout=20) as r:
        assert 200 <= r.status < 300, (url, r.status)
        ctype = r.headers.get('content-type','')
        assert 'image' in ctype or 'octet-stream' in ctype, (url, ctype)
    slides.append({
        "image": {
            "url": url,
            "metadata": {
                "altText": f"The Quiet Money Move carousel slide {i} of 7",
                "dimensions": {"width": 1080, "height": 1080}
            }
        }
    })

common = {
    "schedulingType": "automatic",
    "mode": "addToQueue",
    "text": caption,
    "assets": slides,
    "source": "hermes-tbt-quiet-money-move-carousel-v03",
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
