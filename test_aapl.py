import pandas as pd

# 1) Chemin vers le fichier AAPL
path = "data/stocks/AAPL.csv"   # adapte si ton chemin est différent

# 2) Chargement du CSV
df = pd.read_csv(path)

# 3) Afficher les colonnes
print("Colonnes :")
print(df.columns)

# 4) Afficher les 5 premières lignes
print("\nPremières lignes :")
print(df.head())

# 5) Infos sur les types
print("\nInfos :")
print(df.info())
