import json
import os
import re
from typing import List, Dict, Any, Optional

PRESET_DOCUMENTARIES = {
    "The Lost City of Atlantis: Submerged Secrets": {
        "title": "The Lost City of Atlantis: Submerged Secrets",
        "category": "Ancient History & Mystery",
        "default_voice": "en-US-ChristopherNeural",
        "default_style": "Historical Epic & Ancient Civilization",
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Golden Metropolis",
                "speaker": "Lead Narrator",
                "voice": "en-US-ChristopherNeural",
                "narration": "More than two thousand years ago, the Greek philosopher Plato wrote of an empire beyond the Pillars of Hercules—a civilization of unimaginable wealth, advanced engineering, and boundless power.",
                "visual_prompt": "Monumental ancient city of Atlantis with concentric rings of water and land, golden temples, marble palaces, ancient triremes sailing through grand canals, sun rays breaking through majestic clouds, 8k cinematic photorealism",
                "camera_motion": "zoom_in"
            },
            {
                "scene_num": 2,
                "title": "The Wrath of the Oceans",
                "speaker": "Lead Narrator",
                "voice": "en-US-ChristopherNeural",
                "narration": "In a single day and night of catastrophic misfortune, violent earthquakes shook the tectonic plates. Towering tsunamis swept through the marble corridors, swallowing the golden towers into the abyssal depths.",
                "visual_prompt": "Cataclysmic ocean tsunami crashing violently over towering ancient Greek marble towers and bronze statues, dramatic stormy skies with lightning, dark churning waves, cinematic devastation",
                "camera_motion": "pan_right"
            },
            {
                "scene_num": 3,
                "title": "Ruins in the Abyssal Blue",
                "speaker": "Deep Ocean Explorer",
                "voice": "en-US-GuyNeural",
                "narration": "Modern deep-sea submersibles scanning the Atlantic seabed have revealed anomalous geometric structures—colossal megalithic columns standing silent under thousands of feet of crushing water.",
                "visual_prompt": "Deep sea research submarine with bright xenon headlights illuminating submerged megalithic stone pillars and statues covered in coral on the dark ocean floor, bioluminescent marine life, eerie atmospheric blue haze",
                "camera_motion": "zoom_out"
            },
            {
                "scene_num": 4,
                "title": "An Eternal Legend",
                "speaker": "Lead Narrator",
                "voice": "en-US-ChristopherNeural",
                "narration": "Whether a moral allegory or a submerged historical truth, Atlantis remains humanity's greatest reminder: that even the mightiest empires can vanish beneath the tides of time.",
                "visual_prompt": "Panoramic sunset over the endless deep ocean, calm glittering waves reflecting golden sunlight, ethereal outline of an ancient sunken city faintly visible beneath translucent crystal water",
                "camera_motion": "pan_left"
            }
        ]
    },
    "The James Webb Cosmic Journey: Edge of the Universe": {
        "title": "The James Webb Cosmic Journey: Edge of the Universe",
        "category": "Space Exploration & Science",
        "default_voice": "en-GB-RyanNeural",
        "default_style": "Space & Cosmic Odyssey",
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Golden Eye of Humanity",
                "speaker": "Astrophysicist Narrator",
                "voice": "en-GB-RyanNeural",
                "narration": "One million miles from Earth, orbiting in the frigid silence of the Lagrange Point, rests humanity's most ambitious time machine: the James Webb Space Telescope.",
                "visual_prompt": "James Webb Space Telescope in deep space with its golden hexagonal beryllium mirrors glowing in sunlight, silver sunshield deployed, Earth and Moon glowing small in the far cosmic background, 8k space cinematography",
                "camera_motion": "zoom_in"
            },
            {
                "scene_num": 2,
                "title": "The First Dawning Stars",
                "speaker": "Astrophysicist Narrator",
                "voice": "en-GB-RyanNeural",
                "narration": "By capturing infrared light that has travelled for over thirteen billion years, Webb peers directly into cosmic dawn—the primordial era when the very first stars ignited the dark universe.",
                "visual_prompt": "Spectacular cosmic deep field nebula glowing with thousands of spiral and elliptical galaxies, stellar nurseries with pink and turquoise hydrogen gas clouds, brilliant young stars bursting into life, James Webb telescope imagery",
                "camera_motion": "zoom_out"
            },
            {
                "scene_num": 3,
                "title": "Atmospheres of Alien Worlds",
                "speaker": "Astrophysicist Narrator",
                "voice": "en-US-GuyNeural",
                "narration": "For the first time in history, we are decoding the chemical signatures of distant exoplanets—detecting water vapor, carbon dioxide, and atmospheric clouds across light-years of void.",
                "visual_prompt": "Cinematic visual of a lush Earth-like exoplanet with glowing blue oceans and violet clouds orbiting close to a brilliant red dwarf star, distant moons visible in alien orbit, highly realistic space art",
                "camera_motion": "pan_right"
            },
            {
                "scene_num": 4,
                "title": "The Endless Frontier",
                "speaker": "Astrophysicist Narrator",
                "voice": "en-GB-RyanNeural",
                "narration": "Looking deeper into the void, we do not just discover the history of the cosmos; we discover our own origins, written across the stardust of eternity.",
                "visual_prompt": "Vast spiral galaxy rotating majestically against the deep velvet black of space, billions of shimmering star clusters and luminous cosmic dust lanes, panoramic breathtaking astronomy view",
                "camera_motion": "zoom_in"
            }
        ]
    },
    "The Mariana Trench: Aliens of the Abyssal Zone": {
        "title": "The Mariana Trench: Aliens of the Abyssal Zone",
        "category": "Ocean & Marine Biology",
        "default_voice": "en-US-EricNeural",
        "default_style": "BBC Nature & Wildlife",
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Descent into Midnight",
                "speaker": "Narrator",
                "voice": "en-US-EricNeural",
                "narration": "Seven miles straight down in the western Pacific Ocean lies the Mariana Trench—a realm of absolute darkness where pressures exceed one thousand atmospheres.",
                "visual_prompt": "Cinematic underwater view of a steep oceanic abyssal canyon descending into pitch black abyss, distant blue ocean light fading above, dramatic underwater topography",
                "camera_motion": "zoom_in"
            },
            {
                "scene_num": 2,
                "title": "Creatures of Cold Fire",
                "speaker": "Marine Biologist",
                "voice": "en-GB-SoniaNeural",
                "narration": "In this crushing wasteland, life has abandoned sunlight. Organisms survive through bioluminescence—producing their own living light to hunt, communicate, and evade unseen predators.",
                "visual_prompt": "Alien-like deep sea jellyfish with neon bioluminescent blue and green light pulses glowing through translucent body in pitch black ocean water, macro National Geographic photography",
                "camera_motion": "pan_left"
            },
            {
                "scene_num": 3,
                "title": "The Hydrothermal Furnaces",
                "speaker": "Narrator",
                "voice": "en-US-EricNeural",
                "narration": "Around volcanic black smoker chimneys spewing mineral-rich superheated water, entire ecosystems thrive completely disconnected from solar photosynthesis.",
                "visual_prompt": "Underwater volcanic hydrothermal vent chimney spewing black mineral smoke on ocean floor, surrounded by giant white tube worms and deep sea crabs illuminated by submarine light beam",
                "camera_motion": "zoom_out"
            },
            {
                "scene_num": 4,
                "title": "Earth's Final Secret",
                "speaker": "Narrator",
                "voice": "en-US-EricNeural",
                "narration": "The hadal zone proves that life will carve out an empire in the most extreme corners of our world—and perhaps on icy moons across the solar system.",
                "visual_prompt": "Deep sea exploration submersible hovering peacefully over vast unexplored ocean floor trench, glowing searchlights illuminating uncharted volcanic rocks, awe-inspiring silence",
                "camera_motion": "pan_right"
            }
        ]
    },
    "The Golden Age of Bagan: Empire of 10,000 Pagodas": {
        "title": "The Golden Age of Bagan: Empire of 10,000 Pagodas",
        "category": "Burmese History & Heritage",
        "default_voice": "en-US-ChristopherNeural",
        "default_style": "Historical Epic & Ancient Civilization",
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Plain of Gold",
                "speaker": "Lead Narrator",
                "voice": "en-US-ChristopherNeural",
                "narration": "On the sun-drenched plains of central Myanmar, along the curves of the Irrawaddy River, arose one of the most magnificent religious landscapes in human civilization: the Kingdom of Bagan.",
                "visual_prompt": "Breathtaking aerial sunrise over Bagan Myanmar, thousands of ancient red brick Buddhist pagodas and golden stupas emerging through mystical morning mist, hot air balloons drifting gently, warm golden light",
                "camera_motion": "zoom_in"
            },
            {
                "scene_num": 2,
                "title": "Anawrahta and the Monks",
                "speaker": "Historian",
                "voice": "en-US-RogerNeural",
                "narration": "In the eleventh century, King Anawrahta unified the realm under Theravada Buddhism. For over two centuries, kings, queens, and commoners constructed more than ten thousand sacred monuments.",
                "visual_prompt": "Ancient Burmese king in royal silk garments and golden crown standing before a newly consecrated grand red brick temple, Buddhist monks in saffron robes chanting, cinematic historical epic",
                "camera_motion": "pan_right"
            },
            {
                "scene_num": 3,
                "title": "The Murals of Time",
                "speaker": "Lead Narrator",
                "voice": "en-US-ChristopherNeural",
                "narration": "Inside the arched corridors of Ananda and Dhammayangyi, ancient fresco murals painted in mineral pigments have survived earthquakes and centuries of monsoon rains.",
                "visual_prompt": "Interior corridor of ancient Bagan temple illuminated by single shaft of golden sunlight, ancient Buddhist wall paintings and intricate stucco carvings, golden Buddha statue glowing serenely in background",
                "camera_motion": "zoom_out"
            },
            {
                "scene_num": 4,
                "title": "The Timeless Sanctuary",
                "speaker": "Lead Narrator",
                "voice": "en-US-ChristopherNeural",
                "narration": "Though the empire eventually yielded to the tides of history, the bells of Bagan still whisper an enduring testament of devotion, art, and imperial grace.",
                "visual_prompt": "Sunset over Bagan landscape, silhouettes of ancient stupas against dramatic crimson and violet sky, serene and spiritual atmosphere, 8k National Geographic masterpiece",
                "camera_motion": "pan_left"
            }
        ]
    }
}

def generate_documentary_script(
    topic: str,
    target_scenes: int = 4,
    voice_narrator: str = "en-US-ChristopherNeural",
    style_name: str = "Cinematic Photorealism (Universal)",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a structured documentary script with scenes, narration, visual prompts, and camera directions.
    Uses Gemini API if key is provided, or uses smart heuristic story architect.
    """
    # Check if matches any preset title
    for title, doc in PRESET_DOCUMENTARIES.items():
        if topic.lower().strip() in title.lower() or title.lower() in topic.lower().strip():
            return doc

    # If Gemini API key is available, call Gemini API
    if api_key and api_key.strip():
        try:
            return generate_with_gemini(topic, target_scenes, voice_narrator, style_name, api_key)
        except Exception:
            pass

    # High quality built-in heuristic documentary story architect
    return generate_heuristic_documentary(topic, target_scenes, voice_narrator, style_name)

def generate_heuristic_documentary(
    topic: str,
    target_scenes: int = 4,
    voice_narrator: str = "en-US-ChristopherNeural",
    style_name: str = "Cinematic Photorealism (Universal)"
) -> Dict[str, Any]:
    """
    Intelligent heuristic documentary script generator for any topic without requiring an external API key.
    """
    clean_topic = topic.strip().title()

    templates = [
        {
            "stage": "The Genesis & The World Before",
            "camera": "zoom_in",
            "narration_pattern": f"For generations, {clean_topic} was merely a whisper—an elusive phenomenon that challenged the boundaries of human understanding. To understand its true magnitude, we must journey back to where the story first began.",
            "prompt_pattern": f"Cinematic wide establishing shot of {clean_topic}, dramatic atmospheric horizon, golden hour lighting, cinematic film photography, 8k masterpiece"
        },
        {
            "stage": "The Turning Point & The Conflict",
            "camera": "pan_right",
            "narration_pattern": f"As scholars and explorers delved deeper into {clean_topic}, they uncovered startling evidence that overturned centuries of accepted wisdom, sparking fierce debates across the globe.",
            "prompt_pattern": f"Dramatic and detailed cinematic scene depicting the mysteries of {clean_topic}, volumetric lighting, intense dramatic atmosphere, high contrast, 35mm film still"
        },
        {
            "stage": "The Deep Investigation & Revelation",
            "camera": "zoom_out",
            "narration_pattern": f"Under the lens of modern analysis, intricate patterns emerged from within {clean_topic}, revealing hidden complexities that had remained concealed beneath the surface of time.",
            "prompt_pattern": f"Breathtaking close-up cinematic visual of {clean_topic}, highly intricate details, photorealistic lighting, cinematic color grading, national geographic documentary quality"
        },
        {
            "stage": "The Legacy & The Infinite Horizon",
            "camera": "pan_left",
            "narration_pattern": f"Today, the story of {clean_topic} stands as a testament to humanity's relentless quest for truth—a legacy that continues to reshape our understanding of the universe.",
            "prompt_pattern": f"Panoramic cinematic sunset view reflecting the profound impact of {clean_topic}, serene glowing skies, epic cinematic scale, beautiful depth of field"
        },
        {
            "stage": "The Untold Secret",
            "camera": "zoom_in",
            "narration_pattern": f"Yet, even with all our discoveries, profound enigmas surround {clean_topic}, reminding us that some mysteries are waiting for future generations to unlock.",
            "prompt_pattern": f"Mysterious and atmospheric cinematic exploration of {clean_topic}, moody shadows, ethereal light rays breaking through darkness, 8k resolution"
        }
    ]

    scenes = []
    num_to_build = min(target_scenes, len(templates))
    for i in range(num_to_build):
        tmpl = templates[i]
        scenes.append({
            "scene_num": i + 1,
            "title": f"Chapter {i + 1}: {tmpl['stage']}",
            "speaker": "Lead Narrator",
            "voice": voice_narrator,
            "narration": tmpl["narration_pattern"],
            "visual_prompt": tmpl["prompt_pattern"],
            "camera_motion": tmpl["camera"]
        })

    return {
        "title": clean_topic,
        "category": "Custom Documentary",
        "default_voice": voice_narrator,
        "default_style": style_name,
        "scenes": scenes
    }

def generate_with_gemini(topic: str, target_scenes: int, voice_narrator: str, style_name: str, api_key: str) -> Dict[str, Any]:
    """Generates documentary scenes using Google Gemini API"""
    import urllib.request

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    system_prompt = (
        f"You are an award-winning BBC / National Geographic documentary director and scriptwriter. "
        f"Create a captivating {target_scenes}-scene documentary about '{topic}'. "
        f"Return ONLY valid JSON matching this exact structure with no markdown backticks: "
        f"{{\"title\": \"...\", \"category\": \"...\", \"scenes\": ["
        f"{{\"scene_num\": 1, \"title\": \"...\", \"speaker\": \"Lead Narrator\", \"voice\": \"{voice_narrator}\", "
        f"\"narration\": \"Engaging documentary narration (2-3 sentences)\", "
        f"\"visual_prompt\": \"Detailed photorealistic image generation prompt for scene\", "
        f"\"camera_motion\": \"zoom_in|zoom_out|pan_left|pan_right\"}}]}}"
    )

    data = {
        "contents": [{"parts": [{"text": system_prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Clean potential markdown fences
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"```$", "", text)
        parsed = json.loads(text.strip())
        parsed["default_voice"] = voice_narrator
        parsed["default_style"] = style_name
        return parsed
