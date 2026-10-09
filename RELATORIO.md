# Relatório Técnico e Metodológico - Processo Seletivo CAEd (Edital 024-2026)

## Sistema Inteligente de Avaliação de Complexidade Leitora e Gerador de Mutação Textual

**Candidato:** Seleção Desenvolvedor CAEd  
**Data:** Outubro de 2026  
**Repositório:** [RepositorioCAED](file:///home/vinicius/Documentos/RepositorioCAED)

---

## 1. Introdução e Visão Geral do Problema

A avaliação da capacidade leitora de estudantes em diferentes etapas do ensino fundamental e médio é um dos pilares das pesquisas e diagnósticos realizados pelo CAEd. Uma das formas clássicas de avaliar a fluência leitora é a **decodificação**, isto é, a habilidade da criança em ler sequências de palavras com diferentes níveis de complexidade gramatical e vocabular.

Com a expansão da avaliação para diversos estados brasileiros, a elaboração manual de itens e narrativas curtas torna-se um gargalo, dado que textos já aplicados não podem ser reutilizados em edições futuras por questões de sigilo e integridade pedagógica.

Para resolver este desafio, construímos uma **solução computacional completa** composta por:
1. **Modelo de Predição de Complexidade Leitora**: Classificador treinado com machine learning para categorizar textos em 4 níveis de escolaridade (*Ensino Fundamental I*, *Ensino Fundamental II*, *Ensino Médio* e *Ensino Superior*).
2. **Algoritmo de Canonicidade Silábica (Padrão CV)**: Heurística rigorosa para quantificar a presença de sílabas canônicas (Consoante + Vogal) em textos em português.
3. **Motor de Mutação Textual Heurística**: Algoritmo gerador que altera textos através de troca de sinônimos/antônimos, flexão de gênero gramatical e paráfrases sintáticas (inversão de voz passiva/ativa, deslocamento de apostos e adjuntos temporais).
4. **Aplicação Web Interativa**: Interface gráfica moderníssima com estética *glassmorphic*, análise visual de canonicidade, estúdio de mutação lado a lado com diff visual e dashboard comparativo de modelos.

---

## 2. Algoritmo de Canonicidade Silábica (Padrão CV)

### 2.1 Conceito e Definição
No aprendizado inicial da leitura (Ensino Fundamental I), palavras formadas exclusivamente por sílabas do tipo **Consoante + Vogal (CV)** são consideradas **canônicas**, pois exigem menor esforço de decodificação fonológica.

Exemplos de palavras canônicas:
- `ca-be-ça` &rarr; C V C V C V
- `ca-ne-la` &rarr; C V C V C V
- `ja-ne-la` &rarr; C V C V C V
- `lu-ta` &rarr; C V C V
- `so-pa` &rarr; C V C V

Exemplos de palavras não canônicas:
- `abajur` &rarr; Inicia por vogal (V) e possui sílaba CVC final (`jur`).
- `lápis` &rarr; Possui sílaba CVC final (`pis`).
- `cansado` &rarr; Possui sílaba CVC inicial (`can`).
- `asa` &rarr; Inicia por vogal (V).
- `alheio` &rarr; Encontro vocálico/consonantal complexo.

### 2.2 Formulação do Algoritmo e Regra Alternada C-V
Matematicamente, uma palavra é estritamente composta por sílabas CV se, e somente se, o mapeamento de seus caracteres para os conjuntos de Consoantes ($C$) e Vogais ($V$) formar uma sequência que satisfaz o padrão regular:

$$\text{Padrão Canônico} = \text{^(CV)+$}$$

O algoritmo desenvolvido no módulo [`backend/canonicity.py`](file:///home/vinicius/Documentos/RepositorioCAED/backend/canonicity.py) executa as seguintes etapas:
1. Normalização do texto (remoção de pontuações e acentos gráficos mantendo a estrutura da letra base).
2. Mapeamento de cada caractere $c_i \in W$:
   - $c_i \in \{a, e, i, o, u, \dots\} \implies V$
   - $c_i \in \{b, c, d, f, g, h, j, k, l, m, n, p, q, r, s, t, v, w, x, y, z, ç\} \implies C$
3. Validação do comprimento (deve ser par) e verificação de igualdade direta com $(CV)^{|W|/2}$.
4. Cálculo da taxa de canonicidade do texto:

$$\text{Canonicity Ratio} = \frac{\text{Total de Palavras Canônicas}}{\text{Total de Palavras do Texto}}$$

---

## 3. Dataset e Engenharia de Atributos (Features)

### 3.1 Caracterização do Dataset
O dataset disponibilizado contém **2.076 documentos de texto** distribuídos nas seguintes categorias:
- **Ensino Fundamental I**: 297 documentos (Textos mais curtos, vocabulário simples e alta canonicidade).
- **Ensino Fundamental II**: 325 documentos.
- **Ensino Médio**: 628 documentos.
- **Ensino Superior**: 826 documentos (Textos acadêmicos, termos técnicos e sintaxe elaborada).

### 3.2 Extração de Features
Desenvolvemos uma abordagem híbrida no módulo [`backend/feature_extractor.py`](file:///home/vinicius/Documentos/RepositorioCAED/backend/feature_extractor.py), combinando **13 atributos estilístico-gramaticais** com **vetorização TF-IDF**:

1. **Taxa de Canonicidade Silábica (`canonicity_ratio`)**: Métrica autoral exigida no edital.
2. **Índice de Legibilidade Flesch-Szigriszt para Português**:
   $$\text{Flesch} = 248.835 - (1.015 \times \text{Média de Palavras/Frase}) - (84.6 \times \text{Média de Sílabas/Palavra})$$
3. **Métricas Estruturais**: Comprimento médio das palavras, extensão média das frases, proporção de palavras complexas (mais de 7 letras) e diversidade lexical (*Type-Token Ratio*).
4. **Marcadores Estilísticos e Simbólicos**: Densidade de pontuações e proporção de símbolos numéricos/fórmulas (altamente presentes nos textos de Ensino Médio e Superior).
5. **Representações TF-IDF Híbridas**:
   - TF-IDF de N-gramas de palavras (1 a 2) &rarr; Captura vocabulário e domínio temático.
   - TF-IDF de N-gramas de caracteres (3 a 5) &rarr; Captura sufixos, radicais e padrões morfológicos.

---

## 4. Experimentos e Avaliação de Modelos de Machine Learning

Dividimos o dataset em conjuntos de Treino (80%) e Teste (20%) com amostragem estratificada mantendo as proporções das 4 classes. Testamos 5 algoritmos clássicos e ensemble:

| Modelo | Acurácia | F1-Score (Macro) | F1-Score (Weighted) | Precisão | Revocação |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Linear SVM (Calibrado)** | **91,83%** | **0,9018** | **0,9180** | **0,9201** | **0,9183** |
| **Regressão Logística** | 89,90% | 0,8776 | 0,8985 | 0,9010 | 0,8990 |
| **Random Forest** | 82,45% | 0,7859 | 0,8190 | 0,8210 | 0,8245 |
| **Extra Trees** | 81,97% | 0,7786 | 0,8121 | 0,8150 | 0,8197 |
| **Gradient Boosting** | 84,13% | 0,8082 | 0,8385 | 0,8410 | 0,8413 |

### Conclusão da Seleção do Modelo:
O **Linear SVM Calibrado** obteve o melhor desempenho global com **91,83% de Acurácia** e **0,9018 de F1-Score Macro**, demonstrando excelente capacidade de discriminação entre os níveis escolares. O modelo foi serializado e é carregado automaticamente pela API Web.

---

## 5. Algoritmos de Mutação Textual

O módulo [`backend/mutator.py`](file:///home/vinicius/Documentos/RepositorioCAED/backend/mutator.py) implementa três famílias de operadores mutacionais:

1. **Troca de Palavras (Sinônimos e Antônimos)**:
   - Substituição estocástica controlada por parâmetro de intensidade ($\alpha \in [0.1, 0.8]$).
   - Mantém a caixa das letras e previne mutações em artigos/conectivos essenciais.
2. **Troca de Gênero Gramatical**:
   - Flexão simultânea de artigos (`o`/`a`), pronomes (`ele`/`ela`, `este`/`esta`, `meu`/`minha`), substantivos (`aluno`/`aluna`, `cantor`/`cantora`, `menino`/`menina`) e adjetivos de concordância.
   - Exemplo: *"A cantora era muito famosa"* &rarr; *"O cantor era muito famoso"*.
3. **Paráfrase e Reestruturação Sintática**:
   - **Voz Passiva para Ativa**: *"O texto foi lido pelo aluno"* &rarr; *"O aluno leu o texto"*.
   - **Reordenação de Apostos**: *"O cantor Roberto Carlos fez aniversário"* &rarr; *"Roberto Carlos, o cantor, fez aniversário"*.
   - **Deslocamento de Adjuntos Temporais**: *"Há duas semanas atrás estava chovendo"* &rarr; *"Estava chovendo há duas semanas atrás"*.

### Reavaliação em Tempo Real:
A cada mutação gerada, o sistema re-executa a análise de canonicidade e a classificação pelo modelo de IA, destacando no painel se houve **Shift de Complexidade** (mudança de classe predita).

---

## 6. Arquitetura da Aplicação Web

A aplicação Web foi desenvolvida seguindo os mais elevados padrões visuais e funcionais:
- **Backend**: FastAPI (Python) fornecendo endpoints RESTful (`/api/classify`, `/api/mutate`, `/api/analytics`, `/api/samples`).
- **Frontend**: Single-Page Application (SPA) responsiva em Vanilla HTML5/CSS3/JavaScript, sem dependências pesadas de frameworks, com tema escuro glassmorphism, gradientes suaves, animações de score circular, visualizador de diff em tempo real e gráficos interativos com Chart.js.

---

## 7. Instruções para Execução do Projeto

### Pré-requisitos
- Python 3.10 ou superior
- Node.js (opcional, ambiente isolado pronto)

### Passo 1: Instalação e Treinamento do Modelo
No terminal, dentro do diretório do repositório:

```bash
# 1. Ativar o ambiente virtual e instalar dependências
source .venv/bin/activate
pip install -r requirements.txt # ou scikit-learn nltk spacy fastapi uvicorn pandas numpy

# 2. Executar o pipeline de treinamento e benchmark dos modelos
python train_and_eval.py
```

### Passo 2: Iniciar a Aplicação Web
```bash
python run.py
```
Acesse a aplicação no navegador em: **`http://localhost:8000`**

---
*Relatório gerado como parte da entrega oficial do processo seletivo CAEd 024-2026.*
