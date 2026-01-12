# 📈 Assistant Financier Agentique (AI Financial Analyst)

Ce projet est une application d'analyse financière intelligente reposant sur une architecture **multi-agents**. Il combine l'analyse quantitative de données boursières avec une veille médiatique en temps réel pour fournir une aide à la décision complète.

## 🚀 Fonctionnalités

- **Analyse Quantitative** : Un agent spécialisé analyse l'historique des prix (Moyennes mobiles, RSI, Volatilité) pour identifier les tendances et les niveaux clés.
- **Veille Médiatique** : Un agent "Chercheur" scanne le web via DuckDuckGo pour trouver les dernières actualités financières pertinentes.
- **Dashboard Interactif** : Interface utilisateur claire et moderne réalisée avec **Streamlit**.
- **Mode Comparaison** : Possibilité de comparer la performance relative de plusieurs actions.
- **Prédiction IA** : Modèle de Machine Learning intégré (FastAPI) pour prédire les mouvements futurs.

## 🖼️ Aperçus du Dashboard

![Interface Principale](images/Capture%20d'écran%202026-01-11%20112623.png)
*Vue d'ensemble de l'analyse individuelle avec indicateurs techniques et actualités.*

![Comparaison Multi-Actions](images/Capture%20d’écran%20(356).png)
*Performance relative et comparaison de plusieurs tickers.*

![Signaux Techniques](images/Capture%20d’écran%20(361).png)
*Détails des signaux (RSI, Moyennes Mobiles) et prédiction du modèle.*


## 🧠 Architecture & Agents

Le système utilise le framework **Phidata** pour orchestrer deux agents distincts, propulsés par le modèle **Llama 3** (via Groq) :

1.  **Agent Analyste Quantitatif (Financial Analysis Agent)** :
    *   **Rôle** : Interpréter les données chiffrées (CSV).
    *   **Spécificité** : Fonctionne en vase clos (sans accès internet) pour garantir une analyse purement technique et éviter les hallucinations. Il reçoit des résumés statistiques pré-calculés.

2.  **Agent Chercheur d'Actualités (Web News Agent)** :
    *   **Rôle** : Contextualiser l'analyse avec des faits réels.
    *   **Outils** : Utilise `DuckDuckGo` pour rechercher des articles récents.
    *   **Capacité** : Synthétise les informations et filtre le bruit médiatique.

## 🛠️ Stack Technique

*   **LLM** : Llama-3.1-8b-instant (via **Groq** pour l'inférence ultra-rapide).
*   **Orchestration** : [Phidata](https://docs.phidata.com/).
*   **Interface** : Streamlit.
*   **Données** : Pandas pour le traitement, yfinance/CSV locaux pour les sources.

## 📦 Installation

1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/votre-user/votre-repo.git
    cd votre-repo
    ```

2.  **Créer un environnement virtuel** :
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration** :
    Créez un fichier `.env` à la racine du projet et ajoutez votre clé API Groq :
    ```env
    GROQ_API_KEY=votre_cle_api_groq_ici
    PHI_API_KEY=votre_cle_api_phi_ici  # Optionnel
    ```

## ▶️ Utilisation

### 1. Lancer l'API (Backend)
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Lancer le Dashboard (Frontend)
```bash
streamlit run streamlit_app.py
```

L'interface sera accessible sur `http://localhost:8501`.


## 📂 Structure du Projet

*   `streamlit_app.py` : Entrée principale de l'interface utilisateur.
*   `app/` : Backend FastAPI (Modèles Pydantic, détection de drift).
*   `financial_agent.py` : Définition des agents (Phidata).
*   `train_model.py` : Script d'entraînement du modèle RandomForest.
*   `analysis_stock_data.py` : Logique de calcul technique.
*   `data/` : Sources de données (CSV).
*   `model/` : Modèle entraîné (`.pkl`).


## Auteurs

**Samah SAIDI**


Projet NLP & IA Générative.
