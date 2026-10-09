import os
import pandas as pd
from pathlib import Path

LABEL_MAP = {
    "1_Ensino_Fundamental_I": "Ensino Fundamental I",
    "2_Ensino_Fundamental_II": "Ensino Fundamental II",
    "3_Ensino_Medio": "Ensino Médio",
    "4_Ensino_Superior": "Ensino Superior"
}

ORDERED_LABELS = [
    "Ensino Fundamental I",
    "Ensino Fundamental II",
    "Ensino Médio",
    "Ensino Superior"
]

def load_dataset(dataset_dir: str = "dataset_caed") -> pd.DataFrame:
    records = []
    base_path = Path(dataset_dir)
    
    if not base_path.exists():
        raise FileNotFoundError(f"Diretório do dataset não encontrado: {dataset_dir}")
        
    for category_folder in base_path.iterdir():
        if category_folder.is_dir() and category_folder.name in LABEL_MAP:
            label = LABEL_MAP[category_folder.name]
            folder_key = category_folder.name
            
            for file_path in category_folder.glob("*.txt"):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().strip()
                        
                    if content:
                        records.append({
                            "filename": file_path.name,
                            "category_dir": folder_key,
                            "label": label,
                            "text": content,
                            "char_count": len(content),
                            "word_count": len(content.split())
                        })
                except Exception as e:
                    print(f"Erro ao ler {file_path}: {e}")
                    
    df = pd.DataFrame(records)
    print(f"Dataset carregado com sucesso: {len(df)} documentos.")
    return df

if __name__ == "__main__":
    df = load_dataset()
    print(df["label"].value_counts())
