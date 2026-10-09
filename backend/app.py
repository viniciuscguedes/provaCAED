"""
Aplicação Web API FastAPI para o Sistema CAEd de Análise, Classificação e Mutação de Textos.
"""

import os
import sys
import random
import difflib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Garantir importações do pacote backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.canonicity import analyze_text_canonicity, syllabify_portuguese, is_canonical_word
from backend.feature_extractor import extract_text_features
from backend.model_trainer import load_trained_pipeline
from backend.mutator import apply_mutations
from backend.dataset_loader import load_dataset, ORDERED_LABELS

app = FastAPI(
    title="Plataforma CAEd de Análise e Mutação de Complexidade Leitora",
    description="API RESTful para Classificação de Complexidade Textual, Análise Silábica CV e Operadores de Mutação.",
    version="1.0.0"
)

# Configurar CORS para permitir qualquer origem no desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega pipeline e estatísticas ao iniciar
pipeline_wrapper = load_trained_pipeline()
if pipeline_wrapper:
    pipeline, benchmark_results = pipeline_wrapper
else:
    pipeline = None
    benchmark_results = {}

# Pydantic Schemas
class ClassifyRequest(BaseModel):
    text: str = Field(..., example="A cantora era muito famosa na cidade de Ouro Preto.")

class MutateRequest(BaseModel):
    text: str = Field(..., example="Há duas semanas atrás estava chovendo forte na cidade.")
    operations: list[str] = Field(default=["synonym", "gender", "paraphrase"])
    intensity: float = Field(default=0.3, ge=0.0, le=1.0)

# Endpoints
@app.get("/api/health")
def health():
    return {
        "status": "online",
        "model_loaded": pipeline is not None,
        "model_name": pipeline.model_name if pipeline else None
    }

@app.post("/api/classify")
def classify_text(req: ClassifyRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="O texto fornecido não pode estar vazio.")
        
    if not pipeline:
        raise HTTPException(status_code=500, detail="O modelo de machine learning não está carregado. Treine o modelo primeiro.")
        
    # Predição e probabilidades
    pred_result = pipeline.predict_single(req.text)
    
    # Análise detalhada de canonicidade
    canonicity_info = analyze_text_canonicity(req.text)
    
    # Adicionar divisão silábica para amostra de palavras
    canonical_samples = [
        {"word": w, "syllables": syllabify_portuguese(w)}
        for w in list(set(canonicity_info["canonical_words"]))[:10]
    ]
    non_canonical_samples = [
        {"word": w, "syllables": syllabify_portuguese(w)}
        for w in list(set(canonicity_info["non_canonical_words"]))[:10]
    ]
    
    return {
        "text": req.text,
        "predicted_level": pred_result["predicted_level"],
        "probabilities": pred_result["probabilities"],
        "model_used": pred_result["model_used"],
        "features": pred_result["features"],
        "canonicity": {
            "ratio": canonicity_info["canonicity_ratio"],
            "canonical_count": canonicity_info["canonical_words_count"],
            "non_canonical_count": canonicity_info["non_canonical_words_count"],
            "total_words": canonicity_info["total_words"],
            "canonical_samples": canonical_samples,
            "non_canonical_samples": non_canonical_samples
        }
    }

@app.post("/api/mutate")
def mutate_and_evaluate(req: MutateRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="O texto fornecido não pode estar vazio.")
        
    # Aplica mutações
    mutation_res = apply_mutations(req.text, req.operations, req.intensity)
    mutated_text = mutation_res["mutated_text"]
    
    # Predição original vs nova
    orig_eval = pipeline.predict_single(req.text) if pipeline else None
    mut_eval = pipeline.predict_single(mutated_text) if pipeline else None
    
    # Análise de canonicidade original vs nova
    orig_canon = analyze_text_canonicity(req.text)
    mut_canon = analyze_text_canonicity(mutated_text)
    
    # Diff em HTML/markup para visualização no frontend
    matcher = difflib.SequenceMatcher(None, req.text.split(), mutated_text.split())
    diff_tokens = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            diff_tokens.append({"type": "equal", "text": " ".join(req.text.split()[i1:i2])})
        elif tag == "replace":
            diff_tokens.append({
                "type": "replace",
                "old": " ".join(req.text.split()[i1:i2]),
                "new": " ".join(mutated_text.split()[j1:j2])
            })
        elif tag == "delete":
            diff_tokens.append({"type": "delete", "text": " ".join(req.text.split()[i1:i2])})
        elif tag == "insert":
            diff_tokens.append({"type": "insert", "text": " ".join(mutated_text.split()[j1:j2])})

    return {
        "original_text": req.text,
        "mutated_text": mutated_text,
        "operations_applied": mutation_res["operations_applied"],
        "diff_tokens": diff_tokens,
        "before": {
            "predicted_level": orig_eval["predicted_level"] if orig_eval else "N/A",
            "probabilities": orig_eval["probabilities"] if orig_eval else {},
            "canonicity_ratio": orig_canon["canonicity_ratio"],
            "features": orig_eval["features"] if orig_eval else {}
        },
        "after": {
            "predicted_level": mut_eval["predicted_level"] if mut_eval else "N/A",
            "probabilities": mut_eval["probabilities"] if mut_eval else {},
            "canonicity_ratio": mut_canon["canonicity_ratio"],
            "features": mut_eval["features"] if mut_eval else {}
        },
        "complexity_changed": orig_eval["predicted_level"] != mut_eval["predicted_level"] if orig_eval and mut_eval else False
    }

@app.get("/api/analytics")
def get_analytics():
    return {
        "benchmark_results": benchmark_results,
        "ordered_labels": ORDERED_LABELS,
        "active_model": pipeline.model_name if pipeline else None
    }

@app.get("/api/samples")
def get_dataset_samples():
    try:
        df = load_dataset("dataset_caed")
        samples = {}
        for label in ORDERED_LABELS:
            sub = df[df["label"] == label]
            if not sub.empty:
                row = sub.sample(1).iloc[0]
                samples[label] = {
                    "filename": row["filename"],
                    "text": row["text"][:600] + ("..." if len(row["text"]) > 600 else "")
                }
        return samples
    except Exception as e:
        return {"error": str(e)}

# Servir arquivos estáticos do frontend se o diretório existir
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def read_root():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
