# Guia de Seleção de Códigos e Explicação Técnica (Processo Seletivo CAEd - Edital 024-2026)

Este documento apresenta a **seleção dos 5 arquivos essenciais de código fonte** para upload no formulário do Google Form (**ARQUIVO 1** - limite de até 5 arquivos), acompanhado da **explicação detalhada da lógica e arquitetura** de cada um deles.

---

## 📦 1. Seleção dos 5 Arquivos Essenciais para Envio (ARQUIVO 1)

O Formulário do Google permite o envio de **no máximo 5 arquivos de código fonte** (limite de 1 MB por item). Para cobrir 100% dos requisitos do edital, selecionamos os 5 módulos principais da pasta [`backend/`](file:///home/vinicius/Documentos/RepositorioCAED/backend):

| Arquivo Selecionado | Função Principal no Projeto | Requisito Atendido |
| :--- | :--- | :--- |
| **1. `backend/canonicity.py`** | Algoritmo de Canonicidade Silábica CV | **Requisito Obrigatório Seção 2** (Heurística de palavras C-V) |
| **2. `backend/feature_extractor.py`** | Extração de Atributos e Métricas Estilísticas | Feature Engineering, Flesch, TTR, métricas gramaticais |
| **3. `backend/model_trainer.py`** | Pipeline de ML, Benchmark e Persistência | Treinamento comparativo (SVM, Reg. Logística, Random Forest) |
| **4. `backend/mutator.py`** | Motor de Mutação Textual | 3 Operadores (Sinônimos/Antônimos, Gênero, Paráfrase) |
| **5. `backend/app.py`** | Servidor API RESTful (FastAPI) | Integração da Aplicação Web e endpoints do sistema |

> **Nota:** Para o **ARQUIVO 2** do formulário, envie o documento **`RELATORIO.md`** (ou converta-o para PDF/Word se desejar).

---

## 🛠️ 2. Explicação Detalhada dos 5 Códigos Essenciais

---

### Arquivo 1: `backend/canonicity.py`
**Objetivo:** Implementar o algoritmo de validação de canonicidade silábica para a língua portuguesa.

#### Conceitos e Lógica de Implementação:
- **Definição de Canonicidade:** Uma palavra canônica é formada exclusivamente por sílabas do tipo **CV (Consoante + Vogal)**, tais como *ca-be-ça*, *ca-ne-la*, *ja-ne-la*, *lu-ta*, *so-pa*.
- **Padrão Regular $C$-$V$ Alternado:** O código mapeia cada letra da palavra para `'C'` (consoante) ou `'V'` (vogal). Uma palavra com todas as sílabas CV possui comprimento par e o padrão exato `"CV" * (tamanho // 2)`.
- **Funções Chave:**
  - `get_word_cv_pattern(word)`: Mapeia caracteres para a string contendo `'C'`, `'V'` ou `'X'`.
  - `is_canonical_word(word)`: Testa se a palavra limpa corresponde exatamente ao padrão C-V alternado. Retorna `True` ou `False`.
  - `syllabify_portuguese(word)`: Separador silábico heurístico para visualização das sílabas no frontend.
  - `analyze_text_canonicity(text)`: Processa todo o texto, contabiliza palavras canônicas vs não-canônicas e calcula a taxa `canonicity_ratio`.

---

### Arquivo 2: `backend/feature_extractor.py`
**Objetivo:** Extrair atributos numéricos estilísticos, morfológicos e de legibilidade a partir de qualquer texto.

#### Conceitos e Lógica de Implementação:
- **Índice de Legibilidade Flesch-Szigriszt (Adaptado para PT-BR):**
  $$\text{Flesch} = 248.835 - (1.015 \times \text{Média de Palavras/Frase}) - (84.6 \times \text{Média de Sílabas/Palavra})$$
- **Conjunto de 13 Atributos Extraídos:**
  1. `canonicity_ratio`: Taxa de palavras canônicas CV.
  2. `canonical_words_count`: Quantidade absoluta de palavras CV.
  3. `word_count` / `char_count`: Contagem total de palavras e caracteres.
  4. `avg_word_length`: Média de letras por palavra.
  5. `sentence_count` / `avg_sentence_length`: Extensão e complexidade sintática das frases.
  6. `avg_syllables_per_word`: Densidade silábica dos vocábulos.
  7. `flesch_reading_ease`: Score de facilidade de leitura.
  8. `complex_word_ratio`: Proporção de palavras com mais de 7 caracteres.
  9. `type_token_ratio`: Diversidade lexical ($TTR = \text{Vocábulos Únicos} / \text{Total de Palavras}$).
  10. `punctuation_ratio` / `numeric_symbol_ratio`: Densidade de pontuações e símbolos matemáticos.

---

### Arquivo 3: `backend/model_trainer.py`
**Objetivo:** Construir o pipeline de Machine Learning, realizar a vetorização TF-IDF dual, treinar múltiplos modelos e persistir o melhor modelo.

#### Conceitos e Lógica de Implementação:
- **Vetorização Híbrida (`_prepare_features`)**:
  - `TfidfVectorizer` de N-gramas de palavras ($1 \le n \le 2$, max 4.000 atributos).
  - `TfidfVectorizer` de N-gramas de caracteres ($3 \le n \le 5$, max 4.000 atributos).
  - `StandardScaler` para normalizar as 13 features numéricas tabulares.
  - As matrizes são unidas em uma matriz esparsa via `scipy.sparse.hstack`.
- **Benchmarking Comparativo (`train_and_evaluate_all`)**:
  - Avalia **Linear SVM**, **Regressão Logística** e **Random Forest** usando validação estratificada 80/20.
  - Calcula Acurácia, F1-Macro, F1-Weighted, Precisão, Revocação e Matriz de Confusão.
- **Persistência**: O pipeline completo (vetorizadores, scaler e modelo) é salvo em `backend/models/complexity_model.pkl` via `joblib`.

---

### Arquivo 4: `backend/mutator.py`
**Objetivo:** Aplicar mutações heurísticas no texto sem a necessidade de redes neurais pesadas, permitindo avaliar a sensibilidade do modelo de IA.

#### Conceitos e Lógica de Implementação:
1. **Troca de Palavras (`mutate_synonyms_antonyms`)**:
   - Dicionário curado de sinônimos e antônimos para a língua portuguesa.
   - Substituição aleatória com intensidade configurável ($\alpha \in [0.1, 0.8]$), preservando a caixa alta/baixa inicial.
2. **Troca de Gênero Gramatical (`mutate_gender`)**:
   - Mapeamento bidirecional flexional para artigos (*o/a*, *um/uma*), pronomes (*ele/ela*, *este/esta*, *meu/minha*), substantivos (*aluno/aluna*, *cantor/cantora*) e adjetivos (*famoso/famosa*, *bonito/bonita*).
3. **Paráfrase Sintática (`mutate_paraphrase`)**:
   - **Regra 1 (Voz Passiva &rarr; Ativa):** *"O texto foi lido pelo aluno"* &rarr; *"O aluno leu o texto"*.
   - **Regra 2 (Expressões Temporais):** *"Há duas semanas atrás estava chovendo"* &rarr; *"Estava chovendo há duas semanas atrás"*.
   - **Regra 3 (Reordenação de Apostos):** *"O cantor Roberto Carlos fez aniversário"* &rarr; *"Roberto Carlos, o cantor, fez aniversário"*.

---

### Arquivo 5: `backend/app.py`
**Objetivo:** Servidor backend FastAPI que expõe a API RESTful e conecta os modelos de ML e mutação à interface Web.

#### Endpoints Principais:
- `POST /api/classify`: Recebe um texto, executa a extração de atributos, realiza a predição no modelo salvo (`Linear SVM`) e retorna probabilidades, score de canonicidade e lista de sílabas.
- `POST /api/mutate`: Recebe o texto e parâmetros de mutação, aplica os operadores escolhidos, calcula o diff e realiza a reavaliação "Antes vs Depois" da complexidade predita.
- `GET /api/analytics`: Retorna os dados de benchmark de todos os modelos (acurácia, F1-score e matriz de confusão) para alimentação do dashboard gráfico.
- `GET /api/samples`: Fornece trechos reais do dataset para testes rápidos na interface.

---

## 📝 3. Resumo para Preenchimento do Formulário

- **Para o ARQUIVO 1 (Código fonte):**
  Faça o upload individual dos 5 arquivos:
  1. `canonicity.py`
  2. `feature_extractor.py`
  3. `model_trainer.py`
  4. `mutator.py`
  5. `app.py`

- **Para o ARQUIVO 2 (Relatório):**
  Faça o upload do arquivo **`RELATORIO.md`** contendo a fundamentação teórica, gráficos, tabelas de acurácia (91,83%) e a metodologia completa.
