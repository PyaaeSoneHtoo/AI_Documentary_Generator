import os
import math
import struct
import wave
from typing import List, Dict

BGM_TRACKS = [
    {
        "id": "cinematic_drone",
        "name": "Cinematic Ambient Drone (Deep, Mysterious)",
        "mood": "Mystery / Deep Space"
    },
    {
        "id": "ancient_reverie",
        "name": "Ancient Reverie (Warm, Ethereal)",
        "mood": "History / Nature"
    },
    {
        "id": "none",
        "name": "None (Voiceover Only)",
        "mood": "Silent Background"
    }
]

def synthesize_ambient_soundscape(output_path: str, duration_sec: int = 30, mood: str = "cinematic_drone") -> str:
    """
    Synthesizes a seamless atmospheric ambient documentary drone
    using pure Python (wave/math), ensuring zero external downloads required!
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    sample_rate = 44100
    total_samples = int(sample_rate * duration_sec)
    
    # Audio parameters based on mood
    if mood == "ancient_reverie":
        f1, f2, f3 = 110.0, 164.81, 220.0  # A2, E3, A3 warm ambient chord
    else:
        f1, f2, f3 = 55.0, 82.41, 110.0    # A1, E2, A2 deep documentary sub-drone
        
    with wave.open(output_path, "w") as wav_file:
        wav_file.setnchannels(2)      # Stereo
        wav_file.setsampwidth(2)      # 16-bit
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(total_samples):
            t = float(i) / sample_rate
            
            # Slow LFO breathing modulation
            lfo1 = 0.8 + 0.2 * math.sin(2.0 * math.pi * 0.1 * t)
            lfo2 = 0.8 + 0.2 * math.cos(2.0 * math.pi * 0.13 * t)
            
            # Stereo panning oscillation
            pan = 0.5 + 0.3 * math.sin(2.0 * math.pi * 0.05 * t)
            
            # Ambient harmonic waves
            s1 = 0.5 * math.sin(2.0 * math.pi * f1 * t) * lfo1
            s2 = 0.3 * math.sin(2.0 * math.pi * f2 * t + 0.2) * lfo2
            s3 = 0.2 * math.sin(2.0 * math.pi * f3 * t + 0.4)
            
            # Subtle sub-harmonic pulse
            pulse = 0.15 * math.sin(2.0 * math.pi * (f1 * 0.5) * t)
            
            signal = (s1 + s2 + s3 + pulse) * 0.25
            
            # Soft fade-in and fade-out
            fade_len = sample_rate * 2
            if i < fade_len:
                signal *= (i / fade_len)
            elif i > (total_samples - fade_len):
                signal *= ((total_samples - i) / fade_len)
                
            left = int(signal * (1.0 - pan) * 32767.0)
            right = int(signal * pan * 32767.0)
            
            left = max(-32768, min(32767, left))
            right = max(-32768, min(32767, right))
            
            frames.extend(struct.pack("<hh", left, right))
            
        wav_file.writeframes(frames)
        
    return output_path

def get_or_create_bgm(bgm_id: str, assets_dir: str = "assets/bgm", duration: int = 60) -> str:
    """Returns path to requested BGM track, generating it if needed"""
    if bgm_id == "none":
        return None
        
    filename = f"{bgm_id}.wav"
    path = os.path.join(assets_dir, filename)
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        synthesize_ambient_soundscape(path, duration_sec=duration, mood=bgm_id)
        
    return path
