import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.dataset_loader import load_dataset
from backend.model_trainer import ComplexityClassifierPipeline

def main():
    df = load_dataset("dataset_caed")

    
    pipeline = ComplexityClassifierPipeline()
    results = pipeline.train_and_evaluate_all(df)

if __name__ == "__main__":
    main()
