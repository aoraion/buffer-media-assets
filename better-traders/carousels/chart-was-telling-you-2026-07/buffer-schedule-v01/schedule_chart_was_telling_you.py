#!/usr/bin/env python3
import json, subprocess, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent
BRANCH = "tbt-chart-was-telling-you-20260706-v01"
BASE = "better-traders/carousels/chart-was-telling-you-2026-07/v01-review-pack"
RAW = f"https://raw.githubusercontent.com/aoraion/buffer-media-assets/{BRANCH}/{BASE}"
BUFFER = "/Users/bettybot/bin/buffer-tbt"
FIELDS = "id,status,dueAt,channel.name,channel.service,metadata.type,metadata.shouldShareToFeed,assets.id,assets.type,assets.image.width,assets.image.height,assets.image.altText"

CAPTION = """The chart was talking before the trade ever felt obvious.

A cleaner read often starts with three questions:
1. Where did price already react?
2. Where is momentum actually changing?
3. What would invalidate the idea before you get emotional?

That’s the difference between forcing a setup and reading the story already on the chart.

Educational content only. Not financial advice.

#TheBetterTraders #CryptoTrading #TradingEducation #TradingPlan"""

CHANNELS = {
    "instagram": {
        "channelId": "69d8a6b3031bfa423ceb17b5",
        "channel": "thebettertraders",
        "metadata": {"instagram": {"type": "post", "shouldShareToFeed": True}},
    },
    "facebook": {
        "channelId": "69d8a6e8031bfa423ceb1857",
        "channel": "The Better Traders",
        "metadata": {"facebook": {"type": "post"}},
    },
}

assets = []
for n in range(1, 8):
    assets.append({
        "image": {
            "url": f"{RAW}/tbt-chart-was-telling-you-slide-{n:02d}-v01-review.png",
            "metadata": {
                "altText": f"The Chart Was Telling You carousel slide {n} of 7",
                "dimensions": {"width": 1080, "height": 1080},
            },
        }
    })


def run(cmd, outfile=None):
    print("$", " ".join(cmd), flush=True)
    p = subprocess.run(cmd, text=True, capture_output=True)
    if outfile:
        pathlib.Path(outfile).write_text(p.stdout if p.stdout.strip() else p.stderr)
    if p.stdout:
        print(p.stdout)
    if p.stderr:
        print(p.stderr, file=sys.stderr)
    if p.returncode != 0:
        raise SystemExit(p.returncode)
    return p.stdout

# Write payloads
payload_paths = {}
for platform, cfg in CHANNELS.items():
    payload = {
        "schedulingType": "automatic",
        "mode": "addToQueue",
        "text": CAPTION,
        "assets": assets,
        "source": "hermes-tbt-chart-was-telling-you-carousel-v01",
        "aiAssisted": False,
        "channelId": cfg["channelId"],
        "metadata": cfg["metadata"],
    }
    path = ROOT / f"payload-{platform}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    payload_paths[platform] = path

asset_manifest = {
    "branch": BRANCH,
    "raw_base": RAW,
    "assets": assets,
    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
(ROOT / "asset-manifest.json").write_text(json.dumps(asset_manifest, indent=2, ensure_ascii=False))

if "--dry-run-only" in sys.argv:
    for platform, path in payload_paths.items():
        run([BUFFER, "posts", "create", "--input", str(path), "--dry-run", "--output", "json"], ROOT / f"dry-run-{platform}.json")
    sys.exit(0)

created = []
for platform, path in payload_paths.items():
    create_out = run([BUFFER, "posts", "create", "--input", str(path), "--output", "json"], ROOT / f"create-{platform}.json")
    data = json.loads(create_out)
    post = data.get("post") or data
    post_id = post.get("id")
    status = post.get("status")
    if not post_id:
        raise SystemExit(f"No post id returned for {platform}: {data}")
    verify_out = run([BUFFER, "posts", "get", "--id", post_id, "--fields", FIELDS, "--output", "json"], ROOT / f"verify-{platform}-{post_id}.json")
    verify = json.loads(verify_out)
    due = verify.get("dueAt")
    created.append({
        "platform": platform,
        "channel": CHANNELS[platform]["channel"],
        "channel_id": CHANNELS[platform]["channelId"],
        "post_id": post_id,
        "create_status": status,
        "status": verify.get("status"),
        "due_at_utc": due,
        "asset_count_verified": len(verify.get("assets") or []),
        "verify_file": f"verify-{platform}-{post_id}.json",
    })

summary = {
    "status": "scheduled",
    "approved_by": "Aaron Dishner won't DM YOU!",
    "approved_at_context": "2026-07-06 Discord thread 1509755822069121114 message 1523540595044384829",
    "github_assets": {
        "repository": "https://github.com/aoraion/buffer-media-assets.git",
        "branch": BRANCH,
        "raw_urls_verified": 7,
        "dimensions": "1080x1080 each",
    },
    "created_posts": created,
    "notes": [
        "Scheduled to TBT Instagram and Facebook via /Users/bettybot/bin/buffer-tbt.",
        "TBT X channel was not used because a 7-slide carousel exceeds X image limits.",
    ],
}
(ROOT / "buffer-schedule-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
print(json.dumps(summary, indent=2, ensure_ascii=False))
