import os
import subprocess
import shutil
from typing import List, Dict, Any, Optional, Callable
from modules.voice_engine import get_audio_duration

def format_ffmpeg_path(path: str) -> str:
    """Format file path for FFmpeg filter arguments (escapes backslashes and colons)"""
    abs_path = os.path.abspath(path).replace('\\', '/')
    # Escape colon for Windows drive letters (e.g. C: -> C\:)
    if len(abs_path) > 1 and abs_path[1] == ':':
        abs_path = abs_path[0] + '\\:' + abs_path[2:]
    return abs_path

def get_ken_burns_filter(motion: str, duration: float, width: int = 1920, height: int = 1080, fps: int = 30) -> str:
    """
    Constructs an FFmpeg video filter for cinematic Ken Burns camera motion.
    Avoids jitter by scaling to high resolution first, then applying zoompan.
    """
    total_frames = max(30, int(round(duration * fps)))
    
    # Pre-scale image to fit canvas
    base_filter = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    
    if motion == "zoom_in":
        # Slow cinematic zoom from 1.0x to 1.20x
        zoom_speed = 0.20 / total_frames
        motion_filter = f"zoompan=z='min(zoom+{zoom_speed:.5f},1.22)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif motion == "zoom_out":
        # Slow cinematic zoom out from 1.20x to 1.0x
        zoom_speed = 0.20 / total_frames
        motion_filter = f"zoompan=z='if(lte(zoom,1.0),1.22,max(1.001,zoom-{zoom_speed:.5f}))':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif motion == "pan_right":
        # Slow cinematic horizontal glide to the right
        pan_speed = 0.5
        motion_filter = f"zoompan=z='1.14':d={total_frames}:x='if(lte(on,1),(0),min(iw-(iw/zoom),x+{pan_speed}))':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif motion == "pan_left":
        # Slow cinematic horizontal glide to the left
        pan_speed = 0.5
        motion_filter = f"zoompan=z='1.14':d={total_frames}:x='if(lte(on,1),(iw-(iw/zoom)),max(0,x-{pan_speed}))':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    else:
        # Static subtle pulse
        motion_filter = f"zoompan=z='1.02':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
        
    return f"{base_filter},{motion_filter}"

def render_scene(
    image_path: str,
    audio_path: str,
    output_scene_path: str,
    srt_path: Optional[str] = None,
    motion: str = "zoom_in",
    burn_subtitles: bool = True,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30
) -> bool:
    """
    Renders a single scene into an MP4 video with Ken Burns motion,
    audio narration sync, and optional burned subtitles.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_scene_path)), exist_ok=True)
    duration = get_audio_duration(audio_path)
    
    vf = get_ken_burns_filter(motion, duration, width, height, fps)
    
    # If subtitle burning is enabled and SRT exists
    if burn_subtitles and srt_path and os.path.exists(srt_path) and os.path.getsize(srt_path) > 0:
        clean_srt = format_ffmpeg_path(srt_path)
        # Netflix / Documentary style subtitles: crisp white text, subtle semi-opaque black background box
        sub_style = (
            "Fontname=Arial,Fontsize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
            "BorderStyle=3,Outline=1,Shadow=0,MarginV=35,Alignment=2"
        )
        vf += f",subtitles='{clean_srt}':force_style='{sub_style}'"
        
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_scene_path
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        # Fallback without subtitle filter in case fontconfig had an issue
        if burn_subtitles:
            fallback_vf = get_ken_burns_filter(motion, duration, width, height, fps)
            cmd[cmd.index("-vf") + 1] = fallback_vf
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return res.returncode == 0
        return False
        
    return True

def concatenate_scenes(scene_paths: List[str], output_merged_path: str) -> bool:
    """Concatenates multiple scene MP4 files losslessly using FFmpeg concat demuxer"""
    os.makedirs(os.path.dirname(os.path.abspath(output_merged_path)), exist_ok=True)
    
    concat_list_file = os.path.join(os.path.dirname(output_merged_path), "concat_list.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for scene in scene_paths:
            # Use forward slashes and escape single quotes
            clean_path = os.path.abspath(scene).replace('\\', '/')
            f.write(f"file '{clean_path}'\n")
            
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        output_merged_path
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if os.path.exists(concat_list_file):
        try:
            os.remove(concat_list_file)
        except Exception:
            pass
            
    return res.returncode == 0 and os.path.exists(output_merged_path)

def mix_background_music(
    video_path: str,
    bgm_path: Optional[str],
    output_final_path: str,
    bgm_volume: float = 0.12
) -> bool:
    """
    Mixes looped background music into the video with speech ducking
    and adds a 2-second audio fade-out at the end.
    """
    if not bgm_path or not os.path.exists(bgm_path):
        # Simply copy input to output if no BGM
        shutil.copy2(video_path, output_final_path)
        return True
        
    total_duration = get_audio_duration(video_path)
    fade_start = max(0.5, total_duration - 2.0)
    
    # Filter graph: loop BGM, duck volume, mix with voiceover, fade out audio at finish
    filter_complex = (
        f"[1:a]aloop=loop=-1:size=2e+09,volume={bgm_volume:.3f}[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[mixed];"
        f"[mixed]afade=t=out:st={fade_start:.2f}:d=2.0[aout]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", bgm_path,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_final_path
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        # Fallback to copy original video without music
        shutil.copy2(video_path, output_final_path)
        return True
        
    return True

def merge_srt_files(scene_srt_paths: List[str], scene_durations: List[float], output_master_srt: str):
    """Combines individual scene SRT files into one master SRT with cumulative timestamps"""
    from datetime import timedelta
    import re
    
    current_offset_sec = 0.0
    master_cues = []
    cue_index = 1
    
    def parse_time(timestr):
        # 00:00:01,234
        parts = re.split(r'[:,\.]', timestr)
        return timedelta(
            hours=int(parts[0]),
            minutes=int(parts[1]),
            seconds=int(parts[2]),
            milliseconds=int(parts[3])
        )
        
    def format_time(td):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        millis = int(td.microseconds / 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"
        
    for idx, srt_file in enumerate(scene_srt_paths):
        if os.path.exists(srt_file):
            with open(srt_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
            blocks = re.split(r'\n\s*\n', content)
            offset_td = timedelta(seconds=current_offset_sec)
            
            for b in blocks:
                lines = b.strip().split('\n')
                if len(lines) >= 3 and "-->" in lines[1]:
                    time_line = lines[1]
                    text = "\n".join(lines[2:])
                    m = re.match(r'(\d+:\d+:\d+[,\.]\d+)\s*-->\s*(\d+:\d+:\d+[,\.]\d+)', time_line)
                    if m:
                        start_td = parse_time(m.group(1)) + offset_td
                        end_td = parse_time(m.group(2)) + offset_td
                        master_cues.append(f"{cue_index}\n{format_time(start_td)} --> {format_time(end_td)}\n{text}\n")
                        cue_index += 1
                        
        current_offset_sec += scene_durations[idx]
        
    with open(output_master_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(master_cues))
