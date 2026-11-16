import os
import random
import time
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont

STYLE_PRESETS = {
    "Cinematic Photorealism (Universal)": {
        "suffix": ", cinematic film still, photorealistic 8k, panavision anamorphic lens, beautiful natural color grading, volumetric lighting, hyper-realistic, dramatic atmosphere",
        "model": "flux-realism"
    },
    "BBC Nature & Wildlife": {
        "suffix": ", national geographic documentary photography, photorealistic 8k uhd, cinematic macro lens, golden hour lighting, wild animals and pristine landscape, masterpiece",
        "model": "flux"
    },
    "Historical Epic & Ancient Civilization": {
        "suffix": ", epic cinematic historical documentary still, ancient architecture, dramatic film lighting, atmospheric dust, 35mm film photograph, highly detailed, realistic historical accuracy",
        "model": "flux-realism"
    },
    "Space & Cosmic Odyssey": {
        "suffix": ", deep space exploration documentary visual, james webb telescope aesthetic, interstellar nebula, glowing stars, high-definition cosmic phenomenon, 8k cinematic space photography",
        "model": "flux"
    },
    "True Crime & Dark Noir Mystery": {
        "suffix": ", dark noir investigative documentary cinematography, moody chiaroscuro lighting, gritty film grain, rain-slicked atmosphere, mysterious shadows, 35mm film still",
        "model": "flux-realism"
    },
    "Cyberpunk & Future Sci-Fi": {
        "suffix": ", futuristic sci-fi cinematic concept art, cyberpunk aesthetic, neon reflections, holographic displays, volumetric fog, photorealistic 8k",
        "model": "flux"
    },
    "Renaissance Oil Painting": {
        "suffix": ", dramatic renaissance oil painting, rembrandt lighting, rich oil brush textures, museum masterpiece, historical fine art, dramatic storytelling",
        "model": "flux"
    }
}

ASPECT_RATIOS = {
    "16:9 (Landscape - Documentary / YouTube)": (1920, 1080),
    "9:16 (Vertical - Shorts / TikTok / Reels)": (1080, 1920),
    "2.39:1 (Ultrawide - Anamorphic Cinema)": (1920, 804),
    "1:1 (Square - Instagram)": (1080, 1080)
}

def generate_scene_image(
    prompt: str,
    style_name: str = "Cinematic Photorealism (Universal)",
    aspect_ratio_name: str = "16:9 (Landscape - Documentary / YouTube)",
    output_path: str = "scene.jpg",
    seed: int = None,
    max_retries: int = 3
) -> str:
    """
    Generates a high-resolution cinematic AI image using Pollinations.ai FLUX engine.
    Saves image to output_path and returns the path.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    style = STYLE_PRESETS.get(style_name, STYLE_PRESETS["Cinematic Photorealism (Universal)"])
    dimensions = ASPECT_RATIOS.get(aspect_ratio_name, (1920, 1080))
    width, height = dimensions

    enhanced_prompt = prompt.strip() + style["suffix"]
    encoded_prompt = urllib.parse.quote(enhanced_prompt)

    if seed is None:
        seed = random.randint(100000, 99999999)

    model = style.get("model", "flux")
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model={model}&nologo=true&seed={seed}&enhance=true"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=45)
            if response.status_code == 200 and len(response.content) > 5000:
                with open(output_path, "wb") as f:
                    f.write(response.content)

                # Validate image integrity with PIL
                with Image.open(output_path) as img:
                    img.verify()

                return output_path
        except Exception:
            time.sleep(2)

    # Fallback: Create elegant cinematic title card placeholder if network fails
    create_cinematic_fallback_image(prompt, width, height, output_path)
    return output_path

def create_cinematic_fallback_image(prompt: str, width: int, height: int, output_path: str):
    """Generates an atmospheric dark gradient title card if network request fails"""
    img = Image.new("RGB", (width, height), color=(15, 20, 30))
    draw = ImageDraw.Draw(img)

    # Gradient overlay
    for y in range(height):
        alpha = int((y / height) * 40)
        draw.line([(0, y), (width, y)], fill=(10 + alpha, 15 + alpha, 25 + alpha))

    # Decorative cinematic borders
    border_color = (60, 80, 110)
    draw.rectangle([40, 40, width - 40, height - 40], outline=border_color, width=2)
    draw.rectangle([46, 46, width - 46, height - 46], outline=(30, 40, 60), width=1)

    # Text wrapping for prompt
    text = f"SCENE: {prompt[:120]}..." if len(prompt) > 120 else f"SCENE: {prompt}"
    draw.text((width // 2, height // 2), text, fill=(220, 230, 245), anchor="mm")
    draw.text((width // 2, height // 2 + 50), "[ AI Cinematic Visual Preview ]", fill=(130, 150, 180), anchor="mm")

    img.save(output_path, quality=95)
