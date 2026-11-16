import asyncio
import os
import re
from typing import List, Dict, Optional, Tuple

VOICE_CATALOG = {
    "Documentary Narrators (English)": [
        {
            "id": "en-US-ChristopherNeural",
            "name": "Christopher (US - Deep, Authoritative, History)",
            "gender": "Male",
            "role": "Lead Narrator"
        },
        {
            "id": "en-GB-RyanNeural",
            "name": "Ryan (UK - BBC Nature & Classic Documentary)",
            "gender": "Male",
            "role": "BBC Nature / Classic"
        },
        {
            "id": "en-US-GuyNeural",
            "name": "Guy (US - Engaging, Modern, Tech / Science)",
            "gender": "Male",
            "role": "Science / Investigation"
        },
        {
            "id": "en-US-EricNeural",
            "name": "Eric (US - Dramatic, Dark Noir, Mystery)",
            "gender": "Male",
            "role": "Mystery / True Crime"
        },
        {
            "id": "en-GB-SoniaNeural",
            "name": "Sonia (UK - Regal, Storyteller, Historical)",
            "gender": "Female",
            "role": "Historical / Storyteller"
        },
        {
            "id": "en-US-JennyNeural",
            "name": "Jenny (US - Warm, Thoughtful, Cinematic)",
            "gender": "Female",
            "role": "Warm / Cinematic"
        },
        {
            "id": "en-US-AriaNeural",
            "name": "Aria (US - Expressive, Clear)",
            "gender": "Female",
            "role": "Narrator / Host"
        },
        {
            "id": "en-AU-WilliamNeural",
            "name": "William (Australia - Adventure & Expedition)",
            "gender": "Male",
            "role": "Adventure / Ocean"
        }
    ],
    "Character / Multi-Voice (Dialogue & Quotes)": [
        {
            "id": "en-US-RogerNeural",
            "name": "Roger (US - Veteran Historian / Scholar)",
            "gender": "Male",
            "role": "Scholar / Expert"
        },
        {
            "id": "en-US-SteffanNeural",
            "name": "Steffan (US - Deep Character / Ancient Voice)",
            "gender": "Male",
            "role": "Ancient Character"
        },
        {
            "id": "en-US-AnaNeural",
            "name": "Ana (US - Young Witness / Protagonist)",
            "gender": "Female",
            "role": "Witness / Protagonist"
        }
    ],
    "Burmese Voices (Local / Cultural)": [
        {
            "id": "my-MM-ThihaNeural",
            "name": "Thiha (Burmese - Deep Male Narrator)",
            "gender": "Male",
            "role": "Burmese Narrator"
        },
        {
            "id": "my-MM-NilarNeural",
            "name": "Nilar (Burmese - Clear Female Narrator)",
            "gender": "Female",
            "role": "Burmese Narrator"
        }
    ]
}

def get_voice_list() -> List[Dict[str, str]]:
    """Returns flat list of all voice options"""
    voices = []
    for category, items in VOICE_CATALOG.items():
        for item in items:
            voices.append({
                "category": category,
                "id": item["id"],
                "name": item["name"],
                "gender": item["gender"],
                "role": item["role"]
            })
    return voices

def get_voice_name(voice_id: str) -> str:
    """Finds display name for a voice ID"""
    for v in get_voice_list():
        if v["id"] == voice_id:
            return v["name"]
    return voice_id

async def _synthesize_edge_tts_async(text: str, voice: str, output_audio_path: str, output_srt_path: Optional[str] = None, rate: str = "+0%", pitch: str = "+0Hz") -> float:
    """Internal async synthesizer using edge-tts with SubMaker for accurate timing"""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    submaker = edge_tts.SubMaker()

    with open(output_audio_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    if output_srt_path:
        srt_content = submaker.get_srt()
        with open(output_srt_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(srt_content)

    # Determine duration
    duration = get_audio_duration(output_audio_path)
    return duration

def generate_voiceover(text: str, voice: str = "en-US-ChristopherNeural", output_audio_path: str = "voiceover.mp3", output_srt_path: Optional[str] = None, rate: str = "+0%", pitch: str = "+0Hz") -> float:
    """
    Synchronous wrapper to generate voiceover MP3 and optional timed SRT file.
    Returns audio duration in seconds.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_audio_path)), exist_ok=True)
    if output_srt_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_srt_path)), exist_ok=True)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(_synthesize_edge_tts_async(text, voice, output_audio_path, output_srt_path, rate, pitch))
        else:
            return asyncio.run(_synthesize_edge_tts_async(text, voice, output_audio_path, output_srt_path, rate, pitch))
    except RuntimeError:
        return asyncio.run(_synthesize_edge_tts_async(text, voice, output_audio_path, output_srt_path, rate, pitch))

def get_audio_duration(file_path: str) -> float:
    """Accurately calculates audio duration in seconds using mutagen or ffprobe"""
    try:
        from mutagen.mp3 import MP3
        audio = MP3(file_path)
        return float(audio.info.length)
    except Exception:
        pass

    try:
        import subprocess
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception:
        return 5.0
