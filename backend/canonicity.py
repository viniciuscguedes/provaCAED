"""
Módulo de Análise de Canonicidade Silábica em Português.

Uma palavra canônica é definida como aquela composta exclusivamente por sílabas do tipo CV (Consoante + Vogal).
Exemplos de palavras canônicas: cabeça (ca-be-ça), canela (ca-ne-la), janela (ja-ne-la), luta (lu-ta), sopa (so-pa).
Exemplos de palavras não canônicas: abajur (a-ba-jur), lápis (lá-pis), cansado (can-sa-do), asa (a-sa), alheio (al-hei-o).
"""

import re
import unicodedata

VOWELS = set("aeiouáéíóúâêôãõàü")
CONSONANTS = set("bcdfghjklmnpqrstvwxyzç")

def normalize_text(text: str) -> str:
    """Remove caracteres especiais e converte para minúsculas."""
    return text.lower().strip()

def get_word_cv_pattern(word: str) -> str:
    """
    Mapeia cada caractere de uma palavra para 'C' (Consoante), 'V' (Vowel/Vogal), ou 'X' (Outro).
    """
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
    """
    Verifica se uma palavra é estritamente canônica (composta apenas por repetições de sílabas CV).
    Em termos de padrão de caracteres, uma palavra canônica possui sequência alternada C-V-C-V...
    começando com Consoante, terminando com Vogal e com número par de letras > 0.
    """
    word_clean = re.sub(r"[^a-zA-ZáéíóúâêôãõàüçÁÉÍÓÚÂÊÔÃÕÀÜÇ]", "", word.lower())
    if not word_clean:
        return False
    
    cv_pattern = get_word_cv_pattern(word_clean)
    
    # Uma palavra com todas as sílabas CV tem a forma C-V-C-V...C-V
    # O tamanho precisa ser par e corresponder exatamente a "CV" repetido
    if len(cv_pattern) % 2 != 0:
        return False
        
    expected_pattern = "CV" * (len(cv_pattern) // 2)
    return cv_pattern == expected_pattern

def syllabify_portuguese(word: str) -> list[str]:
    """
    Divisor silábico heurístico para português para visualização detalhada.
    """
    word_clean = re.sub(r"[^a-zA-ZáéíóúâêôãõàüçÁÉÍÓÚÂÊÔÃÕÀÜÇ]", "", word.lower())
    if not word_clean:
        return []
    
    # Regra simples de separação silábica aproximada
    syllables = []
    curr = ""
    i = 0
    n = len(word_clean)
    
    while i < n:
        curr += word_clean[i]
        # Se formou um padrão CV básico e o próximo é uma consoante seguida de vogal, ou fim de palavra
        if len(curr) >= 2 and curr[-2] in CONSONANTS and curr[-1] in VOWELS:
            if i + 1 < n and word_clean[i+1] in CONSONANTS:
                # Checa se o próximo grupo é CV
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
    """
    Analisa todo um texto e retorna métricas detalhadas de canonicidade.
    """
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
