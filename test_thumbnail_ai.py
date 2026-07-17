import os
import requests
from io import BytesIO
from PIL import Image

def generate_test_thumbnail_direct(prompt: str, output_path: str):
    print(f"Generating image directly from Pollinations.ai (NO Python rendering) for prompt:\n'{prompt}'...")
    
    # We add width and height for vertical Shorts
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1920&nologo=true"
    
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch image.")
        return
        
    # Just save the image directly! No Pillow text rendering.
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img.save(output_path, quality=95)
    print(f"Thumbnail saved to {output_path}")

if __name__ == "__main__":
    # The trick is to ask the AI to draw the text in the prompt itself!
    test_prompt = "A vertical YouTube Shorts thumbnail. A highly detailed close-up of a glowing DNA double helix in a futuristic laboratory. Big, bold, glowing yellow text that says 'MISTERI DNA' written across the center of the image. Cinematic lighting, 8k resolution."
    
    out_file = os.path.join(os.getcwd(), "thumbnail_test_ai_text.jpg")
    generate_test_thumbnail_direct(test_prompt, out_file)
