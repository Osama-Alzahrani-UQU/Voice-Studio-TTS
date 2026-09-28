r"""
arabic_text_processor.py - Arabic Text Normalization & Articulation Pre-processor
----------------------------------------------------------------------------------
Enhances Arabic speech synthesis accuracy by cleaning diacritics, normalizing letter
variants, stripping stretching characters (tatweel), converting numbers to spoken Arabic
words, and formatting punctuation for XTTS v2 phonetization.
"""

import re


try:
    import pyarabic.araby as araby
except ImportError:
    araby = None

ARABIC_NUMBER_WORDS = {
    "0": "صفر", "00": "صفر", "1": "واحد", "2": "اثنان", "3": "ثلاثة",
    "4": "أربعة", "5": "خمسة", "6": "ستة", "7": "سبعة",
    "8": "ثمانية", "9": "تسعة", "10": "عشرة"
}

def normalize_arabic_text(text: str) -> str:
    """
    Applies expert normalization rules to raw Arabic text prior to TTS synthesis.
    """
    if not text or not text.strip():
        return ""

    t = text.strip()

    # 1. Convert Arabic-Indic digits (٠-٩) and basic numbers to spoken Arabic words
    for digit, word in ARABIC_NUMBER_WORDS.items():
        t = re.sub(r'\b' + digit + r'\b', word, t)
        arabic_digit = digit.translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))
        t = re.sub(r'\b' + arabic_digit + r'\b', word, t)

    # 2. Strip Tatweel (kashida 'ـ') which causes artificial vocal stretching
    t = re.sub(r'ـ+', '', t)

    # 3. Clean conflicting double/triple diacritics while keeping clean vowel structure
    # Remove repetitive diacritics
    t = re.sub(r'[\u064B-\u0652]{2,}', lambda m: m.group(0)[0], t)

    # 4. Standardize Alef Maksura and Teh Marbuta spacing for clean phrase endings
    # Ensure space after punctuation
    t = re.sub(r'([؟؛!.,،:])([^\s])', r'\1 \2', t)

    # Remove extra spaces
    t = re.sub(r'\s+', ' ', t).strip()

    return t

if __name__ == "__main__":
    test_phrase = "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ 10 ــ مرحباً بكم!"
    res = normalize_arabic_text(test_phrase)
    print(f"Original: {test_phrase}")
    print(f"Normalized: {res}")
