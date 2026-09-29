# Authors & Upstream Attributions

Voice Studio is made possible thanks to groundbreaking open-source research and engineering contributions from the global AI and speech community.

---

## Core Maintainer & Application Architecture
- **Osama Alzahrani** ([@Osama-Alzahrani-UQU](https://github.com/Osama-Alzahrani-UQU))
  - Application design, dual-engine unified speech facade router (`UnifiedTTSManager`), CustomTkinter desktop interface with real-time English (LTR) ⇄ Arabic (RTL) localization, long-form sentence boundary chunking, phonetic text normalization, and portable PyInstaller build pipeline.

---

## Upstream Open-Source Projects & Attributions

### 1. [VoiceStudio by Palash Deb](https://github.com/debpalash/VoiceStudio)
- **Author**: Palash Deb ([@debpalash](https://github.com/debpalash))
- **License**: AGPL-3.0
- **Contributions & Concepts**:
  - Broadcast-grade Audio DSP mastering pipeline (`audio_dsp.py`): EBU R128 loudness targeting (-2 dBFS peak), trailing silence trimming, soft-knee dynamic compression, boundary cross-fading, and studio acoustic presets (`Broadcast`, `Podcast`, `Warm`, `Bright`, `Raw`).
  - Fast, ReDoS-safe inline prosody and SSML markup parsing (`ssml_lite.py`): `[slow]`, `[fast]`, `[emphasis]`, `[pause]`, `<break time="..."/>`.
  - Model Context Protocol (MCP) server architecture (`mcp_server.py`) exposing standardized speech synthesis, cloning, and design tools to AI agents.

### 2. [OmniVoice by k2-fsa](https://github.com/k2-fsa/OmniVoice)
- **Authors**: k2-fsa research team (Daniel Povey, Fangjun Kuang, and contributors)
- **License**: Apache-2.0
- **Contributions & Concepts**:
  - Diffusion-based non-autoregressive speech generation covering 600+ world languages and dialects.
  - Natural-language Voice Design prompting (gender, age bracket, pitch, style, accent).
  - High-speed zero-shot voice cloning and `.pt` prompt conditioning caching.

### 3. [Coqui XTTS v2](https://github.com/coqui-ai/TTS)
- **Authors**: Coqui AI Team & TTS Community
- **License**: Coqui Public Model License (CPML) / MPL-2.0
- **Contributions & Concepts**:
  - Auto-regressive transformer speech synthesis with zero-shot multi-speaker cloning.
  - Curated studio voice profiles (6 Male, 8 Female) sampled at 24kHz mono PCM.

---

## Community & Supporting Libraries
- **CustomTkinter**: Modern GUI framework by Tom Schimansky.
- **PyTorch**: Deep learning framework by Meta AI & PyTorch Foundation.
- **Transformers**: Hugging Face model hub and tokenization ecosystem.
- **SoundFile & Pygame**: Cross-platform low-latency audio loading and playback.
