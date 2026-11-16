import os
import glob
import json
import streamlit as st
from PIL import Image

# Import core modules
from modules.voice_engine import get_voice_list, get_voice_name
from modules.visual_engine import STYLE_PRESETS, ASPECT_RATIOS
from modules.story_engine import PRESET_DOCUMENTARIES, generate_documentary_script
from modules.audio_library import BGM_TRACKS
from modules.pipeline import run_documentary_pipeline

# Page Configuration
st.set_page_config(
    page_title="AI Documentary & Story Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for cinematic feel
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff8a00, #e52e71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #9aa0a6;
        margin-bottom: 20px;
    }
    .scene-box {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stat-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #1e293b;
        color: #38bdf8;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_script" not in st.session_state:
    # Default to Atlantis preset
    default_doc = PRESET_DOCUMENTARIES["The Lost City of Atlantis: Submerged Secrets"]
    st.session_state.current_script = json.loads(json.dumps(default_doc))

if "rendered_documentary" not in st.session_state:
    st.session_state.rendered_documentary = None

# Sidebar Controls
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600&auto=format&fit=crop&q=80", use_container_width=True)
    st.markdown("### ⚙️ Production Settings")

    style_choice = st.selectbox(
        "🎨 Visual Art Style",
        list(STYLE_PRESETS.keys()),
        index=0
    )

    ratio_choice = st.selectbox(
        "📐 Aspect Ratio",
        list(ASPECT_RATIOS.keys()),
        index=0
    )

    bgm_choice = st.selectbox(
        "🎵 Background Ambient Music",
        [t["name"] for t in BGM_TRACKS],
        index=0
    )
    selected_bgm_id = next(t["id"] for t in BGM_TRACKS if t["name"] == bgm_choice)

    bgm_volume = st.slider("🔊 Music Volume (Ducking)", min_value=0.05, max_value=0.35, value=0.12, step=0.01)

    burn_subs = st.checkbox("📝 Burn Subtitles into Video", value=True)

    st.markdown("---")
    st.markdown("### 🔑 Optional LLM Expansion")
    gemini_key = st.text_input("Google Gemini API Key (Optional)", type="password", help="If provided, enables deep multi-scene script writing with Gemini 1.5")
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key

# Header
st.markdown('<div class="main-header">🎬 AI Documentary & Story Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Create cinematic long-form documentaries with multi-voice AI narration, dynamic Ken Burns camera motion, and ambient music — 100% Free & Zero Setup.</div>', unsafe_allow_html=True)

tabs = st.tabs(["🌟 1. Studio & Topic", "📜 2. Storyboard & Scene Editor", "📽️ 3. Screening Room (Player)", "📁 4. Project Archive"])

# TAB 1: STUDIO
with tabs[0]:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("#### 💡 Step 1: Choose or Input Your Topic")
        topic_mode = st.radio("Topic Mode:", ["Featured Documentary Presets", "Custom Topic or Theme"], horizontal=True)

        if topic_mode == "Featured Documentary Presets":
            selected_preset_title = st.selectbox(
                "Select a Curated Documentary:",
                list(PRESET_DOCUMENTARIES.keys())
            )
            if st.button("📥 Load Preset into Storyboard", use_container_width=True):
                st.session_state.current_script = json.loads(json.dumps(PRESET_DOCUMENTARIES[selected_preset_title]))
                st.success(f"Loaded '{selected_preset_title}' with {len(st.session_state.current_script['scenes'])} scenes!")
        else:
            custom_topic = st.text_input("Enter Documentary Topic:", placeholder="e.g. The Secrets of the Great Pyramid of Giza")
            scene_count = st.slider("Target Number of Scenes:", min_value=3, max_value=8, value=4)
            
            voice_options = get_voice_list()
            narrator_choice = st.selectbox(
                "Lead Narrator Voice:",
                [f"{v['name']} ({v['role']})" for v in voice_options],
                index=0
            )
            selected_voice_id = voice_options[[f"{v['name']} ({v['role']})" for v in voice_options].index(narrator_choice)]["id"]

            if st.button("✨ Architect Documentary Storyboard", use_container_width=True):
                if not custom_topic.strip():
                    st.error("Please enter a topic.")
                else:
                    with st.spinner("Analyzing topic and structuring cinematic scenes..."):
                        script = generate_documentary_script(
                            topic=custom_topic,
                            target_scenes=scene_count,
                            voice_narrator=selected_voice_id,
                            style_name=style_choice,
                            api_key=gemini_key or os.getenv("GEMINI_API_KEY")
                        )
                        st.session_state.current_script = script
                        st.success(f"Generated documentary plan: '{script['title']}' with {len(script['scenes'])} scenes! Head to Tab 2 to review.")

    with col2:
        st.markdown("#### 🎬 Current Storyboard Overview")
        if st.session_state.current_script:
            doc = st.session_state.current_script
            st.markdown(f"**Title:** {doc.get('title', 'Untitled')}")
            st.markdown(f"**Category:** {doc.get('category', 'Documentary')}")
            st.markdown(f"**Total Scenes:** `{len(doc.get('scenes', []))}`")
            st.markdown(f"**Style:** `{style_choice}`")
            st.markdown(f"**Format:** `{ratio_choice}`")
            
            # Show summary list
            for s in doc.get("scenes", []):
                st.markdown(f"- **Scene {s['scene_num']}:** {s.get('title', 'Chapter')} *(Camera: {s.get('camera_motion', 'zoom_in')})*")

# TAB 2: STORYBOARD & SCENE EDITOR
with tabs[1]:
    st.markdown("#### 📜 Review & Refine Each Scene")
    st.info("💡 You can customize every line of speech, camera movement, and visual prompt before rendering!")

    if not st.session_state.current_script or not st.session_state.current_script.get("scenes"):
        st.warning("No scenes loaded yet. Please choose or generate a topic in Tab 1.")
    else:
        scenes = st.session_state.current_script["scenes"]
        all_voices = get_voice_list()
        voice_ids = [v["id"] for v in all_voices]
        voice_labels = [f"{v['name']}" for v in all_voices]

        for i, scene in enumerate(scenes):
            with st.expander(f"🎬 Scene {scene.get('scene_num', i+1)}: {scene.get('title', 'Chapter')}", expanded=(i==0)):
                sc_col1, sc_col2 = st.columns([1, 1])

                with sc_col1:
                    scene["title"] = st.text_input(f"Scene Title #{i+1}", value=scene.get("title", f"Scene {i+1}"), key=f"title_{i}")
                    
                    # Voice selection
                    curr_voice = scene.get("voice", "en-US-ChristopherNeural")
                    voice_idx = voice_ids.index(curr_voice) if curr_voice in voice_ids else 0
                    selected_voice_label = st.selectbox(
                        "Narrator / Speaker Voice",
                        voice_labels,
                        index=voice_idx,
                        key=f"voice_{i}"
                    )
                    scene["voice"] = voice_ids[voice_labels.index(selected_voice_label)]

                    # Camera Motion
                    motions = ["zoom_in", "zoom_out", "pan_right", "pan_left", "static"]
                    motion_labels = ["Cinematic Zoom In (Focus)", "Dramatic Zoom Out (Reveal)", "Glide Pan Right", "Glide Pan Left", "Subtle Breathing Pulse"]
                    curr_motion = scene.get("camera_motion", "zoom_in")
                    motion_idx = motions.index(curr_motion) if curr_motion in motions else 0
                    
                    selected_motion = st.selectbox(
                        "Camera Motion Filter",
                        motion_labels,
                        index=motion_idx,
                        key=f"motion_{i}"
                    )
                    scene["camera_motion"] = motions[motion_labels.index(selected_motion)]

                with sc_col2:
                    scene["narration"] = st.text_area(
                        "🎙️ Spoken Script (Narration):",
                        value=scene.get("narration", ""),
                        height=100,
                        key=f"narration_{i}"
                    )
                    scene["visual_prompt"] = st.text_area(
                        "🎨 Visual Art Generation Prompt:",
                        value=scene.get("visual_prompt", ""),
                        height=100,
                        key=f"prompt_{i}"
                    )

        st.markdown("---")
        render_btn = st.button("🚀 Render Full Documentary Video Now", type="primary", use_container_width=True)

        if render_btn:
            progress_bar = st.progress(0.0)
            status_text = st.empty()

            def progress_hook(percent, msg):
                progress_bar.progress(min(1.0, max(0.0, percent)))
                status_text.markdown(f"**{msg}**")

            try:
                result = run_documentary_pipeline(
                    project_title=st.session_state.current_script.get("title", "Documentary"),
                    scenes=st.session_state.current_script["scenes"],
                    style_name=style_choice,
                    aspect_ratio_name=ratio_choice,
                    bgm_id=selected_bgm_id,
                    bgm_volume=bgm_volume,
                    burn_subtitles=burn_subs,
                    progress_callback=progress_hook
                )
                st.session_state.rendered_documentary = result
                st.success("🎉 Video rendering complete! Switch to Tab 3: Screening Room to watch your documentary.")
            except Exception as e:
                st.error(f"❌ Rendering Error: {e}")

# TAB 3: SCREENING ROOM (PLAYER)
with tabs[2]:
    st.markdown("#### 📽️ Screening Room & Video Export")

    if st.session_state.rendered_documentary and os.path.exists(st.session_state.rendered_documentary["video_path"]):
        res = st.session_state.rendered_documentary
        v_col1, v_col2 = st.columns([2, 1])

        with v_col1:
            st.video(res["video_path"])

        with v_col2:
            st.markdown(f"### 🎬 {res['title']}")
            st.markdown(f"- **Runtime:** `{res['duration']:.1f} seconds`")
            st.markdown(f"- **Total Chapters:** `{res['scenes_count']} scenes`")
            
            file_size_mb = os.path.getsize(res["video_path"]) / (1024 * 1024)
            st.markdown(f"- **File Size:** `{file_size_mb:.2f} MB`")

            # Download MP4
            with open(res["video_path"], "rb") as vf:
                st.download_button(
                    label="⬇️ Download Final Documentary (MP4)",
                    data=vf,
                    file_name=os.path.basename(res["video_path"]),
                    mime="video/mp4",
                    use_container_width=True
                )

            # Download SRT
            if os.path.exists(res.get("srt_path", "")):
                with open(res["srt_path"], "rb") as sf:
                    st.download_button(
                        label="📄 Download Master Subtitles (SRT)",
                        data=sf,
                        file_name=os.path.basename(res["srt_path"]),
                        mime="text/plain",
                        use_container_width=True
                    )
    else:
        st.info("No video has been rendered in this session yet. Go to Tab 2 and click 'Render Full Documentary Video'!")

# TAB 4: ARCHIVE & PREVIOUS PROJECTS
with tabs[3]:
    st.markdown("#### 📁 Saved Documentaries & Media Archive")
    
    # Scan output directories for mp4 files
    saved_videos = glob.glob("output/*/*_documentary.mp4")
    if not saved_videos:
        st.write("No saved documentaries found in `output/` directory yet.")
    else:
        for vid_path in reversed(saved_videos):
            folder = os.path.dirname(vid_path)
            vid_name = os.path.basename(vid_path)
            sz_mb = os.path.getsize(vid_path) / (1024 * 1024)
            
            with st.expander(f"📽️ {vid_name} ({sz_mb:.2f} MB)"):
                arc_c1, arc_c2 = st.columns([2, 1])
                with arc_c1:
                    st.video(vid_path)
                with arc_c2:
                    st.markdown(f"**Path:** `{vid_path}`")
                    with open(vid_path, "rb") as f:
                        st.download_button(
                            label=f"⬇️ Download {vid_name}",
                            data=f,
                            file_name=vid_name,
                            mime="video/mp4",
                            key=f"dl_{vid_path}"
                        )
