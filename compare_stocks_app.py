import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd

from analysis_stock_data import get_stock_with_indicators



DATA_DIR = Path("data/stocks")
ALL_TICKERS = sorted([p.stem for p in DATA_DIR.glob("*.csv")])


def parse_date_or_none(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return None


def show_comparison_page():
    st.title("📊 Side‑by‑Side Stock Comparison")

    # Sélection des tickers et dates dans la sidebar
    with st.sidebar:
        st.header("Stock Selection")
        st.caption(f"Total available stocks: {len(ALL_TICKERS)}")

        default_list = (
            ["AAPL", "GOOG", "TSLA"]
            if {"AAPL", "GOOG", "TSLA"} <= set(ALL_TICKERS)
            else ALL_TICKERS[:3]
        )

        selected = st.multiselect(
            "Select stocks to analyze",
            options=ALL_TICKERS,
            default=default_list,
        )
        start_input = st.text_input("Start date (YYYY-MM-DD)", "2010-01-01")
        end_input = st.text_input("End date (YYYY-MM-DD)", "2023-01-01")

    start_date = parse_date_or_none(start_input)
    end_date = parse_date_or_none(end_input)

    if not selected:
        st.warning("Choisis au moins un ticker.")
        return
    if not start_date or not end_date:
        st.error("Dates invalides. Utilise le format YYYY-MM-DD.")
        return

    data_dict = {}
    for t in selected:
        df, _ = get_stock_with_indicators(t, start_date=start_input, end_date=end_input)
        if df.empty:
            st.warning(f"⚠️ Données insuffisantes pour {t} (ignoré).")
            continue
        df = df.rename(columns={"Date": "Date", "Close": "Close", "Volume": "Volume"})
        df = df.sort_values("Date")
        df["Ticker"] = t
        data_dict[t] = df

    if not data_dict:
        st.error("Aucune donnée disponible pour les tickers sélectionnés.")
        return

    st.subheader("Side‑by‑Side Comparison")
    cols = st.columns(len(data_dict))
    for col, (t, df) in zip(cols, data_dict.items()):
        with col:
            st.markdown(f"### {t}")
            st.json(df.head(3).to_dict(orient="records"))

    st.subheader("Stock Trading Volume Comparison")
    volumes = pd.concat(
        [df[["Date", "Volume"]].assign(Ticker=t) for t, df in data_dict.items()],
        ignore_index=True,
    )
    vol_pivot = volumes.pivot(index="Date", columns="Ticker", values="Volume")
    st.bar_chart(vol_pivot)

    st.subheader("Normalized Price Performance (%)")
    perf_list = []
    for t, df in data_dict.items():
        df_loc = df[["Date", "Close"]].copy()
        if df_loc["Close"].iloc[0] == 0:
            continue
        df_loc["Close_norm"] = df_loc["Close"] / df_loc["Close"].iloc[0] - 1
        df_loc["Ticker"] = t
        perf_list.append(df_loc[["Date", "Ticker", "Close_norm"]])

    if not perf_list:
        st.warning("Impossible de calculer la performance normalisée.")
        return

    perf = pd.concat(perf_list, ignore_index=True)
    perf_pivot = perf.pivot(index="Date", columns="Ticker", values="Close_norm") * 100
    st.line_chart(perf_pivot)
    st.markdown("### 📥 Export des données comparées")

    all_concat = pd.concat(data_dict.values(), ignore_index=True)
    csv_bytes = all_concat.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Télécharger les données multi‑actions (CSV)",
        data=csv_bytes,
        file_name="comparaison_stocks.csv",
        mime="text/csv",
        use_container_width=True,
    )









# import streamlit as st
# from pathlib import Path
# from datetime import datetime

# from analysis_stock_data import get_stock_with_indicators

# DATA_DIR = Path("data/stocks")
# ALL_TICKERS = sorted([p.stem for p in DATA_DIR.glob("*.csv")])

# st.set_page_config(page_title="Stock Comparison", layout="wide")

# st.title("📊 Side‑by‑Side Stock Comparison")

# with st.sidebar:
#     st.header("Stock Selection")
#     st.caption(f"Total available stocks: {len(ALL_TICKERS)}")

#     selected = st.multiselect(
#         "Select stocks to analyze",
#         options=ALL_TICKERS,
#         default=["AAPL", "GOOG", "TSLA"] if {"AAPL","GOOG","TSLA"} <= set(ALL_TICKERS) else ALL_TICKERS[:3],
#     )
#     start_input = st.text_input("Start date (YYYY-MM-DD)", "2010-01-01")
#     end_input = st.text_input("End date (YYYY-MM-DD)", "2023-01-01")


# import pandas as pd

# def parse_date_or_none(s):
#     try:
#         return datetime.strptime(s, "%Y-%m-%d")
#     except ValueError:
#         return None

# start_date = parse_date_or_none(start_input)
# end_date = parse_date_or_none(end_input)

# if not selected:
#     st.warning("Choisis au moins un ticker.")
#     st.stop()
# if not start_date or not end_date:
#     st.error("Dates invalides. Utilise le format YYYY-MM-DD.")
#     st.stop()

# data_dict = {}
# for t in selected:
#     df, _ = get_stock_with_indicators(t, start_date=start_input, end_date=end_input)
#     # harmoniser
#     df = df.rename(columns={"Date": "Date", "Close": "Close", "Volume": "Volume"})
#     df = df.sort_values("Date")
#     df["Ticker"] = t
#     data_dict[t] = df


# st.subheader("Side‑by‑Side Comparison")

# cols = st.columns(len(selected))
# for col, t in zip(cols, selected):
#     with col:
#         st.markdown(f"### {t}")
#         st.json(data_dict[t].head(3).to_dict(orient="records"))


# st.subheader("Stock Trading Volume Comparison")

# volumes = pd.concat(
#     [df[["Date", "Volume"]].assign(Ticker=t) for t, df in data_dict.items()],
#     ignore_index=True,
# )

# vol_pivot = volumes.pivot(index="Date", columns="Ticker", values="Volume")

# st.bar_chart(vol_pivot)



# st.subheader("Normalized Price Performance (%)")

# perf_list = []
# for t, df in data_dict.items():
#     df = df[["Date", "Close"]].copy()
#     df["Close_norm"] = df["Close"] / df["Close"].iloc[0] - 1
#     df["Ticker"] = t
#     perf_list.append(df[["Date", "Ticker", "Close_norm"]])

# perf = pd.concat(perf_list, ignore_index=True)
# perf_pivot = perf.pivot(index="Date", columns="Ticker", values="Close_norm") * 100

# st.line_chart(perf_pivot)
