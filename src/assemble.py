import os
import json
import random
import subprocess
from pathlib import Path
from .config import CONFIG, ROOT

def _run(cmd: list[str], desc: str = ""):
    if desc:
        print(f"    ffmpeg: {desc}")
    p = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if p.returncode != 0:
        tail = (p.stderr or "")[-3000:]
        raise RuntimeError(f"FFmpeg command failed (exit {p.returncode}): {cmd[0]} ...\n--- stderr ---\n{tail}")

def probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])

def build(
    scene_videos: list[Path],
    voice_audio: Path,
    captions_ass: Path,
    out_path: Path,
    work_dir: Path,
    words: list[dict] = None,
    scenes: list[dict] = None,
    videos_per_scene: int = 1,
    hook_text: str = "",
    thumbnail_img: Path = None,
) -> Path:
    """
    Assemble scene videos, voice narration, background music, and captions using FFmpeg.
    """
    v = CONFIG["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write concat list for scene videos
    concat_list = work_dir / "concat_scenes.txt"
    concat_lines = [f"file '{p.absolute().as_posix()}'" for p in scene_videos]
    concat_list.write_text("\n".join(concat_lines), encoding="utf-8")

    combined_video = work_dir / "combined_video.mp4"
    _run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(combined_video),
    ], "concatenating news scene videos")

    # 2. Pick background music (random from assets/music/ or assets/bg.mp3)
    music_candidates = []
    music_dir = ROOT / "assets" / "music"
    if music_dir.is_dir():
        for ext in ("*.mp3", "*.wav", "*.m4a", "*.ogg"):
            music_candidates.extend(list(music_dir.rglob(ext)))
    if not music_candidates:
        music_candidates = [p for p in (ROOT / "assets").glob("*.mp3") if p.is_file() and p.name != "bg.mp3"]

    bg_music = random.choice(music_candidates) if music_candidates else (ROOT / "assets" / "bg.mp3")

    audio_dur = probe_duration(voice_audio)
    video_dur = probe_duration(combined_video)
    final_dur = max(audio_dur, video_dur)

    # 3. Assemble with audio mixing and ASS subtitles burn-in
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ass_escaped = str(captions_ass.absolute()).replace("\\", "/").replace(":", "\\:")

    vf_filters = [
        f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
        f"subtitles=filename='{ass_escaped}'"
    ]
    vf_str = ",".join(vf_filters)

    if bg_music.exists():
        print(f"    [Assemble] Adding background music ({bg_music.name}) with volume=0.15...")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(combined_video),
            "-i", str(voice_audio),
            "-stream_loop", "-1", "-i", str(bg_music),
            "-filter_complex",
            f"[0:v]{vf_str}[v];"
            f"[2:a]volume=0.15[bg];"
            f"[1:a][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", f"{final_dur:.3f}",
            str(out_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(combined_video),
            "-i", str(voice_audio),
            "-vf", vf_str,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", f"{final_dur:.3f}",
            str(out_path),
        ]

    _run(cmd, "rendering final video with captions and mixed audio")
    return out_path


def _format_ass_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - h * 3600 - m * 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"


def _wrap_quote(text: str, max_chars_per_line: int = 30) -> str:
    words = text.strip().split()
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + 1 > max_chars_per_line and curr:
            lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
        else:
            curr.append(w)
            curr_len += len(w) + 1
    if curr:
        lines.append(" ".join(curr))
    return "\\N".join(lines)


def build_pure_lofi(
    scene_videos: list[Path],
    music_track: Path,
    out_path: Path,
    work_dir: Path,
    quote_text: str = "",
    song_title: str = "",
    target_dur: float = 40.0,
) -> Path:
    """
    Assemble pure Lo-Fi music Shorts:
    - 100% pure music (no voiceover / narration)
    - Concatenates aesthetic B-rolls (rain, night cozy)
    - Elegant burning of subtitle overlay (song title, calming quote, 24/7 radio badge)
    - Audio fade-in and fade-out
    """
    v = CONFIG["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. Concat scenes
    concat_list = work_dir / "concat_scenes.txt"
    concat_lines = [f"file '{p.absolute().as_posix()}'" for p in scene_videos]
    concat_list.write_text("\n".join(concat_lines), encoding="utf-8")

    combined_video = work_dir / "combined_video.mp4"
    _run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(combined_video),
    ], "concatenating lofi scene videos")

    # 2. Write aesthetic ASS subtitle file
    ass_path = work_dir / "pure_lofi.ass"
    display_title = song_title if song_title else music_track.stem
    wrapped_quote = _wrap_quote(quote_text, max_chars_per_line=28) if quote_text else "breathe in, let go... rest well tonight 🌙"
    
    end_t_str = _format_ass_ts(target_dur - 1.0)
    end_badge_t_str = _format_ass_ts(target_dur - 0.5)
    
    ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopBadge, Arial, 34, &H00E8F8F5&, &H000000FF&, &H00000000&, &H80000000&, 1, 0, 0, 0, 100, 100, 1, 0, 1, 3, 2, 8, 40, 40, 240, 1
Style: MainQuote, Georgia, 46, &H00FFFFFF&, &H000000FF&, &H00000000&, &H90000000&, 0, 1, 0, 0, 100, 100, 1, 0, 3, 4, 3, 5, 80, 80, 0, 1
Style: BottomBadge, Arial, 32, &H00A0D2FA&, &H000000FF&, &H00000000&, &H80000000&, 1, 0, 0, 0, 100, 100, 1, 0, 1, 3, 2, 2, 40, 40, 320, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.80,{end_badge_t_str},TopBadge,,0,0,0,,{{\\fad(800,800)}}♫ {display_title}
Dialogue: 0,0:00:01.50,{end_t_str},MainQuote,,0,0,0,,{{\\fad(1200,1200)}}{wrapped_quote}
Dialogue: 0,0:00:03.00,{end_badge_t_str},BottomBadge,,0,0,0,,{{\\fad(1000,1000)}}🌙 24/7 Live Stream on Channel
"""
    ass_path.write_text(ass_content, encoding="utf-8")
    ass_escaped = str(ass_path.absolute()).replace("\\", "/").replace(":", "\\:")

    # 3. Audio & Video Assemble with FFmpeg
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    fade_out_st = max(0.0, target_dur - 2.0)
    af_filter = f"afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out_st:.2f}:d=2.0,volume=1.0"
    
    vf_filter = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fade=t=in:st=0:d=1.0,fade=t=out:st={target_dur-1.0:.2f}:d=1.0,subtitles=filename='{ass_escaped}'"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(combined_video),
        "-i", str(music_track),
        "-filter_complex",
        f"[0:v]{vf_filter}[v];[1:a]{af_filter}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", f"{target_dur:.2f}",
        str(out_path),
    ]

    _run(cmd, "rendering pure lofi music Short with ambient typography")
    return out_path
