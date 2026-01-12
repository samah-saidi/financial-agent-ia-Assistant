import streamlit as st
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/stocks")


# ---------------------------------------------------------------------
# Chargement des données
# ---------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_data(ticker: str) -> pd.DataFrame:
    csv_path = DATA_DIR / f"{ticker}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Fichier introuvable pour le ticker {ticker}: {csv_path}")
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------
# Indicateurs
# ---------------------------------------------------------------------

def add_basic_indicators(stock_df: pd.DataFrame,
                         window_short: int = 7,
                         window_long: int = 30) -> pd.DataFrame:
    """Rendement simple, moyennes mobiles, volatilité 30 jours."""
    df = stock_df.copy()
    df["Return"] = df["Close"].pct_change()
    df["MA_short"] = df["Close"].rolling(window_short).mean()
    df["MA_long"] = df["Close"].rolling(window_long).mean()
    df["Volatility_30d"] = df["Return"].rolling(30).std()
    return df


def add_moving_averages(df: pd.DataFrame,
                        short_window: int = 20,
                        long_window: int = 50) -> pd.DataFrame:
    """Moyennes mobiles supplémentaires sur Close."""
    df = df.copy()
    df["MA_short_20"] = df["Close"].rolling(window=short_window,
                                            min_periods=short_window).mean()
    df["MA_long_50"] = df["Close"].rolling(window=long_window,
                                           min_periods=long_window).mean()
    return df


def add_rsi(df: pd.DataFrame, periods: int = 14) -> pd.DataFrame:
    """Ajoute un RSI(14) sur la colonne Close."""
    df = df.copy()
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=periods, min_periods=periods).mean()
    avg_loss = loss.rolling(window=periods, min_periods=periods).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    df["RSI_14"] = rsi
    return df


def add_volatility(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """Volatilité glissante basée sur les rendements journaliers."""
    df = df.copy()
    returns = df["Close"].pct_change()
    df["Volatility_30d"] = returns.rolling(window=window,
                                           min_periods=window).std()
    return df


# ---------------------------------------------------------------------
# Résumé numérique + texte
# ---------------------------------------------------------------------

def summarize_stock(stock_df: pd.DataFrame) -> dict:
    """Résumé : dates, prix début/fin, min, max, moyenne, volatilité moyenne."""
    if stock_df.empty:
        return {}

    summary = {
        "first_date": stock_df["Date"].min(),
        "last_date": stock_df["Date"].max(),
        "start_price": stock_df["Close"].iloc[0],
        "end_price": stock_df["Close"].iloc[-1],
        "min_price": stock_df["Close"].min(),
        "max_price": stock_df["Close"].max(),
        "mean_price": stock_df["Close"].mean(),
        "volatility_30d_mean": stock_df["Volatility_30d"].mean()
        if "Volatility_30d" in stock_df.columns else None,
    }
    return summary


def generate_text_summary(ticker: str, summary: dict) -> str:
    if not summary:
        return f"Aucune donnée disponible pour l'action {ticker} sur la période sélectionnée."

    text = (
        f"Pour l'action {ticker}, entre le {summary['first_date'].date()} "
        f"et le {summary['last_date'].date()}, le cours de clôture est passé "
        f"de {summary['start_price']:.2f} à {summary['end_price']:.2f}. "
        f"Le prix minimum observé est {summary['min_price']:.2f} et le maximum "
        f"{summary['max_price']:.2f}, pour un prix moyen de "
        f"{summary['mean_price']:.2f}. "
    )
    if summary.get("volatility_30d_mean") is not None:
        text += (
            f"La volatilité moyenne sur 30 jours est "
            f"{summary['volatility_30d_mean']:.4f}."
        )
    return text


# ---------------------------------------------------------------------
# Fonction principale appelée par app.py
# ---------------------------------------------------------------------

def get_stock_with_indicators(ticker: str, start_date=None, end_date=None):
    """
    Charge les données, filtre par dates, ajoute indicateurs et résumés.
    Retourne (df_with_indicators, summary_dict).
    """
    df = load_data(ticker)

    if start_date:
        df = df[df["Date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["Date"] <= pd.to_datetime(end_date)]

    if df.empty:
        return df, {}

    # Indicateurs de base (Return, MA_short, MA_long, Volatility_30d)
    df = add_basic_indicators(df)

    # Indicateurs techniques avancés
    df = add_moving_averages(df, short_window=20, long_window=50)
    df = add_rsi(df, periods=14)
    df = add_volatility(df, window=30)  # écrase Volatility_30d si déjà là

    summary = summarize_stock(df)
    tech_text = interpret_technical_signals(df)
    summary["technical_text"] = tech_text
    summary["technical_score"] = technical_score(df)
    return df, summary

def interpret_technical_signals(df: pd.DataFrame) -> str:
    """
    Produit une interprétation simple à partir des MA et du RSI.
    """
    if df.empty:
        return "Aucun signal technique disponible (pas de données)."

    last = df.iloc[-1]

    # RSI : zones standard 30 / 70 [web:103][web:111]
    rsi = last.get("RSI_14", None)
    if rsi is not None and pd.notna(rsi):
        if rsi > 70:
            rsi_comment = (
                f"Le RSI(14) est à {rsi:.1f}, en zone de surachat (>70), "
                "ce qui suggère un risque de correction à court terme."
            )
        elif rsi < 30:
            rsi_comment = (
                f"Le RSI(14) est à {rsi:.1f}, en zone de survente (<30), "
                "ce qui peut indiquer un potentiel de rebond."
            )
        else:
            rsi_comment = (
                f"Le RSI(14) est à {rsi:.1f}, indiquant un momentum neutre "
                "sans excès majeur d'achat ou de vente."
            )
    else:
        rsi_comment = "Le RSI(14) n'a pas pu être calculé sur la période choisie."

    # Croisement de moyennes mobiles (MA_short_20 vs MA_long_50) [web:108][web:110]
    ma_short = last.get("MA_short_20", None)
    ma_long = last.get("MA_long_50", None)

    if ma_short is not None and ma_long is not None and pd.notna(ma_short) and pd.notna(ma_long):
        if ma_short > ma_long:
            ma_comment = (
                "La moyenne mobile courte (20 jours) est au‑dessus de la "
                "moyenne mobile longue (50 jours), signal compatible avec "
                "une tendance haussière (crossover haussier)."
            )
        elif ma_short < ma_long:
            ma_comment = (
                "La moyenne mobile courte (20 jours) est sous la "
                "moyenne mobile longue (50 jours), ce qui correspond à "
                "un signal de tendance plutôt baissière."
            )
        else:
            ma_comment = (
                "Les moyennes mobiles 20 et 50 jours sont très proches, "
                "ce qui traduit une absence de tendance claire."
            )
    else:
        ma_comment = (
            "Les moyennes mobiles 20/50 jours ne sont pas disponibles sur l'échantillon."
        )

    return rsi_comment + " " + ma_comment

def technical_score(df: pd.DataFrame) -> int:
    """
    Renvoie un score technique simple basé sur RSI et MA (entre -2 et +2).
    +1 si MA courte > MA longue, -1 si l'inverse.
    +1 si RSI < 30 (potentiel rebond), -1 si RSI > 70 (risque correction).
    """
    if df.empty:
        return 0

    last = df.iloc[-1]
    score = 0

    # MA
    ma_short = last.get("MA_short_20")
    ma_long = last.get("MA_long_50")
    if ma_short is not None and ma_long is not None and pd.notna(ma_short) and pd.notna(ma_long):
        if ma_short > ma_long:
            score += 1
        elif ma_short < ma_long:
            score -= 1

    # RSI [web:103][web:111]
    rsi = last.get("RSI_14")
    if rsi is not None and pd.notna(rsi):
        if rsi < 30:
            score += 1
        elif rsi > 70:
            score -= 1

    return score


# ---------------------------------------------------------------------
# Test manuel en ligne de commande
# ---------------------------------------------------------------------

if __name__ == "__main__":
    ticker = input("Ticker pour le test (ex: AAPL, MSFT) : ").strip().upper() or "AAPL"

    df_with_ind, summary = get_stock_with_indicators(ticker)

    print(df_with_ind.tail())

    print(f"\nRésumé numérique {ticker} :")
    for k, v in summary.items():
        print(f"{k}: {v}")

    print("\nRésumé texte :")
    print(generate_text_summary(ticker, summary))
