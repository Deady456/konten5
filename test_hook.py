import subprocess
from pathlib import Path
import yaml
import sys

ROOT = Path(r"c:\Users\Administrator\konten5")

with open(ROOT / "config.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

hook_cfg = CONFIG.get("hook_text", {})
w = CONFIG["video"]["width"]
h = CONFIG["video"]["height"]
fps = CONFIG["video"]["fps"]

hook_text = "INI ADALAH TEKS HOOK 3 DETIK PERTAMA!"
ht_font = str(ROOT / "assets" / "fonts" / "Anton-Regular.ttf").replace("\\", "/").replace(":", "\\:")
ht_size = hook_cfg.get("font_size", 80)
ht_color = hook_cfg.get("color", "white")
ht_outline = hook_cfg.get("outline", 4)
ht_duration = hook_cfg.get("duration", 3)
safe_text = hook_text.replace("'", "\u2019").replace(":", "\\:")

drawtext_filter = (
    f"drawtext=fontfile='{ht_font}':text='{safe_text}'"
    f":fontsize={ht_size}:fontcolor={ht_color}"
    f":borderw={ht_outline}:bordercolor=black"
    f":x=(w-tw)/2:y=(h-th)/2"
    f":enable='between(t\\,0\\,{ht_duration})'"
)

# test captions
dummy_ass = ROOT / "output" / "test_captions.ass"
dummy_ass.parent.mkdir(exist_ok=True)
ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Anton,55,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,6,0,5,10,10,1056,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:10.00,Default,,0,0,0,,Ini adalah contoh subtitle di tengah layar
"""
with open(dummy_ass, "w", encoding="utf-8") as f:
    f.write(ass_content)

ass_arg = str(dummy_ass).replace("\\", "/").replace(":", "\\:")
fonts_arg = str(ROOT / "assets" / "fonts").replace("\\", "/").replace(":", "\\:")
subtitles_filter = f"subtitles='{ass_arg}':fontsdir='{fonts_arg}'"

vf_chain = f"{drawtext_filter},{subtitles_filter}"

out_path = ROOT / "output" / "test_hook.mp4"

cmd = [
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", f"color=c=blue:s={w}x{h}:r={fps}:d=10",
    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
    "-vf", vf_chain,
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-c:a", "aac", "-b:a", "128k", "-shortest",
    "-pix_fmt", "yuv420p",
    str(out_path)
]

print("Running FFmpeg to generate test video...")
p = subprocess.run(cmd, capture_output=True, text=True)
if p.returncode != 0:
    print(p.stderr)
    sys.exit(1)

print(f"Test video created successfully at: {out_path}")
