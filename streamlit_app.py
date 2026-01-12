import streamlit as st
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests
import json

from analysis_stock_data import get_stock_with_indicators
from financial_agent import (
    get_base_summary,
    financial_agent,
    web_news_agent,
)
from compare_stocks_app import show_comparison_page


@st.cache_data
def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Conversion DataFrame -> CSV (bytes) pour le download_button."""
    return df.to_csv(index=False).encode("utf-8")


# ---------------------------------------------------------------------
# Configuration & CSS
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="AI Financial Assistant",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)
# En‑tête principal
st.markdown(
    """
    <h1 style="display:flex;align-items:center;gap:0.6rem;
               font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
               font-size:2.1rem;font-weight:800;color:#111827;margin-bottom:0.3rem;">
        📈 Assistant financier IA : analyse boursière et actualités
    </h1>
    <p style="margin:0;color:#6b7280;font-size:0.9rem;">
        Analyse historique et actualités financières récentes via recherche web.
    </p>
    <p style="margin:0;color:#9ca3af;font-size:0.8rem;">
        Analyse basée sur le dataset Stock Market Dataset.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<style>
/* ... ton CSS existant ... */
main.stApp {
    background-color: #f8f9fa;
    color: #2c3e50;
}
            
            /* Conteneur principal */
section.main > div.block-container {
    padding-top: 1.5rem;
}

/* Pas de grosses cartes blanches pour tous les blocs */
section.main [data-testid="stVerticalBlock"] > div {
    background-color: transparent;
    box-shadow: none;
    padding: 0;
    margin-bottom: 1rem;
}
            
/* Texte lisible dans la zone principale */
section.main {
    color: #1f2666;
}
section.main p,
section.main li,
section.main span {
    color: #1f2133;
    font-size: 0.95rem;
}
            
            /* Titres */
h1, h2, h3 {
    color: #111827;
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
}
h1 { font-weight: 800; }
h2 {
    font-weight: 600;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

/* Sidebar sombre + texte clair */
[data-testid="stSidebar"] {
    background-color: #1f4666;
    color: #f9fafb;
}


/* Couleur des titres/labels généraux de la sidebar */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #f9fafb !important;
}

/* >>> Couleur spécifique pour les options du st.radio (mode d'affichage) <<< */
div[data-testid="stSidebar"] .stRadio label {
    color: #e5e7eb !important;        /* gris clair */
    font-weight: 600;
}

/* Option sélectionnée encore plus claire */
div[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:nth-child(2) {
    color: #ffffff !important;
}
            

</style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------------------
# Data Setup
# ---------------------------------------------------------------------

DATA_DIR = Path("data/stocks")
if DATA_DIR.exists():
    TICKERS = sorted([p.stem for p in DATA_DIR.glob("*.csv")])
else:
    st.error("Dossier de données introuvable.")
    TICKERS = []


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def parse_date_or_none(s: str):
    s = s.strip()
    if not s:
        return None
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        st.sidebar.error(f"Date invalide : {s}")
        return None


def get_api_prediction(features: dict):
    """Appelle l'API locale pour prédire le mouvement."""
    url = "http://localhost:8000/predict"
    try:
        response = requests.post(url, json=features, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": "Connection error", "details": str(e)}



# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------

with st.sidebar:
    st.title("💸 AI Finance")
    st.markdown("---")
    st.header("Paramètres")

    view = st.radio(
        "Mode d’affichage",
        ["Analyse individuelle", "Comparaison multi‑actions"],
    )

    # Variables par défaut
    ticker = None
    start_input = ""
    end_input = ""
    lancer = False
    compare_mode = False

    if view == "Analyse individuelle":
        ticker = st.selectbox("Action à analyser", TICKERS, index=0 if TICKERS else None)

        st.markdown("### Période d'analyse")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_input = st.text_input("Début", "", placeholder="YYYY-MM-DD")
        with col_d2:
            end_input = st.text_input("Fin", "", placeholder="YYYY-MM-DD")

        st.markdown("---")
        lancer = st.button("🚀 Lancer l'analyse", use_container_width=True, type="primary")
        compare_mode = st.checkbox("Mode Comparaison pour ce ticker")


# ---------------------------------------------------------------------
# Routing par mode
# ---------------------------------------------------------------------

if view == "Comparaison multi‑actions":
    # Page de comparaison globale (sélection des tickers dans compare_stocks_app)
    show_comparison_page()
    st.stop()


# ---------------------------------------------------------------------
# Main Application : Analyse individuelle
# ---------------------------------------------------------------------

if not ticker:
    st.info("Veuillez sélectionner un ticker dans la barre latérale.")
    st.stop()

st.title(f"Analyse Financière : {ticker}")

if lancer:
    start_date = parse_date_or_none(start_input)
    end_date = parse_date_or_none(end_input)

    with st.spinner(f"Analyse de {ticker} en cours..."):
        df_with_ind, base_text, summary_dict = get_base_summary(
            ticker, start_date, end_date
        )
        tech_text = summary_dict.get("technical_text")

        if tech_text:
            st.markdown("### ⚙️ Synthèse des signaux techniques")
            st.info(tech_text)


        if not summary_dict and df_with_ind.empty:
            st.error(f"Aucune donnée trouvée pour {ticker} sur la période demandée.")
            st.stop()

        price_prompt = (
            f"Voici un résumé pour {ticker}:\n{base_text}\n"
            "Rédige une analyse financière structurée (Tendance, Risques, Opportunités)."
        )
        try:
            price_run = financial_agent.run(price_prompt)
            quant_analysis = price_run.content
        except Exception as e:
            quant_analysis = f"Erreur lors de l'analyse IA : {str(e)}"

        news_prompt = (
            f"Trouve les dernières actualités financières importantes pour {ticker}. "
            "Résume en 3 points clés avec titres."
        )
        try:
            news_run = web_news_agent.run(news_prompt)
            news_content = news_run.content
        except Exception:
            news_content = "Indisponible (limite API ou réseau)."

    # Indicateurs clés
    st.markdown("### 📊 Indicateurs Clés")
    m1, m2, m3, m4 = st.columns(4)

    start_p = summary_dict.get("start_price", 0)
    end_p = summary_dict.get("end_price", 0)
    perf = ((end_p - start_p) / start_p * 100) if start_p else 0

    with m1:
        st.metric("Prix Début", f"${start_p:.2f}")
    with m2:
        st.metric("Prix Fin", f"${end_p:.2f}", f"{perf:.2f}%")
    with m3:
        st.metric("Volatilité", f"{summary_dict.get('volatility_30d_mean', 0):.4f}")
    with m4:
        st.metric("Volume Moyen", "N/A")

    st.markdown("---")

    tech_score = summary_dict.get("technical_score")

    if tech_score is not None:
        label = "neutre"
        if tech_score >= 2:
            label = "plutôt haussier"
        elif tech_score <= -2:
            label = "plutôt baissier"

        st.markdown(
            f"**Score technique global** : {tech_score} ({label}). "
            "Basé sur les croisements de moyennes mobiles et le RSI."
        )



    # --- SECTION PREDICTION API ---
    st.markdown("### 🔮 Prédiction IA (Modèle Local)")

    # Préparation des données pour l'API (dernière ligne connue du dataset, pas forcément aujourd'hui)
    if not df_with_ind.empty:
        last_row = df_with_ind.iloc[-1]
        
        # Fallback pour Adj Close si absent
        adj_close_val = last_row["Close"]
        if "Adj Close" in df_with_ind.columns:
            adj_close_val = last_row["Adj Close"]
        elif "Adj_Close" in df_with_ind.columns:
            adj_close_val = last_row["Adj_Close"]

        # Helper pour nettoyer les NaNs (JSON standard n'aime pas NaN)
        def clean_float(val):
            return float(val) if pd.notna(val) else 0.0

        # Construction du payload
        api_payload = {
            "Open": clean_float(last_row["Open"]),
            "High": clean_float(last_row["High"]),
            "Low": clean_float(last_row["Low"]),
            "Close": clean_float(last_row["Close"]),
            "Volume": int(last_row["Volume"]) if pd.notna(last_row["Volume"]) else 0,
            "Adj_Close": clean_float(adj_close_val)
        }

        with st.spinner("Interrogation du modèle de prédiction..."):
            pred_res = get_api_prediction(api_payload)
        
        if "error" in pred_res:
            st.warning(f"API non disponible : {pred_res['error']} - {pred_res.get('details', '')}")

        else:
            # Affichage du résultat
            col_p1, col_p2 = st.columns(2)
            prob = pred_res.get("prediction_probability", 0.0)
            risk = pred_res.get("risk_level", "Unknown")
            
            with col_p1:
                st.metric("Probabilité de Hausse (Demain)", f"{prob:.1%}")
            with col_p2:
                st.metric("Niveau de Risque", risk)
            
            drift = pred_res.get("drift_warning", False)
            if drift:
                st.warning("⚠️ Attention : Dérive de données détectée (Drift) !")
    else:
        st.info("Pas assez de données pour faire une prédiction.")

    st.markdown("---")


    # Analyse + News

    col_analysis, col_news = st.columns([2, 1])

    with col_analysis:
        st.subheader("💡 Analyse Quantitative")
        st.info(quant_analysis)

        st.subheader("📈 Graphiques")
        tab1, tab2 = st.tabs(["Prix", "Volume"])
        with tab1:
            st.line_chart(df_with_ind.set_index("Date")[["Close"]])
        with tab2:
            st.bar_chart(df_with_ind.set_index("Date")[["Volume"]])

    tech_text = summary_dict.get("technical_text")
    if tech_text:
        st.markdown("### ⚙️ Synthèse des signaux techniques")
        st.info(tech_text)

    with col_news:
        st.subheader("📰 Actualités")
        st.markdown(news_content)

    # Comparaison locale autour du ticker sélectionné
    if compare_mode:
        st.markdown("---")
        st.header("⚔️ Comparateur Multi-Actions")

        multiselect_tickers = st.multiselect(
            "Ajouter des concurrents",
            [t for t in TICKERS if t != ticker],
        )

        if multiselect_tickers:
            tickers_to_compare = [ticker] + multiselect_tickers
            data_dict = {}

            for t in tickers_to_compare:
                d, _ = get_stock_with_indicators(t, start_date, end_date)
                if d.empty:
                    st.warning(f"⚠️ Données insuffisantes pour {t} (ignoré).")
                    continue
                d = d.rename(columns={"Date": "Date", "Close": "Close", "Volume": "Volume"})
                d["Ticker"] = t
                data_dict[t] = d.sort_values("Date")

            valid_tickers = list(data_dict.keys())

            if not valid_tickers:
                st.error("Aucune donnée valide pour la comparaison.")
            else:
                st.subheader("Performance Relative (%)")
                perf_dfs = []
                for t in valid_tickers:
                    df_t = data_dict[t].copy()
                    first_close = df_t["Close"].iloc[0]
                    if first_close > 0:
                        df_t["Performance"] = ((df_t["Close"] / first_close) - 1) * 100
                        perf_dfs.append(df_t[["Date", "Ticker", "Performance"]])

                if perf_dfs:
                    perf_all = pd.concat(perf_dfs)
                    perf_pivot = perf_all.pivot_table(
                        index="Date", columns="Ticker", values="Performance"
                    )
                    st.line_chart(perf_pivot)

                with st.expander("Voir les données brutes"):
                    cols = st.columns(len(valid_tickers))
                    for idx, t in enumerate(valid_tickers):
                        with cols[idx]:
                            st.caption(t)
                            st.dataframe(data_dict[t].head())
        # 3bis. Indicateurs techniques (si disponibles dans df_with_ind)
    st.markdown("---")
    st.markdown("### 📊 Indicateurs techniques")

    # On suppose que get_stock_with_indicators / df_with_ind contient déjà ces colonnes
    tech_cols = [c for c in ["MA_short", "MA_long", "Volatility_30d", "RSI_14"] if c in df_with_ind.columns]

    if not tech_cols:
        st.info("Aucun indicateur technique détaillé n'est disponible pour ce ticker sur cette période.")
    else:
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            st.markdown("#### Courbes de moyennes mobiles")
            ma_cols = [c for c in ["MA_short", "MA_long"] if c in tech_cols]
            if ma_cols:
                st.line_chart(
                    df_with_ind.set_index("Date")[["Close"] + ma_cols]
                    .dropna()
                )
            else:
                st.caption("Moyennes mobiles non disponibles.")

        with col_t2:
            st.markdown("#### Volatilité / RSI")
            vol_cols = [c for c in ["Volatility_30d"] if c in tech_cols]
            rsi_cols = [c for c in ["RSI_14"] if c in tech_cols]

            if vol_cols:
                st.line_chart(
                    df_with_ind.set_index("Date")[vol_cols].dropna()
                )
            if rsi_cols:
                st.line_chart(
                    df_with_ind.set_index("Date")[rsi_cols].dropna()
                )
            if not vol_cols and not rsi_cols:
                st.caption("Aucun indicateur de volatilité ou RSI disponible.")

    st.markdown("### 📥 Export des données")

    csv_bytes = _to_csv_bytes(df_with_ind)

    st.download_button(
        label="Télécharger les données (CSV)",
        data=csv_bytes,
        file_name=f"{ticker}_historique_indicateurs.csv",
        mime="text/csv",
        use_container_width=True,
    )
