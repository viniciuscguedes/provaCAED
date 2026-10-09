# Plataforma CAEd - Avaliação de Fluência Leitora e Gerador de Textos

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-green.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9.1-orange.svg)](https://scikit-learn.org/)
[![Licença](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen.svg)]()

> Solução computacional inteligente desenvolvida para o processo de seleção do **CAEd (Edital 024-2026)**. O sistema realiza a **predição do nível de complexidade leitora** (EF I, EF II, EM, ES), a **análise de canonicidade silábica (Padrão CV)**, a **mutação textual gerativa** e disponibiliza uma **interface Web interativa**.

---

## Recursos Principais

1. **Modelo de Predição de Complexidade Leitora**:
   - Classificação em 4 níveis de escolaridade com **91,83% de Acurácia** (Linear SVM Calibrado).
   - Vetorização TF-IDF dual (palavras e n-gramas de caracteres) concatenada a 13 atributos estilístico-gramaticais.

2. **Algoritmo de Canonicidade Silábica (Padrão CV)**:
   - Heurística para validação de palavras canônicas $C$-$V$ alternadas (*ca-be-ça*, *lu-ta*, *so-pa*) exigida na Seção 2 do edital.
   - Decomposição silábica e cálculo em tempo real da proporção de canonicidade.

3. **Motor de Mutação Textual**:
   - **Troca de Palavras**: Substituição por sinônimos/antônimos com intensidade configurável.
   - **Troca de Gênero Gramatical**: Flexão de artigos, pronomes, substantivos e adjetivos (*"A cantora era famosa"* $\leftrightarrow$ *"O cantor era famoso"*).
   - **Paráfrase Sintática**: Inversão de voz passiva para ativa, reordenação de apostos e adjuntos temporais.
   - Reavaliação automática do **Shift de Complexidade** no modelo após mutações.

4. **Aplicação Web Interativa**:
   - Interface com estética minimalista editorial, gráficos em tempo real (Chart.js), visualizador de *diffs* e amostradores do dataset.

---

## Como Executar a Aplicação

### 1. Clonar o Repositório e Instalar Dependências
```bash
git clone https://github.com/viniciuscguedes/provaCAED.git
cd provaCAED

python3 -m venv .venv
source .venv/bin/activate

pip install scikit-learn nltk spacy fastapi uvicorn pandas numpy markdown reportlab fpdf2
```

### 2. Iniciar o Servidor Web
```bash
python run.py
```
Acesse a aplicação no navegador em: **`http://localhost:8000`**

### 3. Re-treinar e Avaliar os Modelos (Opcional)
```bash
python train_and_eval.py
```

---

## Estrutura do Repositório

```text
provaCAED/
├── backend/
│   ├── canonicity.py        # Algoritmo de Canonicidade Silábica (Padrão CV)
│   ├── feature_extractor.py # Extração de 13 atributos + Flesch + TTR
│   ├── model_trainer.py     # Pipeline de ML, benchmark e salvamento
│   ├── mutator.py           # Operadores de Mutação (Sinônimos, Gênero, Paráfrases)
│   ├── app.py               # API RESTful FastAPI
│   └── models/              # Artefato do modelo treinado (.pkl)
├── frontend/
│   ├── index.html           # Interface Web SPA
│   ├── styles.css           # Design System editorial minimalista (Zinc)
│   └── app.js               # Lógica do cliente, gráficos e visualização de diffs
├── dataset_caed/            # Dataset original com 2.076 documentos (.txt)
├── train_and_eval.py        # Script para treinar e gerar benchmark
├── run.py                   # Lançador do servidor Uvicorn
└── .gitignore               # Exclusões de ambiente virtual e temporários
```