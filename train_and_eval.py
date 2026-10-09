"""
Script de Treinamento, Avaliação e Validação de Modelos do Projeto CAEd.
Executa a leitura do dataset, extração de features, treinamento comparativo e exportação do modelo.
"""

import sys
import os

# Adiciona o diretório raiz ao PATH do Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.dataset_loader import load_dataset
from backend.model_trainer import ComplexityClassifierPipeline

def main():
    print("==================================================")
    print(" INICIANDO PIPELINE DE ML PARA CLASSIFICAÇÃO CAED ")
    print("==================================================")
    
    # 1. Carrega dataset
    df = load_dataset("dataset_caed")
    print(f"Total de amostras: {len(df)}")
    print(df["label"].value_counts())
    
    # 2. Inicializa e avalia pipeline
    pipeline = ComplexityClassifierPipeline()
    results = pipeline.train_and_evaluate_all(df)
    
    print("\n--- RESUMO FINAL DOS RESULTADOS DOS MODELOS ---")
    for model_name, metrics in results.items():
        print(f"\nModelo: {model_name}")
        print(f"  Acurácia:    {metrics['accuracy']*100:.2f}%")
        print(f"  F1-Macro:    {metrics['f1_macro']:.4f}")
        print(f"  F1-Weighted: {metrics['f1_weighted']:.4f}")
        print(f"  Precisão:    {metrics['precision']:.4f}")
        print(f"  Revocação:   {metrics['recall']:.4f}")
        
    print("\nPipeline executado com sucesso e modelo persistido em backend/models/complexity_model.pkl")

if __name__ == "__main__":
    main()
