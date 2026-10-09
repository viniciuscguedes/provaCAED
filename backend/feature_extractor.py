import re
import numpy as np
import pandas as pd
from backend.canonicity import analyze_text_canonicity, VOWELS

def count_syllables_word(word: str) -> int:
    word_clean = re.sub(r"[^a-zA-Záéíóúâêôãõàüç]", "", word.lower())
    if not word_clean:
        return 0
    vowel_groups = re.findall(r"[aeiouáéíóúâêôãõàü]+", word_clean)
    return max(1, len(vowel_groups))

def extract_text_features(text: str) -> dict:
    clean_text = text.strip()
    words = re.findall(r"\b[a-zA-ZáéíóúâêôãõàüçÁÉÍÓÚÂÊÔÃÕÀÜÇ]+\b", clean_text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", clean_text) if s.strip()]
    
    total_chars = len(clean_text)
    total_words = len(words)
    total_sentences = max(1, len(sentences))
    
    if total_words == 0:
        return {
            "canonicity_ratio": 0.0,
            "canonical_words_count": 0,
            "word_count": 0,
            "char_count": 0,
            "avg_word_length": 0.0,
            "sentence_count": total_sentences,
            "avg_sentence_length": 0.0,
            "avg_syllables_per_word": 0.0,
            "flesch_reading_ease": 0.0,
            "complex_word_ratio": 0.0,
            "type_token_ratio": 0.0,
            "punctuation_ratio": 0.0,
            "numeric_symbol_ratio": 0.0
        }
    
    canonicity_info = analyze_text_canonicity(clean_text)
    canonicity_ratio = canonicity_info["canonicity_ratio"]
    canonical_count = canonicity_info["canonical_words_count"]
    
    avg_word_length = sum(len(w) for w in words) / total_words
    avg_sentence_length = total_words / total_sentences
    
    syllable_counts = [count_syllables_word(w) for w in words]
    avg_syllables_per_word = sum(syllable_counts) / total_words if total_words > 0 else 0.0
    
    flesch = 248.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    
    complex_words = [w for w in words if len(w) > 7]
    complex_word_ratio = len(complex_words) / total_words
    
    unique_words = set(w.lower() for w in words)
    type_token_ratio = len(unique_words) / total_words
    
    punct_count = len(re.findall(r"[,;:()\"'—–-]", clean_text))
    punctuation_ratio = punct_count / total_chars if total_chars > 0 else 0.0
    
    num_symbol_count = len(re.findall(r"[0-9=+\-*/%_]", clean_text))
    numeric_symbol_ratio = num_symbol_count / total_chars if total_chars > 0 else 0.0
    
    return {
        "canonicity_ratio": round(canonicity_ratio, 4),
        "canonical_words_count": canonical_count,
        "word_count": total_words,
        "char_count": total_chars,
        "avg_word_length": round(avg_word_length, 2),
        "sentence_count": total_sentences,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        "flesch_reading_ease": round(flesch, 2),
        "complex_word_ratio": round(complex_word_ratio, 4),
        "type_token_ratio": round(type_token_ratio, 4),
        "punctuation_ratio": round(punctuation_ratio, 4),
        "numeric_symbol_ratio": round(numeric_symbol_ratio, 4)
    }

def extract_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """Extrai features numéricas para um DataFrame contendo uma coluna 'text'."""
    feature_rows = []
    for text in df["text"]:
        feature_rows.append(extract_text_features(text))
    return pd.DataFrame(feature_rows)
