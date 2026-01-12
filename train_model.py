import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Configuration
DATA_PATH = "data/stocks/AAPL.csv"
MODEL_DIR = "model"
MODEL_PATH = f"{MODEL_DIR}/finance_model.pkl"

def train():
    print(f"Chargement des données depuis {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        print(f"Erreur: Fichier {DATA_PATH} introuvable.")
        return

    df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
    df = df.sort_values("Date")
    
    # Nettoyage et préparation
    if 'Adj Close' in df.columns:
        df.rename(columns={'Adj Close': 'Adj_Close'}, inplace=True)
    
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj_Close']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"Colonnes manquantes: {missing}")
        # Si Adj_Close manque, on utilise Close
        if 'Adj_Close' in missing and 'Close' in df.columns:
             print("Utilisation de Close comme Adj_Close")
             df['Adj_Close'] = df['Close']
             required_cols = [c for c in required_cols if c != 'Adj_Close'] + ['Adj_Close']
        else:
            return

    # Création de la target : 1 si le prix monte le lendemain, 0 sinon
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df = df.dropna()

    X = df[required_cols]
    y = df['Target']

    print(f"Entraînement sur {len(df)} lignes pour AAPL...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Précision du modèle sur test set: {acc:.2f}")

    # Sauvegarde
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Modèle sauvegardé dans {MODEL_PATH}")

if __name__ == "__main__":
    train()
