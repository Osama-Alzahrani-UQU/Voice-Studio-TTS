# Voice Studio — استوديو الصوت

تطبيق سطح مكتب لتحويل النصوص والمقالات إلى كلام طبيعي باللغتين **العربية** و**الإنجليزية** باستخدام محرك **Coqui XTTS v2**.

A desktop application for long-form **Arabic & English** Text-to-Speech synthesis powered by **Coqui XTTS v2** and **CustomTkinter**.

---

## المميزات | Features

- **تبديل فوري للغة (العربية ⇄ English) | Instant Bilingual UI & Synthesis**:
  - تبديل لغة الواجهة والقوائم ومحرك النطق بين العربية والإنجليزية مباشرة من الشريط العلوي.
  - Switch both interface localization (RTL/LTR) and speech synthesis language directly from the top toolbar.
- **معالجة النصوص الطويلة | Long-Form Text Processing**:
  - تقسيم تلقائي للفقرات والجمل الطويلة (`text_splitter.py`) مع ضبط النص العربي (`arabic_text_processor.py`) ودمج المقاطع الصوتية.
  - Intelligent sentence segmentation (`text_splitter.py`) and Arabic phonetic normalization (`arabic_text_processor.py`) with seamless audio merging.
- **أصوات استوديو مصنفة | Studio Voice Profiles**:
  - مجموعة من الأصوات الرجالية والنسائية مع عينات صوتية مرجعية مدمجة (`24kHz`).
  - Curated male and female voice profiles with bundled `24kHz` reference samples.
- **مشغل مدمج وتصدير WAV | Embedded Player & WAV Export**:
  - تشغيل وإيقاف مؤقت وتصدير مباشر للملفات الصوتية بصيغة `WAV`.
  - Built-in playback controls and direct `WAV` audio export.

---

## التشغيل | Quick Start

### 1. إعداد البيئة الافتراضية | Environment Setup
```bat
create_venv.bat
```
أو عبر `pip`:
```bash
pip install -r requirements.txt
pip install coqui-tts
```

### 2. تشغيل التطبيق | Run Application
```bat
run.bat
```
أو عبر بايثون:
```bash
python main.py
```

### 3. بناء النسخة التنفيذية (`.exe`) | Build Standalone Executable
```bat
build.bat
```
المسار الناتج:
```text
dist/LocalTTS_App/LocalTTS_App.exe
```

---

## الترخيص | License

MIT License — [LICENSE](LICENSE)
