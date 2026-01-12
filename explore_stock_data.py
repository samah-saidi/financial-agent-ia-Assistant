import pandas as pd

# 1) Chemin vers ton fichier Kaggle
# adapte le chemin/nom de fichier si besoin
DATA_PATH = "data/stock_market.csv"

# 2) Charger le dataset
df = pd.read_csv(DATA_PATH)

# 3) Afficher les infos de base
print("Colonnes disponibles :")
print(df.columns)

print("\nPremières lignes :")
print(df.head())

print("\nInfos :")
print(df.info())
