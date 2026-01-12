from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo

from analysis_stock_data import (
    get_stock_with_indicators,
    generate_text_summary,
)

# ---------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------

load_dotenv()

groq_model = Groq(id="llama-3.1-8b-instant")
print("ID du modèle Groq utilisé :", groq_model.id)

duck_tool = DuckDuckGo(fixed_max_results=3)

# ---------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------

def get_base_summary(ticker: str, start_date=None, end_date=None):
    """
    Charge les données + indicateurs et renvoie :
    - df_with_ind : DataFrame avec prix, volume, indicateurs
    - base_text   : résumé texte
    - summary_dict: résumé numérique pour l'agent
    """
    df_with_ind, summary_dict = get_stock_with_indicators(
        ticker, start_date=start_date, end_date=end_date
    )
    
    if not summary_dict:
        return df_with_ind, "Pas de données disponibles pour cette période.", {}
        
    base_text = generate_text_summary(ticker, summary_dict)
    return df_with_ind, base_text, summary_dict

# ---------------------------------------------------------------------
# Agent d'analyse quantitative (prix)
# ---------------------------------------------------------------------

financial_agent = Agent(
    name="Financial Analysis Agent",
    role=(
        "Tu es un analyste financier. "
        "Tu reçois un résumé quantitatif de l'évolution d'une action "
        "et tu dois produire une analyse claire, structurée, en français, "
        "avec : contexte, interprétation des chiffres, niveaux de risque, "
        "et éventuellement des conseils prudents (pas de promesse de gains)."
    ),
    model=groq_model,
    instructions=[
        "Réponds en français.",
        "Utilise le résumé fourni comme base, ne l'invente pas.",
        "Explique simplement pour un débutant.",
        "Structure ta réponse avec des paragraphes courts et éventuellement des listes.",
    ],
    markdown=True,
)

# ---------------------------------------------------------------------
# Agent d'actualités web (DuckDuckGo)
# ---------------------------------------------------------------------

web_news_agent = Agent(
    name="Web News Agent",
    role=(
        "Tu es un analyste qui utilise un moteur de recherche (DuckDuckGo) "
        "pour trouver des actualités financières récentes sur une entreprise cotée."
    ),
    model=groq_model,
    tools=[duck_tool],
    instructions=[
        "Réponds en français.",
        "Quand tu as besoin d'informations web, formule une requête claire pour DuckDuckGo.",
        "Résume les 3 à 5 principales actualités financières ou boursières récentes.",
        "Inclue, quand c'est possible, les titres des articles et les liens.",
    ],
    markdown=True,
    show_tool_calls=False,
)

# ---------------------------------------------------------------------
# Fonctions principales (utiles pour console + Streamlit)
# ---------------------------------------------------------------------

def run_quantitative_analysis(ticker: str, start_date=None, end_date=None):
    """
    Exécute l'analyse quantitative pour un ticker donné.
    Retourne:
      - df_with_ind : DataFrame (pour les graphiques dans Streamlit)
      - quant_text  : texte de l'analyse généré par l'agent
    """
    df_with_ind, base_text, summary_dict = get_base_summary(
        ticker, start_date, end_date
    )

    price_prompt = (
        f"Voici un résumé quantitatif pour l'action {ticker} :\n\n"
        f"{base_text}\n\n"
        "À partir de ce résumé, rédige une analyse structurée :\n"
        "- explique la tendance générale du cours sur la période,\n"
        "- commente les niveaux minimum, maximum et le prix moyen,\n"
        "- interprète la volatilité moyenne,\n"
        "- donne quelques points de vigilance pour un investisseur prudent.\n"
    )

    response = financial_agent.run(price_prompt)
    return df_with_ind, response.content


def run_news_search(ticker: str):
    """
    Recherche les actualités pour un ticker donné.
    Retourne le texte de synthèse.
    """
    today = datetime.today().strftime("%Y-%m-%d")

    news_prompt = (
        f"Tu dois rechercher des actualités financières récentes sur l'entreprise "
        f"liée au ticker {ticker} en utilisant DuckDuckGo.\n\n"
        "Concentre-toi sur les actualités les plus récentes, idéalement de la "
        "semaine ou du mois en cours.\n"
        "Donne une synthèse en français avec 3 à 5 points, et cite les titres "
        "et liens des articles importants si possible.\n"
    )

    response = web_news_agent.run(news_prompt)
    return response.content

# ---------------------------------------------------------------------
# Programme principal (mode console)
# ---------------------------------------------------------------------

if __name__ == "__main__":
    # Choisir le ticker
    ticker = input("Ticker à analyser (ex: AAPL, MSFT, TSLA) : ").strip().upper() or "AAPL"

    # Choisir la période (optionnelle)
    start = input("Date début (YYYY-MM-DD, vide = tout) : ").strip() or None
    end = input("Date fin   (YYYY-MM-DD, vide = tout) : ").strip() or None

    # 1) Analyse Quantitative
    print(f"\n--- Lancement de l'analyse quantitative pour {ticker} ---")
    df_with_ind, quant_content = run_quantitative_analysis(ticker, start, end)
    print(f"\n=== ANALYSE QUANTITATIVE POUR {ticker} ===\n")
    print(quant_content)

    # 2) Actualités web
    print(f"\n--- Recherche d'actualités pour {ticker} ---")
    news_content = run_news_search(ticker)
    print(f"\n=== ACTUALITÉS FINANCIÈRES POUR {ticker} ===\n")
    print(news_content)

    # 3) Sauvegarder le rapport en Markdown
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    period_str = ""
    if start:
        period_str += f"_{start}"
    if end:
        period_str += f"_{end}"

    today_str = datetime.today().strftime("%Y-%m-%d")
    report_path = reports_dir / f"{ticker}_{today_str}{period_str}.md"

    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"# Rapport pour {ticker} ({today_str})\n\n")
        if start or end:
            f.write(f"_Période analysée : {start or 'début'} → {end or 'fin'}._\n\n")
        f.write("## Analyse quantitative\n\n")
        f.write(quant_content)
        f.write("\n\n## Actualités financières\n\n")
        f.write(news_content)

    print(f"\nRapport sauvegardé dans : {report_path}")
