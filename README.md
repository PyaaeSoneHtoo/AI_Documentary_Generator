# 🎬 AI Documentary & Story Video Generator

An automated, open-source AI video production suite that creates full-length cinematic documentaries and story videos from text prompts or topics.

Built with **Zero API Keys Required**, **Zero Cost**, and **Unlimited Generation**.

---

## 🌟 Key Features

1. **Multi-Voice AI Narration (Edge-TTS)**:
   - Deep, authoritative documentary narrators (Christopher, Ryan BBC-style, Guy, Eric Noir, Sonia, Jenny, and Burmese Thiha/Nilar).
   - Multi-voice support for interviews, ancient quotes, and expert commentary.
   - Millisecond-precise subtitle timestamps extracted directly from speech waveforms.

2. **Cinematic Visual Synthesis (Pollinations.ai / FLUX)**:
   - High-definition 16:9 cinematic visuals or 9:16 vertical shorts format.
   - Curated visual styles: *BBC Nature & Wildlife*, *Historical Epic & Ancient Civilizations*, *Space & Cosmic Odyssey*, *True Crime & Dark Noir*, and *Cyberpunk*.

3. **Dynamic Ken Burns Camera Engine (FFmpeg)**:
   - Fluid camera motions: Cinematic Zoom In, Dramatic Zoom Out, Glide Pan Left, Glide Pan Right, and Subtle Breathing Pulse.
   - Microsecond audio-video synchronization.
   - Built-in Netflix/BBC documentary-style subtitle burning.

4. **Atmospheric Audio & Soundscapes**:
   - Synthesizes deep cinematic sub-bass drones and ambient harmonies.
   - Automatic speech ducking (drops music to 12% during speech) with gentle end fade-outs.

5. **Interactive Web Dashboard (Streamlit)**:
   - **Studio Tab**: Topic input, preset loader, visual art styling, aspect ratio controls.
   - **Storyboard & Scene Editor**: Edit every spoken line, prompt, narrator voice, and camera angle.
   - **Screening Room**: In-browser video player, one-click MP4 & master SRT subtitle download.
   - **Project Archive**: Browse, watch, and re-download past generated documentaries.

---

## 🚀 Quick Start

### 1. Launch the Web UI
Simply double-click `run.bat` (or `run_ai_documentary_generator.bat` in the workspace root).

Or via terminal:
```bash
cd AI_Documentary_Generator
python -m streamlit run app.py
```

Open your browser at: `http://localhost:8501`

---

## 📁 Project Structure

```
AI_Documentary_Generator/
├── app.py                     # Streamlit Web UI Dashboard
├── run.bat                    # One-click Windows runner
├── requirements.txt           # Dependencies
├── modules/
│   ├── story_engine.py        # Heuristic & LLM documentary scene architects
│   ├── voice_engine.py        # Edge-TTS multi-voice audio & subtitle generator
│   ├── visual_engine.py       # Pollinations FLUX cinematic visual generator
│   ├── video_engine.py        # FFmpeg Ken Burns motion, subtitle & concat engine
│   ├── audio_library.py       # Ambient cinematic BGM synthesizer & ducking
│   └── pipeline.py            # End-to-end documentary production pipeline
├── assets/
│   ├── bgm/                   # Ambient soundtrack storage
│   └── fonts/                 # Subtitle fonts
└── output/                    # Rendered documentary MP4s, scenes & subtitles
```

---

## 💡 Pre-Packaged Documentaries Included
- *The Lost City of Atlantis: Submerged Secrets*
- *The James Webb Cosmic Journey: Edge of the Universe*
- *The Mariana Trench: Aliens of the Abyssal Zone*
- *The Golden Age of Bagan: Empire of 10,000 Pagodas*
- *Custom Topic Auto-Expansion for ANY subject*
