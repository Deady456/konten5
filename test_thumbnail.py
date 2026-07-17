import os
import requests
from PIL import Image, ImageDraw, ImageFont
import urllib.request
from io import BytesIO

def generate_test_thumbnail(prompt: str, hook_text: str, output_path: str):
    print(f"Generating image from Pollinations.ai for prompt: '{prompt}'...")
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1920&nologo=true"
    
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch image.")
        return
        
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    
    # Pollinations might not return exact sizes, so we resize it strictly to 1080x1920
    img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
    
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    
    import random
    
    # Random vibrant color
    colors = [
        (255, 255, 0, 255),   # Yellow
        (0, 255, 255, 255),   # Cyan
        (255, 100, 100, 255), # Light Red/Pink
        (100, 255, 100, 255), # Light Green
        (255, 255, 255, 255), # White
        (255, 150, 0, 255)    # Orange
    ]
    random_color = random.choice(colors)

    # Try to load custom bold fonts
    font_paths = [
        os.path.join(os.getcwd(), "Bevan.ttf"),      # Super Bold & Impactful (Google Font)
    ]
    chosen_font_path = random.choice(font_paths)
    
    try:
        font = ImageFont.truetype(chosen_font_path, 85)
        print(f"Using font: {chosen_font_path} with color {random_color}")
    except:
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 85)
        except:
            font = ImageFont.load_default()
            
    # Helper function to draw text with outline and drop shadow
    def draw_text_with_outline(draw, x, y, text, font, text_color, outline_color, shadow_color):
        # Draw shadow
        shadow_offset = 15
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Draw outline (stroke)
        stroke_width = 8
        for adj_x in range(-stroke_width, stroke_width + 1, 2):
            for adj_y in range(-stroke_width, stroke_width + 1, 2):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
                
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)

    # Text wrapping logic to prevent going out of screen (YouTube Safe Area)
    words = hook_text.split()
    lines = []
    current_line = []
    # YouTube Shorts safe area width is roughly 750-800 pixels (to avoid right icons)
    max_width = 800 
    
    for word in words:
        test_line = " ".join(current_line + [word])
        tw = draw.textlength(test_line, font=font)
        if tw > max_width:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                # If a single word is still too long, we might need to shrink font,
                # but for now we just append it
                lines.append(word) 
                current_line = []
        else:
            current_line.append(word)
            
    if current_line:
        lines.append(" ".join(current_line))
    
    print(f"Wrapped text into {len(lines)} lines")
    
    # Draw each line
    y = int(img_height * 0.2) # Position around 20% from the top
    line_spacing = 45 # Jarak antar baris diperbesar (dari 20 menjadi 45)
    
    for line in lines:
        tw = draw.textlength(line, font=font)
        x = (img_width - tw) // 2
        
        # Get line height using textbbox
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        
        draw_text_with_outline(
            draw, x, y, line, font, 
            text_color=random_color,
            outline_color=(0, 0, 0, 255),
            shadow_color=(0, 0, 0, 150)
        )
        y += line_height + line_spacing
        
    # Convert back to RGB to save as JPG
    img = img.convert("RGB")
    img.save(output_path, quality=95)
    print(f"Thumbnail saved to {output_path}")

if __name__ == "__main__":
    test_prompt = "A dark and foggy abandoned asylum hallway at night, paranormal activity, scary, spooky, cinematic lighting, 8k resolution"
    # Testing a mystery title with normal length text
    test_text = "MISTERI RUMAH SAKIT ANGKER YANG DIRAHASIAKAN!"
    out_file = os.path.join(os.getcwd(), "thumbnail_test.jpg")
    generate_test_thumbnail(test_prompt, test_text, out_file)
