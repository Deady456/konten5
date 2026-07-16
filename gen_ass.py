import random
from pathlib import Path

def generate_ass():
    ht_dur = 2.5
    shake_dur = min(0.5, ht_dur)
    frames = int(shake_dur * 30)
    events = []
    
    palettes = ["&H00FFFF&", "&HFFFFFF&", "&H00FF00&", "&HFFFF00&", "&HFF00FF&", "&H0080FF&"]
    c1, c2, c3 = random.sample(palettes, 3)
    l1, l2, l3 = "FAKTA", "GILA", "HEWAN LAUT"
    
    def fmt_time(sec):
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        cs = int((sec % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    if frames > 0:
        frame_len = shake_dur / frames
        for i in range(frames):
            st = i * frame_len
            en = (i + 1) * frame_len
            p = st / shake_dur
            ease_out = 1 - (1 - p) ** 3
            alpha_val = int(255 * (1 - ease_out))
            alpha_tag = f"\\alpha&H{alpha_val:02X}&"
            x_center = int(-300 + (840) * ease_out)
            dx = random.randint(-20, 20)
            dy = random.randint(-20, 20)
            pos = f"{{\\pos({x_center+dx},{600+dy}){alpha_tag}}}"
            styled = f"{pos}{{\\c{c1}}}{l1}\\N{{\\c{c2}}}{l2}\\N{{\\c{c3}}}{l3}"
            events.append(f"Dialogue: 0,{fmt_time(st)},{fmt_time(en)},HookText,,0,0,0,,{styled}")
            
    if ht_dur > shake_dur:
        pos = f"{{\\pos(540,600)}}"
        styled = f"{pos}{{\\c{c1}}}{l1}\\N{{\\c{c2}}}{l2}\\N{{\\c{c3}}}{l3}"
        events.append(f"Dialogue: 0,{fmt_time(shake_dur)},{fmt_time(ht_dur)},HookText,,0,0,0,,{styled}")

    events_str = "\n".join(events)
    ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HookText,Impact,130,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,12,0,5,10,10,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{events_str}
"""
    Path("output/hook_shake_final.ass").write_text(ass_content, encoding="utf-8")
    print("Generated output/hook_shake_final.ass")

generate_ass()
