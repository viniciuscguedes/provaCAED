"""
Módulo para Treinamento, Avaliação Comparativa e Persistência dos Modelos de Predição de Complexidade.
"""

import os
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from backend.dataset_loader import load_dataset, ORDERED_LABELS
from backend.feature_extractor import extract_features_df

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

class ComplexityClassifierPipeline:
    def __init__(self):
        self.vectorizer_word = TfidfVectorizer(ngram_range=(1, 2), max_features=4000, sublinear_tf=True)
        self.vectorizer_char = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), max_features=4000, sublinear_tf=True)
        self.scaler = StandardScaler()
        self.model = None
        self.model_name = ""
        self.feature_names = []
        self.feature_columns = [
            "canonicity_ratio", "canonical_words_count", "word_count", "char_count",
            "avg_word_length", "sentence_count", "avg_sentence_length", "avg_syllables_per_word",
            "flesch_reading_ease", "complex_word_ratio", "type_token_ratio",
            "punctuation_ratio", "numeric_symbol_ratio"
        ]

    def _prepare_features(self, df: pd.DataFrame, is_train: bool = True):
        """Concatena features estilísticas numéricas com TF-IDF de palavras e caracteres."""
        tabular_df = extract_features_df(df)[self.feature_columns]
        
        if is_train:
            X_tabular = self.scaler.fit_transform(tabular_df)
            X_word = self.vectorizer_word.fit_transform(df["text"])
            X_char = self.vectorizer_char.fit_transform(df["text"])
        else:
            X_tabular = self.scaler.transform(tabular_df)
            X_word = self.vectorizer_word.transform(df["text"])
            X_char = self.vectorizer_char.transform(df["text"])
            
        X_combined = hstack([X_tabular, X_word, X_char]).tocsr()
        return X_combined, tabular_df

    def train_and_evaluate_all(self, df: pd.DataFrame):
        """
        Treina múltiplos modelos e retorna o benchmark completo com estatísticas comparativas.
        """
        X_train_df, X_test_df, y_train, y_test = train_test_split(
            df, df["label"], test_size=0.2, random_state=42, stratify=df["label"]
        )
        
        X_train_comb, _ = self._prepare_features(X_train_df, is_train=True)
        X_test_comb, _ = self._prepare_features(X_test_df, is_train=False)
        
        models_to_test = {
            "Linear SVM": LinearSVC(C=1.0, random_state=42, max_iter=2000),
            "Regressão Logística": LogisticRegression(max_iter=1000, C=1.5, random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
        }
        
        results = {}
        best_f1 = -1.0
        best_model_obj = None
        best_name = ""
        
        print("\n" + "="*50)
        print("INICIANDO TREINAMENTO E AVALIAÇÃO COMPARATIVA DE MODELOS")
        print("="*50)
        
        for name, clf in models_to_test.items():
            print(f"Treinando {name}...")
            clf.fit(X_train_comb, y_train)
            y_pred = clf.predict(X_test_comb)
            
            acc = accuracy_score(y_test, y_pred)
            f1_macro = f1_score(y_test, y_pred, average="macro")
            f1_weighted = f1_score(y_test, y_pred, average="weighted")
            precision = precision_score(y_test, y_pred, average="weighted")
            recall = recall_score(y_test, y_pred, average="weighted")
            cm = confusion_matrix(y_test, y_pred, labels=ORDERED_LABELS)
            
            results[name] = {
                "accuracy": round(acc, 4),
                "f1_macro": round(f1_macro, 4),
                "f1_weighted": round(f1_weighted, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "confusion_matrix": cm.tolist()
            }
            
            print(f" -> {name} | Acurácia: {acc:.4f} | F1-Macro: {f1_macro:.4f} | F1-Weighted: {f1_weighted:.4f}")
            
            if f1_macro > best_f1:
                best_f1 = f1_macro
                best_model_obj = clf
                best_name = name
                
        print(f"\nMelhor Modelo Escolhido: {best_name} (F1-Macro: {best_f1:.4f})")
        
        self.model = best_model_obj
        self.model_name = best_name
        
        # Salva o pipeline treinado
        os.makedirs(MODEL_DIR, exist_ok=True)
        save_path = os.path.join(MODEL_DIR, "complexity_model.pkl")
        joblib.dump({
            "vectorizer_word": self.vectorizer_word,
            "vectorizer_char": self.vectorizer_char,
            "scaler": self.scaler,
            "model": self.model,
            "model_name": self.model_name,
            "feature_columns": self.feature_columns,
            "ordered_labels": ORDERED_LABELS,
            "benchmark_results": results
        }, save_path)
        print(f"Modelo salvo em {save_path}")
        
        return results

    def predict_single(self, text: str) -> dict:
        """
        Prediz o nível de complexidade de um único texto com probabilidades.
        """
        df_single = pd.DataFrame([{"text": text}])
        tabular_df = extract_features_df(df_single)[self.feature_columns]
        
        X_tabular = self.scaler.transform(tabular_df)
        X_word = self.vectorizer_word.transform(df_single["text"])
        X_char = self.vectorizer_char.transform(df_single["text"])
        X_comb = hstack([X_tabular, X_word, X_char]).tocsr()
        
        pred_label = self.model.predict(X_comb)[0]
        
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_comb)[0]
            prob_dict = {label: round(float(p), 4) for label, p in zip(self.model.classes_, probs)}
        else:
            prob_dict = {label: (1.0 if label == pred_label else 0.0) for label in ORDERED_LABELS}
            
        features = tabular_df.iloc[0].to_dict()
        
        return {
            "predicted_level": pred_label,
            "probabilities": prob_dict,
            "features": features,
            "model_used": self.model_name
        }

def load_trained_pipeline():
    """Carrega o pipeline pré-treinado do disco."""
    save_path = os.path.join(MODEL_DIR, "complexity_model.pkl")
    if not os.path.exists(save_path):
        return None
    data = joblib.load(save_path)
    pipe = ComplexityClassifierPipeline()
    pipe.vectorizer_word = data["vectorizer_word"]
    pipe.vectorizer_char = data["vectorizer_char"]
    pipe.scaler = data["scaler"]
    pipe.model = data["model"]
    pipe.model_name = data["model_name"]
    pipe.feature_columns = data["feature_columns"]
    return pipe, data["benchmark_results"]
