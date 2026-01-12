# 📈 Assistant Financier Agentique (AI Financial Analyst)

Ce projet est une application d'analyse financière intelligente reposant sur une architecture **multi-agents** avancée. Il vise à reproduire le flux de travail d'un analyste humain en combinant l'analyse technique quantitative (chiffres, graphiques) avec une veille médiatique en temps réel (actualités, sentiment) pour fournir une aide à la décision complète et nuancée.

## 🚀 Fonctionnalités 

### 1. Analyse Individuelle Approfondie
-   **Analyse Quantitative Intelligence** : Un agent dédié interprète les données historiques pour identifier :
    -   **Tendances** : Via le croisement de moyennes mobiles (SMA 20 et SMA 50).
    -   **Momentum** : Analyse du RSI (Relative Strength Index 14 périodes) pour détecter les zones de surachat/survente.
    -   **Risque** : Évaluation de la volatilité sur 30 jours.
-   **Score Technique** : Un algorithme calcule un score global (de -2 à +2) résumant la configuration technique.
-   **Veille Médiatique** : Un second agent scanne le web pour contextualiser la performance boursière avec des événements réels (résultats d'entreprise, annonces macro-économiques).

### 2. Comparateur Multi-Actions
Une interface dédiée permet de confronter plusieurs actifs simultanément :
-   **Performance Normalisée** : Graphique comparatif en base 100 pour visualiser la performance relative réelle (% de gain/perte) indépendamment du prix de l'action.
-   **Analyse des Volumes** : Comparaison des volumes d'échange pour identifier l'intérêt des investisseurs.
-   **Export de Données** : Possibilité de télécharger les jeux de données comparés en CSV unique.

### 3. Dashboard Interactif
Interface utilisateur fluide réalisée avec **Streamlit**, offrant :
-   Graphiques interactifs (Prix, Volume).
-   Sélecteurs de dates dynamiques.
-   Affichage clair des métriques clés (Prix début/fin, Performance %, Volatilité).

## 🧠 Architecture & Agents (Le "Cerveau" du système)

Le système utilise le framework **Phidata** pour orchestrer une collaboration entre deux agents spécialisés, propulsés par le modèle **Llama 3.1** (via Groq) :

### 📊 Agent 1 : L'Analyste Quantitatif (Financial Analysis Agent)
*   **Mission** : Transformer des données brutes en narration financière intelligible.
*   **Fonctionnement (Technique RAG simplifié)** :
    1.  Le système Python (`pandas`) pré-calcule les indicateurs techniques complexes (RSI, SMA, Volatilité) pour contourner les limitations de calcul mathématique des LLMs.
    2.  Un résumé statistique structuré est injecté dans le prompt de l'agent.
    3.  L'agent génère une analyse textuelle basée **uniquement** sur ces faits, garantissant une interprétation déterministe et sans hallucinations.
*   **Sécurité** : Cet agent n'a **pas** d'accès internet pour éviter la pollution de l'analyse technique par des informations externes non vérifiées.

### 🌍 Agent 2 : Le Chercheur d'Actualités (Web News Agent)
*   **Mission** : Connecter l'analyse technique au monde réel.
*   **Outils** : Équipé de l'outil `DuckDuckGo Search`.
*   **Logique** :
    1.  Reçoit une instruction de recherche ciblée sur le ticker.
    2.  Effectue plusieurs requêtes pour trouver des articles récents.
    3.  Synthétise les résultats en filtrant le bruit marketing pour ne garder que les faits financiers (fusions, résultats, produits).

## 🛠️ Stack Technique

*   **LLM** : `Llama-3.1-8b-instant` via l'API **Groq** (Inférence < 1s).
*   **Framework Agentique** : [Phidata](https://docs.phidata.com/).
*   **Frontend** : Streamlit.
*   **Traitement de Données** :
    -   **Pandas** : Manipulation de séries temporelles, calculs de fenêtres glissantes (Rolling windows).
    -   **CSV** : Stockage local des données boursières (Dossier `data/stocks`).

## 📦 Installation Pas à Pas

### Pré-requis
-   Python 3.9 ou supérieur.
-   Une clé API Groq (gratuite en bêta).

### 1. Cloner le projet
```bash
git clone https://github.com/votre-user/nlp-project.git
cd nlp-project
```

### 2. Environnement Virtuel
Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances.
```bash
python -m venv venv
# Activation sous Windows :
venv\Scripts\activate
# Activation sous Mac/Linux :
source venv/bin/activate
```

### 3. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration des Clés API
Créez un fichier `.env` à la racine du projet :
```env
GROQ_API_KEY=gsk_...
# Optionnel : Clé Phidata si vous utilisez leurs outils de monitoring
PHI_API_KEY=phi_...
```

## ▶️ Utilisation

Lancez le dashboard avec Streamlit :

```bash
streamlit run app.py
```
L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`.

## 📂 Structure des Fichiers Clés

-   `app.py` : Point d'entrée de l'interface graphique. Gère la navigation entre "Analyse" et "Comparaison".
-   `financial_agent.py` : Cœur de l'intelligence. Définit les prompts, les rôles des agents et leur orchestration.
-   `analysis_stock_data.py` : "Moteur de calcul". Contient toute la logique mathématique (calcul du RSI, des moyennes mobiles) et la génération des dictionnaires de résumé.
-   `compare_stocks_app.py` : Logique de la page de comparaison multi-actions.
-   `data/stocks/` : Base de données locale (fichiers .csv contenant OHLCV).

## Auteurs
**Projet NLP & IA Générative** - *Conception d'un système multi-agents pour la finance.*
