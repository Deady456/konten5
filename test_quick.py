"""Quick test: generate script + voice + solid background video with hook text."""
import sys, time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from src import script, voice, captions, state
from src.config import CONFIG, OUTPUT_DIR

W = CONFIG["video"]["width"]
H = CONFIG["video"]["height"]
FPS = CONFIG["video"]["fps"]


def slug(s):
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "test"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run():
    log("1/5 Generating script...")
    data = script.generate()
    log(f"    topic: {data['topic']}")
    log(f"    title: {data['title']}")
    log(f"    hook_text: {data.get('thumbnail_text', '(none)')}")
    log(f"    scenes: {len(data['scenes'])}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    work = OUTPUT_DIR / f"test_{stamp}_{slug(data['topic'])}"
    work.mkdir(parents=True, exist_ok=True)

    log("2/5 Synthesizing voice...")
    voice_mp3 = voice.synth(data["full_text"], work / "voice.mp3")
    log(f"    voice: {voice_mp3.stat().st_size/1024:.0f} KB")

    log("3/5 Transcribing (Whisper)...")
    words = captions.transcribe_words(voice_mp3, original_text=data["full_text"])
    log(f"    {len(words)} words transcribed")

    hook_text = data.get("thumbnail_text", "")
    hook_cfg = CONFIG.get("hook_text", {})
    if hook_text and hook_cfg.get("enabled", False):
        captions_words = words[len(hook_text.split()):]
        log(f"    hook_text active, skipping {len(hook_text.split())} words from captions")
    else:
        captions_words = words

    ass_path = captions.write_ass(captions_words, work / "captions.ass", W, H)
    log(f"    captions: {ass_path.name}")

    log("4/5 Building video (solid background + hook text)...")
    build_video(data, voice_mp3, ass_path, hook_text, work)

    final = work / "final.mp4"
    log(f"5/5 DONE: {final}")
    log(f"    path: {final.resolve()}")
    return final


def build_video(data, voice_mp3, ass_path, hook_text, work):
    import subprocess

    final_raw = work / "final_raw.mp4"

    voice_dur_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(voice_mp3)
    ]
    try:
        result = subprocess.run(voice_dur_cmd, capture_output=True, text=True, timeout=10)
        voice_dur = float(result.stdout.strip())
    except Exception:
        voice_dur = 30

    ass_win = str(ass_path).replace("\\", "/")
    ass_escaped = ass_win.replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x1a1a2e:s={W}x{H}:d={voice_dur+1}:r={FPS}",
        "-i", str(voice_mp3),
        "-vf", f"ass='{ass_escaped}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(final_raw)
    ]

    log(f"    ffmpeg running (voice: {voice_dur:.1f}s)...")
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        log(f"    ffmpeg stderr: {proc.stderr[-800:]}")
        raise RuntimeError("ffmpeg failed")
    log(f"    rendered in {time.time()-t0:.1f}s")

    import shutil
    shutil.copy2(final_raw, work / "final.mp4")


if __name__ == "__main__":
    run()
