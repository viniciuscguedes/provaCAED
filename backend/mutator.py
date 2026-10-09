"""
Módulo de Algoritmos de Mutação Textual.
Implementa as 3 operações de mutação exigidas no edital:
1. Troca de Palavras (Sinônimos e Antônimos)
2. Troca de Gênero (Masculino <-> Feminino)
3. Paráfrase (Transformações sintáticas, voz passiva/ativa, deslocamento de termos temporais e apostos).
"""

import re
import random

# Dicionário de Sinônimos e Antônimos em Português para substituição aleatória
PORTUGUESE_SYNONYMS = {
    "pequeno": ["curto", "reduzido", "minúsculo"],
    "grande": ["enorme", "amplo", "extenso"],
    "bonito": ["bello", "atraente", "formoso"],
    "famoso": ["célebre", "renomado", "ilustre"],
    "criança": ["infante", "jovem", "menino"],
    "aluno": ["estudante", "aprendiz", "discente"],
    "professor": ["mestre", "docente", "educador"],
    "fazer": ["construir", "realizar", "elaborar"],
    "dificuldade": ["complexidade", "obstáculo", "desafio"],
    "fácil": ["simples", "descomplicado", "acessível"],
    "difícil": ["complexo", "arduo", "complicado"],
    "começar": ["iniciar", "principiar"],
    "ajudar": ["auxiliar", "colaborar", "amparar"],
    "usar": ["utilizar", "empregar"],
    "bom": ["excelente", "ótimo", "favorável"],
    "novo": ["recente", "inédito", "moderno"],
    "verificar": ["checar", "examinar", "constatar"],
    "texto": ["escrito", "narrativa", "trecho"],
    "livro": ["obra", "exemplar", "volume"],
    "estudo": ["análise", "pesquisa", "investigação"]
}

PORTUGUESE_ANTONYMS = {
    "pequeno": "grande",
    "grande": "pequeno",
    "fácil": "difícil",
    "difícil": "fácil",
    "bonito": "feio",
    "famoso": "desconhecido",
    "bom": "mau",
    "novo": "antigo",
    "alto": "baixo",
    "forte": "fraco",
    "claro": "escuro",
    "rápido": "lento",
    "iniciar": "terminar",
    "alegre": "triste"
}

# Mapeamento bidirecional para troca de gênero
GENDER_MAP = {
    # Artigos e Pronomes
    "o": "a", "a": "o",
    "os": "as", "as": "os",
    "um": "uma", "uma": "um",
    "uns": "umas", "umas": "uns",
    "ele": "ela", "ela": "ele",
    "eles": "elas", "elas": "eles",
    "este": "esta", "esta": "este",
    "estes": "estas", "estas": "estes",
    "aquele": "aquela", "aquela": "aquele",
    "aqueles": "aquela", "aquela": "aqueles",
    "meu": "minha", "minha": "meu",
    "meus": "minhas", "minhas": "meus",
    "seu": "sua", "sua": "seu",
    "seus": "suas", "suas": "seus",
    # Substantivos
    "menino": "menina", "menina": "menino",
    "meninos": "meninas", "meninas": "meninos",
    "aluno": "aluna", "aluna": "aluno",
    "alunos": "alunas", "alunas": "alunos",
    "professor": "professora", "professora": "professor",
    "professores": "professoras", "professoras": "professores",
    "cantor": "cantora", "cantora": "cantor",
    "cantores": "cantoras", "cantoras": "cantores",
    "homem": "mulher", "mulher": "homem",
    "homens": "mulheres", "mulheres": "homens",
    "pai": "mãe", "mãe": "pai",
    "filho": "filha", "filha": "filho",
    "filhos": "filhas", "filhas": "filhos",
    "irmão": "irmã", "irmã": "irmão",
    "gato": "gata", "gata": "gato",
    "cachorro": "cadela", "cadela": "cachorro",
    "médico": "médica", "médica": "médico",
    "autor": "autora", "autora": "autor",
    "leitor": "leitora", "leitora": "leitor",
    # Adjetivos
    "famoso": "famosa", "famosa": "famoso",
    "famosos": "famosas", "famosas": "famosos",
    "bonito": "bonita", "bonita": "bonito",
    "bonitos": "bonitas", "bonitas": "bonitos",
    "novo": "nova", "nova": "novo",
    "novos": "novas", "novas": "novos",
    "pequeno": "pequena", "pequena": "pequeno",
    "pequenos": "pequenas", "pequenas": "pequenos",
    "alto": "alta", "alta": "alto",
    "amado": "amada", "amada": "amado",
    "dedicado": "dedicada", "dedicada": "dedicado"
}

def mutate_synonyms_antonyms(text: str, mode: str = "synonym", intensity: float = 0.3) -> str:
    """
    Substitui aleatoriamente palavras por sinônimos ou antônimos com base na intensidade.
    """
    words = text.split()
    mutated = []
    
    for word in words:
        clean_word = re.sub(r"[^\wáéíóúâêôãõàüçÁÉÍÓÚÂÊÔÃÕÀÜÇ]", "", word.lower())
        punct_before = word[:len(word) - len(word.lstrip(".,!?;:()\"'"))]
        punct_after = word[len(word.rstrip(".,!?;:()\"'")):]
        
        should_mutate = random.random() < intensity
        
        new_word = None
        if should_mutate:
            if mode == "synonym" and clean_word in PORTUGUESE_SYNONYMS:
                candidates = PORTUGUESE_SYNONYMS[clean_word]
                new_word = random.choice(candidates)
            elif mode == "antonym" and clean_word in PORTUGUESE_ANTONYMS:
                new_word = PORTUGUESE_ANTONYMS[clean_word]
                
        if new_word:
            if word[0].isupper():
                new_word = new_word.capitalize()
            mutated.append(punct_before + new_word + punct_after)
        else:
            mutated.append(word)
            
    return " ".join(mutated)

def mutate_gender(text: str) -> str:
    """
    Troca o gênero gramatical de frases (Masculino <-> Feminino).
    Ex: "A cantora era famosa" => "O cantor era famoso"
    """
    words = text.split()
    mutated = []
    
    for word in words:
        clean_word = re.sub(r"[^\wáéíóúâêôãõàüçÁÉÍÓÚÂÊÔÃÕÀÜÇ]", "", word.lower())
        punct_before = word[:len(word) - len(word.lstrip(".,!?;:()\"'"))]
        punct_after = word[len(word.rstrip(".,!?;:()\"'")):]
        
        if clean_word in GENDER_MAP:
            swapped = GENDER_MAP[clean_word]
            if word[0].isupper():
                swapped = swapped.capitalize()
            mutated.append(punct_before + swapped + punct_after)
        else:
            mutated.append(word)
            
    return " ".join(mutated)

def mutate_paraphrase(text: str) -> str:
    """
    Aplica regras de paráfrase e reestruturação sintática:
    1. Voz passiva para voz ativa: 'O texto foi lido pelo aluno' => 'O aluno leu o texto'
    2. Posição de aposto: 'O cantor Roberto Carlos fez aniversário' => 'Roberto Carlos, o cantor, fez aniversário'
    3. Expressões temporais: 'Há duas semanas atrás estava chovendo' => 'Estava chovendo há duas semanas atrás'
    """
    sentences = re.split(r"([.!?]+)", text)
    result_sentences = []
    
    for i in range(0, len(sentences), 2):
        sentence = sentences[i].strip()
        sep = sentences[i+1] if i+1 < len(sentences) else ""
        
        if not sentence:
            continue
            
        modified = False
        
        # Regra 1: Voz Passiva -> Voz Ativa
        # "O/A [Subst1] foi [verb_particípio] pelo/pela [Subst2]" => "O/A [Subst2] [verb_passado] o/a [Subst1]"
        m_passive = re.search(r"^(O|A|Os|As)\s+(.+?)\s+foi\s+(lido|escrito|avaliado|criado|feito)\s+pel[oa]s?\s+(.+)$", sentence, re.IGNORECASE)
        if m_passive:
            art1, obj, part, subj = m_passive.groups()
            verb_map = {
                "lido": "leu", "escrito": "escreveu", "avaliado": "avaliou",
                "criado": "criou", "feito": "fez"
            }
            past_verb = verb_map.get(part.lower(), "modificou")
            sentence = f"{subj.capitalize()} {past_verb} {art1.lower()} {obj}"
            modified = True

        # Regra 2: Expressão temporal inicial -> Final da frase
        # "Há [tempo] atrás [oração]" => "[oração] há [tempo] atrás"
        if not modified:
            m_time = re.search(r"^(Há\s+[\w\s]+\s+atrás),?\s+(.+)$", sentence, re.IGNORECASE)
            if m_time:
                time_expr, clause = m_time.groups()
                sentence = f"{clause.capitalize()} {time_expr.lower()}"
                modified = True
                
        # Regra 3: Inversão de Aposto / Título
        # "O [cargo] [Nome Próprio] [verbo...]" => "[Nome Próprio], o [cargo], [verbo...]"
        if not modified:
            m_app = re.search(r"^(O|A)\s+(cantor|professor|aluno|cientista|médico|autor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(.+)$", sentence)
            if m_app:
                art, title, name, rest = m_app.groups()
                sentence = f"{name}, {art.lower()} {title}, {rest}"
                modified = True
                
        # Regra 4: Se nenhuma regra específica aplicou, inverte orações subordinadas com vírgulas se houver
        if not modified and "," in sentence:
            parts = sentence.split(",", 1)
            if len(parts) == 2 and len(parts[0].split()) > 2 and len(parts[1].split()) > 2:
                sentence = f"{parts[1].strip().capitalize()}, {parts[0].strip().lower()}"

        result_sentences.append(sentence + sep)
        
    return " ".join(result_sentences)

def apply_mutations(text: str, operations: list[str], intensity: float = 0.3) -> dict:
    """
    Aplica uma sequência de operações de mutação ao texto e retorna o resultado.
    """
    current_text = text
    applied_ops = []
    
    for op in operations:
        if op == "synonym":
            current_text = mutate_synonyms_antonyms(current_text, mode="synonym", intensity=intensity)
            applied_ops.append("Substituição de Sinônimos")
        elif op == "antonym":
            current_text = mutate_synonyms_antonyms(current_text, mode="antonym", intensity=intensity)
            applied_ops.append("Substituição de Antônimos")
        elif op == "gender":
            current_text = mutate_gender(current_text)
            applied_ops.append("Troca de Gênero Gramatical")
        elif op == "paraphrase":
            current_text = mutate_paraphrase(current_text)
            applied_ops.append("Paráfrase e Reestruturação Sintática")
            
    return {
        "original_text": text,
        "mutated_text": current_text,
        "operations_applied": applied_ops
    }
