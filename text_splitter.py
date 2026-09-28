"""
text_splitter.py - Intelligent Long-Text Sentence Chunker
-------------------------------------------------------
Splits long multi-paragraph Arabic and English texts into natural sentence
chunks for exact, untruncated speech synthesis.
"""

import re
from typing import List

def split_text_into_chunks(text: str, max_chars: int = 180) -> List[str]:
    """
    Splits text into chunks by sentence delimiters and punctuation.
    Guarantees no chunk exceeds max_chars while preserving full words.
    
    Args:
        text: Input string (Arabic or English)
        max_chars: Target max character limit per chunk
        
    Returns:
        List of clean, untruncated text chunks
    """
    if not text or not text.strip():
        return []

    # Clean text whitespace
    text = text.strip()

    # Split by major sentence boundaries (Arabic: ؟ ؛ \n . ! | English: . ! ? ; \n)
    raw_sentences = re.split(r'(?<=[.!?؛؟\n])\s+', text)
    
    chunks = []
    
    for sentence in raw_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If sentence is within max_chars, add directly
        if len(sentence) <= max_chars:
            chunks.append(sentence)
        else:
            # Sub-split long sentence by clause boundaries (commas, semicolons, dashes)
            sub_clauses = re.split(r'(?<=[,،:-])\s+', sentence)
            current_chunk = ""
            
            for clause in sub_clauses:
                clause = clause.strip()
                if not clause:
                    continue
                    
                if len(current_chunk) + len(clause) + 1 <= max_chars:
                    current_chunk = f"{current_chunk} {clause}".strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    # If a single clause is still longer than max_chars, split by word count
                    if len(clause) > max_chars:
                        words = clause.split()
                        word_chunk = ""
                        for word in words:
                            if len(word_chunk) + len(word) + 1 <= max_chars:
                                word_chunk = f"{word_chunk} {word}".strip()
                            else:
                                if word_chunk:
                                    chunks.append(word_chunk)
                                word_chunk = word
                        if word_chunk:
                            chunks.append(word_chunk)
                        current_chunk = ""
                    else:
                        current_chunk = clause
                        
            if current_chunk:
                chunks.append(current_chunk)
                
    return [c for c in chunks if c and len(c.strip()) > 0]


if __name__ == "__main__":
    test_arabic = "مرحباً بكم في التطبيق المستقل لتوليد الصوت. هذا نظام متقدم يعمل بالكامل بدون اتصال بالإنترنت، حيث يقوم بمعالجة النصوص الطويلة وتقسيمها بدقة عالية دون حذف أي كلمة! يرجى الاستمتاع بالتوليد الصوتي."
    res = split_text_into_chunks(test_arabic, max_chars=80)
    print(f"Split test ({len(res)} chunks):")
    for i, c in enumerate(res):
        print(f" Chunk {i+1} ({len(c)} chars): {c}")
