# Voice Studio — Neural Multilingual Text-to-Speech & Voice Studio Suite

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1%2B-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![OmniVoice](https://img.shields.io/badge/Engine-k2--fsa%20OmniVoice-ff69b4)](https://github.com/k2-fsa/OmniVoice)
[![Coqui XTTS v2](https://img.shields.io/badge/Engine-Coqui%20XTTS%20v2-89b4fa)](https://github.com/coqui-ai/TTS)
[![Audio DSP](https://img.shields.io/badge/DSP-VoiceStudio%20Mastering-a6e3a1)](https://github.com/debpalash/VoiceStudio)
[![MCP](https://img.shields.io/badge/Protocol-MCP%20Server-cba6f7)](https://modelcontextprotocol.io/)
[![UI](https://img.shields.io/badge/GUI-CustomTkinter-fab387)](https://github.com/TomSchimansky/CustomTkinter)
[![License: MIT](https://img.shields.io/badge/License-MIT-a6e3a1.svg)](LICENSE)

**Voice Studio** is a unified, production-grade neural speech synthesis workstation, desktop application, and developer API suite. It seamlessly integrates diffusion-based multilingual synthesis (**k2-fsa OmniVoice**), auto-regressive multi-speaker voice cloning (**Coqui XTTS v2**), broadcast audio mastering DSP pipelines (**debpalash VoiceStudio**), and Model Context Protocol (**MCP**) tools for autonomous AI agents.

---

## Key Highlights & Core Features

### 1. Dual-Engine Neural Architecture
- **k2-fsa OmniVoice Diffusion Engine**:
  - Unmatched multilingual coverage spanning **600+ world languages and dialects** (including Modern Standard Arabic, Gulf, Levantine, Egyptian, and North African accents).
  - **Natural-Language Voice Design**: Synthesize customized speakers by defining gender (`Female`, `Male`), age brackets (`Child`, `Young Adult`, `Middle Aged`, `Elderly`), pitch curves, delivery styles, and accents on the fly without training.
  - **Zero-Shot Voice Cloning**: Instant voice extraction from clean 3–10s audio samples with portable `.pt` voice prompt caching.
- **Coqui XTTS v2 Auto-Regressive Engine**:
  - High-fidelity studio voice synthesis with 14 curated studio voices (6 Male, 8 Female) sampled at 24kHz mono PCM.
  - Expressive prosody, native sentence-boundary chunking, and zero-gap PCM concatenation.

### 2. Broadcast-Grade Audio DSP & Mastering Pipeline
Adapted from **Palash Deb's VoiceStudio** (`services/audio_dsp.py`), Voice Studio features an automated broadcast mastering chain applied to synthesized audio:
- **EBU R128 Peak Loudness Targeting**: Peak normalization to `-2.0 dBFS` with a `-50 dBFS` silence safety floor to prevent noise amplification.
- **Soft-Knee Dynamic Range Compression**: Vectorized PyTorch compression ensuring clear, broadcast-grade speech without clipping or distortion.
- **Chunk Boundary De-Clicking**: Micro raised-cosine cross-fading eliminating pops and acoustic discontinuities at sentence concatenation boundaries.
- **Trailing Silence Trimming**: Intelligently cleans trailing dead silence while preserving natural room reverberation decay.
- **Mastering Acoustic Presets**:
  - `📻 Broadcast Studio`: Radio/podcast standard — warm, punchy, compressed (-2 dBFS peak).
  - `🎙️ Podcast Voice`: Intimate, high vocal presence, crisp consonant definition.
  - `☕ Warm & Cozy`: Full-bodied low-mids, soothing narrative tone for audiobooks.
  - `✨ Crisp & Bright`: Airy high-frequency boost for ultra-articulate educational narration.
  - `🔇 Raw Output`: Direct uncolored model output.

### 3. Lightweight SSML & Emotional Expression Markup
Adapted from `debpalash/VoiceStudio`'s `ssml_lite.py`:
- **Speed & Prosody Modifiers**: `[slow]...[/slow]`, `[fast]...[/fast]`, `[emphasis]...[/emphasis]`.
- **Silence & Pauses**: `[pause]`, `[pause:500ms]`, `<break time="1s"/>`.
- **Non-Verbal Emotional Cues**: `[laughter]`, `[whisper]`, `[sigh]`.

### 4. Model Context Protocol (MCP) Server for AI Agents
Built on `mcp.server.fastmcp`, Voice Studio exposes full speech synthesis capabilities as native tools for AI coding assistants (Claude Code, Cursor, Codex, Antigravity):
- `synthesize_speech`: Text → WAV with engine selection, speaker/instruct customization, speed, and DSP preset.
- `clone_voice`: Extract and cache voice conditioning from audio files.
- `list_voices`: Enumerate available voices, age brackets, pitches, and languages.
- `list_dsp_presets`: Inspect broadcast mastering presets.
- `check_system_status`: Hardware acceleration and model readiness check.
- Supports both standard I/O (`stdio`) and Server-Sent Events (`--sse --port 3900`).

### 5. Asynchronous CustomTkinter Desktop GUI
- **Bidirectional UI Localization**: Instant runtime switching between **English (LTR)** and **Arabic (RTL)** across all menus, badges, dialogs, and controls.
- **Hardware Acceleration Monitor**: Real-time badge tracking CUDA GPU acceleration vs multi-core CPU fallback.
- **Embedded Audio Player Cards**: Interactive waveform playback, seek controls, and one-click WAV export.

---

## System Requirements & Compatibility

| Component | Minimum Specification (CPU Mode) | Recommended Specification (GPU Mode) |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 / 11 (64-bit), Linux, macOS | Windows 10 / 11 (64-bit) |
| **Processor (CPU)** | Quad-Core CPU (Intel Core i5 / AMD Ryzen 5) | 6+ Core Modern High-Clock CPU |
| **Memory (RAM)** | **8 GB RAM** | **16 GB – 32 GB RAM** |
| **Graphics (GPU)** | *No GPU required* (Automatic multi-core CPU mode) | NVIDIA GPU with **6 GB+ VRAM** (CUDA 12+) |
| **Disk Space** | **4 GB SSD space** | **8 GB+ High-Speed NVMe SSD** |
| **Runtime** | Python 3.10 – 3.12 | Python 3.10 – 3.12 + CUDA Toolkit |

---

## Installation & Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Osama-Alzahrani-UQU/Voice-Studio-TTS.git
cd Voice-Studio-TTS
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Launch the Desktop Application
```bash
python main.py
```

### 4. Run the Model Context Protocol (MCP) Server
To connect Voice Studio to Claude Desktop, Cursor, or Antigravity:
```bash
# stdio mode (Claude Desktop / Cursor)
python mcp_server.py

# SSE mode (remote agents / n8n / webhooks)
python mcp_server.py --sse --port 3900
```

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "voicestudio": {
      "command": "python",
      "args": ["E:/Projects_D/LocalTTS_App/mcp_server.py"]
    }
  }
}
```

### 5. Command-Line Batch Synthesis (CLI)
```bash
# Synthesize text directly
python cli_synthesizer.py --text "Welcome to Voice Studio" --engine omnivoice --output welcome.wav

# Synthesize a long text file with Broadcast DSP mastering
python cli_synthesizer.py --file story.txt --engine xtts --speaker "Damien_Black" --dsp broadcast --output story.wav
```

---

## Architecture & Project Structure

```
Voice-Studio-TTS/
├── assets/                     # Custom branding, icons, and banners
├── gui/                        # Asynchronous CustomTkinter GUI components
│   ├── audio_widget.py         # Embedded playback controls and export card
│   ├── chat_bubble.py          # LTR/RTL chat cards with engine badges
│   └── main_window.py          # Primary application window & controls
├── omnivoice/                  # k2-fsa OmniVoice neural diffusion engine
├── speakers/                   # Reference audio samples for XTTS v2 voices
├── arabic_text_processor.py    # Phonetic normalization, diacritic cleaner
├── audio_dsp.py                # Broadcast mastering, EBU R128 normalization (debpalash)
├── audio_player.py             # Low-latency playback controller
├── build_exe.py                # Automated PyInstaller executable packager
├── cli_synthesizer.py          # Terminal & headless batch synthesizer
├── mcp_server.py               # FastMCP server for AI agent integrations
├── ssml_lite.py                # Lightweight prosody & pause parser (debpalash)
├── text_splitter.py            # Sentence boundary chunking engine
├── unified_tts_manager.py      # Dual-engine unified facade router
├── xtts_engine.py              # Coqui XTTS v2 engine with Transformers 5 shim
├── AUTHORS.md                  # Detailed upstream attributions & credits
└── requirements.txt            # Dependency manifest
```

---

## Authors & Upstream Attributions

Voice Studio is built on the shoulders of giants. We express our deepest gratitude to:
1. **Palash Deb** ([@debpalash](https://github.com/debpalash)) — Author of [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) for the broadcast audio DSP mastering architecture, SSML-Lite markup parser, and MCP server tooling.
2. **k2-fsa Research Team** ([@k2-fsa](https://github.com/k2-fsa)) — Authors of [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice) for diffusion-based speech generation and 600+ language support.
3. **Coqui AI & Community** ([@coqui-ai](https://github.com/coqui-ai)) — Authors of [Coqui TTS](https://github.com/coqui-ai/TTS) for the XTTS v2 foundation and voice cloning technology.
4. **Osama Alzahrani** ([@Osama-Alzahrani-UQU](https://github.com/Osama-Alzahrani-UQU)) — Application architecture, unified facade engine, CustomTkinter bilingual interface, and standalone distribution.

See [AUTHORS.md](AUTHORS.md) for full details.

---

## License

This project is licensed under the **MIT License**. Third-party models and components retain their respective upstream licenses (Apache-2.0 for OmniVoice, CPML for Coqui XTTS v2, and AGPL-3.0 for debpalash/VoiceStudio tools).

---
---

# استوديو الصوت — منصة تحويل النص إلى كلام والذكاء الاصطناعي الصوتي

تطبيق برمجي متكامل ومفتوح المصدر لتوليد الأصوات العصبية الاصطناعية، واستنساخ الأصوات، وتصميم نبرات صوتية جديدة عبر الذكاء الاصطناعي التوليدي، مع واجهة مكتبية تفاعلية ثنائية اللغة (عربي / إنجليزي)، ومعالجة صوتية إذاعية متقدمة، وخادم بروتوكول سياق النماذج للوكلاء الأذكياء.

---

## أبرز المميزات والقدرات الهندسية

### 1. بنية المحرك المزدوج الموحد
- **محرك الانتشار العصبي متعدد اللغات (k2-fsa OmniVoice)**:
  - دعم هائل لأكثر من **600 لغة ولهجة عالمية** تشمل اللغة العربية الفصحى واللهجات العربية المتنوعة.
  - **تصميم الأصوات بالأوامر النصية**: إمكانية توليد صوت مخصص عبر تحديد الجنس (ذكر / أنثى)، الفئة العمرية (طفل، شاب، متوسط العمر، مسن)، طبقة الصوت، الأسلوب، واللهجة مباشرة دون الحاجة لأي تدريب مسبق.
  - **استنساخ الأصوات اللحظي**: استخراج البصمة الصوتية من مقطع صوتي نقي مدته 3 إلى 10 ثوانٍ مع حفظها بصيغة بصمة قابلة لإعادة الاستخدام.
- **محرك الأصوات الاستوديو (Coqui XTTS v2)**:
  - مكتبة مدمجة تضم 14 صوتاً استوديو عالي النقاء (6 أصوات رجالية، 8 أصوات نسائية) مسجلة بدقة 24 كيلوهرتز.
  - دعم توليد النصوص الطويلة والمقالات دون اقتطاع عبر تقسيم الجمل الذكي.

### 2. معالجة الصوت الإذاعية وهندسة الماسترينغ
تم دمج خط معالجة الصوت الرقمي المتقدم المقتبس من مشروع المطور بالاش ديب:
- **موازنة مستوى الصوت القياسي (EBU R128)**: ضبط الصوت عند معيار إذاعي محدد مع حد أمان لمنع تضخيم الضوضاء الخلفية.
- **ضغط النطاق الديناميكي الناعم**: تنقية طبقات الصوت وإبراز الكلمات بوضوح فائق دون تشويش.
- **تلاشي النهايات وإزالة الطقطقة**: معالجة نهايات المقاطع الصوتية المجزأة لضمان انتقال صوتي انسيابي خالي من أي عيوب أو فرقعات صوتية.
- **أنماط الماسترينغ الصوتية**:
  - `📻 استوديو إذاعي`: معيار البث الإذاعي والبودكاست - دافئ ومضغوط وواضح بنقاء عالي.
  - `🎙️ صوت بودكاست`: صوت قريب ونقي ومخصص للبودكاست والسرد الصوتي.
  - `☕ دافئ ورخيم`: نبرة دافئة ورخيمة تناسب الروايات والكتب الصوتية.
  - `✨ ناصع ومشرق`: وضوح عالي لمخارج الحروف مع طبقات صوتية مشرقة.
  - `🔇 الصوت الخام الأصلي`: الصوت الخارج من المحرك مباشرة بدون أي معالجة.

### 3. دعم وسوم الأداء الصوتي والتعبيرات
- التحكم بسرعة أجزاء معينة من النص: `[slow]بطيء[/slow]` أو `[fast]سريع[/fast]`.
- الوقفات والسكوت المؤقت: `[pause]` أو وقفات مخصصة بالمللي ثانية.
- التعبيرات الصوتية غير اللفظية: الضحك `[laughter]`، الهمس `[whisper]`، التنهد `[sigh]`.

### 4. خادم بروتوكول سياق النماذج للوكلاء الأذكياء (MCP Server)
يتضمن المشروع خادماً معيارياً مدمجاً يتيح للمساعدين الأذكياء وأنظمة الأتمتة (مثل Claude Code و Cursor و Antigravity) الاتصال مباشرة بالمشروع وتوليد الأصوات برمجياً من خلال أدوات استدعاء معيارية عبر الطرفية أو بروتوكول تدفق الأحداث.

### 5. واجهة مستخدم رسومية متطورة
- **تعريب فوري شامل (عربي ⇄ إنجليزي)**: تبديل لغة الواجهة والقوائم ومحاذاة النصوص بنقرة زر واحدة دون الحاجة لإعادة تشغيل البرنامج.
- **كاشف العتاد والتسريع الآلي**: رصد بطاقة الرسوميات (NVIDIA CUDA) والتبديل التلقائي إلى المعالج المركزي في حال عدم توفر كرت شاشة مخصص.
- **بطاقات استماع وتصدير**: مشغل صوتي تفاعلي لكل رد صوتي مع إمكانية التقديم والتأخير وحفظ الملف بصيغة WAV في أي مسار يختاره المستخدم.

---

## متطلبات التشغيل

| المكون | الحد الأدنى (وضع المعالج) | الموصى به (تسريع كرت الشاشة) |
| :--- | :--- | :--- |
| **نظام التشغيل** | ويندوز 10 / 11 (64 بت)، لينكس، ماك | ويندوز 10 / 11 (64 بت) |
| **المعالج** | معالج رباعي النواة (Intel i5 أو AMD Ryzen 5) | معالج حديث بـ 6 أنوية أو أكثر |
| **الذاكرة العشوائية** | **8 جيجابايت** | **16 إلى 32 جيجابايت** |
| **كرت الشاشة** | *لا يشترط وجود كرت مخصص* (يعمل على المعالج) | كرت NVIDIA بذاكرة **6 جيجابايت أو أعلى** |
| **المساحة التخزينية** | **4 جيجابايت** | **8 جيجابايت SSD** |
| **بيئة التشغيل** | بايثون 3.10 إلى 3.12 | بايثون 3.10 إلى 3.12 مع بيئة CUDA |

---

## التشغيل السريع

### تشغيل الواجهة الرسومية:
```bash
python main.py
```

### تشغيل خادم الوكلاء الأذكياء (MCP):
```bash
python mcp_server.py
```

### التوليد عبر سطر الأوامر (CLI):
```bash
python cli_synthesizer.py --text "مرحباً بكم في استوديو الصوت" --lang ar --dsp broadcast --output audio.wav
```

---

## شكر وتقدير للمشاريع المفتوحة المصدر

ندين بالفضل والشكر للمشاريع والباحثين المتميزين:
1. **بالاش ديب (Palash Deb)**: مؤلف مشروع `debpalash/VoiceStudio` لمعالجة الماسترينغ الإذاعي وأدوات الوكلاء الأذكياء.
2. **فريق أبحاث k2-fsa**: مؤلفو مشروع `k2-fsa/OmniVoice` لمحرك الانتشار الصوتي لأكثر من 600 لغة.
3. **فريق Coqui AI**: مؤلفو `Coqui TTS` لتقنية `XTTS v2` واستنساخ الأصوات.
4. **أسامة الزهراني**: البنية البرمجية، الربط المزدوج للمحركات، تعريب الواجهات، وإدارة المشروع.
