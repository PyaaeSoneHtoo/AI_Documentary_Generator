import os
import re
import time
from typing import Dict, Any, List, Optional, Callable

from modules.voice_engine import generate_voiceover, get_audio_duration
from modules.visual_engine import generate_scene_image
from modules.video_engine import render_scene, concatenate_scenes, mix_background_music, merge_srt_files
from modules.audio_library import get_or_create_bgm

def sanitize_filename(name: str) -> str:
    """Sanitize string for file / folder naming"""
    return re.sub(r'[\\/*?:"<>| ]', '_', name)[:50].strip('_')

def run_documentary_pipeline(
    project_title: str,
    scenes: List[Dict[str, Any]],
    style_name: str = "Cinematic Photorealism (Universal)",
    aspect_ratio_name: str = "16:9 (Landscape - Documentary / YouTube)",
    bgm_id: str = "cinematic_drone",
    bgm_volume: float = 0.12,
    burn_subtitles: bool = True,
    output_root: str = "output",
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Dict[str, Any]:
    """
    Executes the end-to-end documentary generation pipeline:
    1. Multi-voice audio synthesis with millisecond SRT timing
    2. Cinematic image generation via Pollinations FLUX
    3. Ken Burns camera motion & subtitle burning
    4. Seamless multi-scene concatenation
    5. Ambient documentary BGM mixing & ducking
    """
    slug = sanitize_filename(project_title)
    timestamp = int(time.time())
    project_dir = os.path.join(output_root, f"{slug}_{timestamp}")
    scenes_dir = os.path.join(project_dir, "scenes")
    os.makedirs(scenes_dir, exist_ok=True)

    total_scenes = len(scenes)
    scene_video_paths = []
    scene_srt_paths = []
    scene_durations = []

    def update_progress(percent: float, message: str):
        if progress_callback:
            progress_callback(percent, message)

    update_progress(0.05, f"🎬 Initializing project: {project_title} ({total_scenes} scenes)")

    # STEP 1: Process each scene (Voiceover + Visual + Scene Video)
    for idx, scene in enumerate(scenes):
        scene_num = scene.get("scene_num", idx + 1)
        scene_title = scene.get("title", f"Scene {scene_num}")
        narration = scene.get("narration", "").strip()
        voice = scene.get("voice", "en-US-ChristopherNeural")
        prompt = scene.get("visual_prompt", "").strip() or narration
        motion = scene.get("camera_motion", "zoom_in")

        base_progress = 0.05 + (0.75 * (idx / total_scenes))
        step_delta = (0.75 / total_scenes)

        # 1A: Audio voiceover + Subtitles
        update_progress(base_progress + (step_delta * 0.2), f"🎙️ [Scene {scene_num}/{total_scenes}] Synthesizing narration ({voice})...")
        audio_file = os.path.join(scenes_dir, f"scene_{scene_num:02d}_audio.mp3")
        srt_file = os.path.join(scenes_dir, f"scene_{scene_num:02d}.srt")
        duration = generate_voiceover(narration, voice=voice, output_audio_path=audio_file, output_srt_path=srt_file)
        scene_durations.append(duration)
        scene_srt_paths.append(srt_file)

        # 1B: Visual Generation
        update_progress(base_progress + (step_delta * 0.5), f"🎨 [Scene {scene_num}/{total_scenes}] Rendering cinematic visual...")
        image_file = os.path.join(scenes_dir, f"scene_{scene_num:02d}_visual.jpg")
        generate_scene_image(
            prompt=prompt,
            style_name=style_name,
            aspect_ratio_name=aspect_ratio_name,
            output_path=image_file
        )

        # 1C: Video Scene Assembly with Ken Burns & Subtitles
        update_progress(base_progress + (step_delta * 0.8), f"🎥 [Scene {scene_num}/{total_scenes}] Applying {motion} motion & subtitles...")
        scene_mp4 = os.path.join(scenes_dir, f"scene_{scene_num:02d}_video.mp4")
        render_scene(
            image_path=image_file,
            audio_path=audio_file,
            output_scene_path=scene_mp4,
            srt_path=srt_file,
            motion=motion,
            burn_subtitles=burn_subtitles
        )
        scene_video_paths.append(scene_mp4)

    # STEP 2: Concatenate all scenes
    update_progress(0.85, "🎞️ Merging scenes into documentary timeline...")
    merged_video = os.path.join(project_dir, "documentary_merged.mp4")
    concat_success = concatenate_scenes(scene_video_paths, merged_video)
    if not concat_success:
        raise RuntimeError("Failed to concatenate scenes into documentary video.")

    # STEP 3: Mix Background Music (BGM)
    update_progress(0.92, "🎵 Synthesizing & mixing ambient documentary soundscape...")
    final_video = os.path.join(project_dir, f"{slug}_documentary.mp4")
    total_doc_duration = sum(scene_durations)
    
    bgm_file = None
    if bgm_id and bgm_id != "none":
        bgm_file = get_or_create_bgm(bgm_id, assets_dir="assets/bgm", duration=int(total_doc_duration + 5))
        
    mix_background_music(merged_video, bgm_file, final_video, bgm_volume=bgm_volume)

    # STEP 4: Merge Master Subtitle file
    master_srt = os.path.join(project_dir, f"{slug}_documentary.srt")
    merge_srt_files(scene_srt_paths, scene_durations, master_srt)

    update_progress(1.0, f"✅ Documentary completed! ({total_doc_duration:.1f}s, {total_scenes} scenes)")

    thumbnail = os.path.join(scenes_dir, "scene_01_visual.jpg")

    return {
        "success": True,
        "title": project_title,
        "video_path": final_video,
        "srt_path": master_srt,
        "thumbnail_path": thumbnail if os.path.exists(thumbnail) else None,
        "duration": total_doc_duration,
        "scenes_count": total_scenes,
        "project_dir": project_dir
    }
