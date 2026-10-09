import re
import unicodedata

VOWELS = set("aeiouáéíóúâêôãõàü")
CONSONANTS = set("bcdfghjklmnpqrstvwxyzç")

def normalize_text(text: str) -> str:
    return text.lower().strip()

def get_word_cv_pattern(word: str) -> str:
    word_clean = normalize_text(word)
    pattern = []
    for char in word_clean:
        if char in VOWELS:
            pattern.append("V")
        elif char in CONSONANTS:
            pattern.append("C")
        else:
            pattern.append("X")
    return "".join(pattern)

def is_canonical_word(word: str) -> bool:
    word_clean = re.sub(r"[^a-zA-ZáéíóúâêôãõàüçÁÉÍÓÚÂÊÔÃÕÀÜÇ]", "", word.lower())
    if not word_clean:
        return False
    
    cv_pattern = get_word_cv_pattern(word_clean)
    if len(cv_pattern) % 2 != 0:
        return False
        
    expected_pattern = "CV" * (len(cv_pattern) // 2)
    return cv_pattern == expected_pattern

def syllabify_portuguese(word: str) -> list[str]:

    word_clean = re.sub(r"[^a-zA-ZáéíóúâêôãõàüçÁÉÍÓÚÂÊÔÃÕÀÜÇ]", "", word.lower())
    if not word_clean:
        return []
    
    syllables = []
    curr = ""
    i = 0
    n = len(word_clean)
    
    while i < n:
        curr += word_clean[i]
        if len(curr) >= 2 and curr[-2] in CONSONANTS and curr[-1] in VOWELS:
            if i + 1 < n and word_clean[i+1] in CONSONANTS:
                if i + 2 < n and word_clean[i+2] in VOWELS:
                    syllables.append(curr)
                    curr = ""
            elif i + 1 == n:
                syllables.append(curr)
                curr = ""
        i += 1
    
    if curr:
        if syllables:
            syllables[-1] += curr
        else:
            syllables.append(curr)
            
    return syllables

def analyze_text_canonicity(text: str) -> dict:
    words = re.findall(r"\b[a-zA-ZáéíóúâêôãõàüçÁÉÍÓÚÂÊÔÃÕÀÜÇ]+\b", text)
    if not words:
        return {
            "total_words": 0,
            "canonical_words_count": 0,
            "non_canonical_words_count": 0,
            "canonicity_ratio": 0.0,
            "canonical_words": [],
            "non_canonical_words": []
        }
    
    canonical_list = []
    non_canonical_list = []
    
    for w in words:
        if is_canonical_word(w):
            canonical_list.append(w)
        else:
            non_canonical_list.append(w)
            
    total = len(words)
    can_count = len(canonical_list)
    ratio = can_count / total if total > 0 else 0.0
    
    return {
        "total_words": total,
        "canonical_words_count": can_count,
        "non_canonical_words_count": len(non_canonical_list),
        "canonicity_ratio": round(ratio, 4),
        "canonical_words": canonical_list,
        "non_canonical_words": non_canonical_list
    }
