import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import argparse
import json
import re
import time
import random
from datetime import datetime
from . import script, lofi_visuals, assemble, upload, state, review
from .config import CONFIG, OUTPUT_DIR, ROOT


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "short"


def _log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_once(publish_at: str | None = None, upload_to_youtube: bool = True,
             force_review: bool = False) -> dict:
    """
    Run the full pipeline.

    Args:
        publish_at: ISO8601 UTC timestamp for scheduled publish
        upload_to_youtube: Whether to upload to YouTube
        force_review: Force save as draft regardless of mode
    """
    # ============================================================
    # Step 0: Determine format variation
    # ============================================================
    content_cfg = CONFIG.get("content_variation", {})
    if content_cfg.get("enabled", False):
        formats = content_cfg.get("formats", ["list"])
        s = state.load()
        format_idx = s.get("_format_idx", 0)
        selected_format = formats[format_idx % len(formats)]
        state.update({"_format_idx": format_idx + 1})
        _log(f"0/8 Content format: {selected_format}")
    else:
        selected_format = None

    # ============================================================
    # Step 1: Generate theme, title, and bedtime quote
    # ============================================================
    _log("1/5 Generating theme, title, and bedtime quote with LLM")
    data = script.generate()
    _log(f"    title: {data['title']}")
    _log(f"    quote: {data.get('quote')}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    work = OUTPUT_DIR / f"{stamp}_{slug(data['topic'])}"
    work.mkdir(parents=True, exist_ok=True)
    with open(work / 'script.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # ============================================================
    # Step 2: Select Pure Lo-Fi Music Track
    # ============================================================
    _log("2/5 Selecting pure Lo-Fi music track (100% Music, NO voiceover)")
    music_dir = ROOT / "assets" / "music"
    music_candidates = []
    if music_dir.is_dir():
        for ext in ("*.mp3", "*.wav", "*.m4a", "*.ogg"):
            music_candidates.extend(list(music_dir.rglob(ext)))
    if not music_candidates:
        music_candidates = [p for p in (ROOT / "assets").glob("*.mp3")]

    chosen_music = random.choice(music_candidates) if music_candidates else (ROOT / "assets" / "bg.mp3")
    _log(f"    music chosen: {chosen_music.name}")

    # ============================================================
    # Step 3: Fetch nature & lofi visuals
    # ============================================================
    _log("3/5 Fetching cozy & aesthetic Lo-Fi stock videos from Pexels/Pixabay")
    scene_videos = lofi_visuals.fetch_all(data.get("scenes", []), work / "broll", target_total_dur=40.0)
    _log(f"    {len(scene_videos)} clips ready")

    # ============================================================
    # Step 4: Assemble pure Lo-Fi Short video
    # ============================================================
    _log("4/5 Assembling pure Lo-Fi Short (100% music + ambient quote)")
    final = assemble.build_pure_lofi(
        scene_videos=scene_videos,
        music_track=chosen_music,
        out_path=work / "final.mp4",
        work_dir=work / "ffmpeg",
        quote_text=data.get("quote", ""),
        song_title=data.get("song_title", chosen_music.stem),
        target_dur=40.0,
    )
    sz = final.stat().st_size / (1024 * 1024)
    _log(f"    final video ready: {final.name} ({sz:.1f} MB)")

    # ============================================================
    # Step 5: Review or Upload
    # ============================================================
    video_id = None

    # Check if review is needed
    s = state.load()
    video_count = len(s.get("published", []))
    needs_review = force_review or review.should_review(video_count)

    if needs_review and upload_to_youtube:
        _log("5/5 Saving draft for review")
        draft_path = review.save_draft(data, final)
        _log(f"    Draft saved: {draft_path.name}")
        _log("    Run: python -m src.review --list  (to see drafts)")
        _log("    Run: python -m src.review --approve <name>  (to approve)")
    elif upload_to_youtube:
        _log("5/5 Uploading to YouTube")
        video_id = upload.upload_video(
            video_path=final,
            title=data["title"],
            description=data["description"],
            tags=data["tags"],
            publish_at=publish_at,
        )
        _log(f"    uploaded: https://youtube.com/shorts/{video_id}")
    else:
        _log("5/5 Upload skipped (--no-upload)")

    # Save state
    state.add_topic(data["topic"])
    state.add_published({
        "ts": stamp,
        "topic": data["topic"],
        "title": data["title"],
        "path": str(final),
        "video_id": video_id,
        "publish_at": publish_at,
        "format": selected_format,
        "voice": data.get("_voice_name", "unknown"),
    })

    return {"video_id": video_id, "path": str(final), "topic": data["topic"]}


def main():
    p = argparse.ArgumentParser(description="FreeFaceless Pipeline")
    p.add_argument("--no-upload", action="store_true", help="Build only, don't upload")
    p.add_argument("--publish-at", default=None,
                   help="ISO8601 UTC timestamp for scheduled publish")
    p.add_argument("--force-review", action="store_true",
                   help="Force save as draft for review")
    args = p.parse_args()

    run_once(
        publish_at=args.publish_at,
        upload_to_youtube=not args.no_upload,
        force_review=args.force_review,
    )

    print("\n" + "-" * 60)
    print("Done!")
    print("-" * 60)


if __name__ == "__main__":
    main()



