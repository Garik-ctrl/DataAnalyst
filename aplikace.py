import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date

st.title("Finanční data, dividendy a odhad Fair Value z Yahoo Finance")

# Vstupy umístěné do bočního panelu
with st.sidebar:
    ticker_symbol = st.text_input("Zadejte ticker (např. AAPL, MSFT):", "AAPL")
    start_date = st.date_input("Od", value=date(2020, 1, 1))
    end_date = st.date_input("Do", value=date.today())

if ticker_symbol:
    # Načtení dat pomocí yfinance
    ticker_data = yf.Ticker(ticker_symbol)
    info = ticker_data.info

    # Hlavička s informacemi o společnosti
    st.header("Informace o společnosti")
    st.write(f"**Název společnosti:** {info.get('shortName', 'N/A')}")
    st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
    st.write(f"**Průmysl:** {info.get('industry', 'N/A')}")

    # Načtení historických dat pro zvolené datumové rozpětí
    hist_data = ticker_data.history(start=start_date, end=end_date)

    # Výpočet klouzavých průměrů
    hist_data['MA50'] = hist_data['Close'].rolling(window=50).mean()
    hist_data['MA200'] = hist_data['Close'].rolling(window=200).mean()

    # Graf uzavíracích cen s MA50 a MA200
    st.subheader("Graf uzavíracích cen s MA50 a MA200")
    price_chart_data = hist_data[['Close', 'MA50', 'MA200']]
    st.line_chart(price_chart_data)

    # Zobrazení historických dat ve formě tabulky
    st.subheader("Historická data")
    st.write(hist_data)

    st.markdown("---")
    st.header("Dividendy a ex-dividend data")

    # Rozdělení na dva sloupce: levý pro textové hodnoty, pravý pro tabulku dividend
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Hodnoty")
        # Ex-dividend date – převedeno z UNIX timestamp
        ex_dividend_date = info.get('exDividendDate')
        if ex_dividend_date:
            ex_dividend_date_str = datetime.utcfromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
            st.write(f"**Ex-Dividend Date:** {ex_dividend_date_str}")
            st.write("*Poznámka: Jedná se o poslední zaznamenané ex-dividend datum.*")
        else:
            st.write("**Ex-Dividend Date:** Není dostupné")

        # Dividend yield
        dividend_yield = info.get('dividendYield')
        if dividend_yield is not None:
            st.write(f"**Dividend Yield:** {dividend_yield * 100:.2f}%")
        else:
            st.write("**Dividend Yield:** Není dostupná")

        # Payout ratio
        payout_ratio = info.get('payoutRatio')
        if payout_ratio is not None:
            st.write(f"**Payout Ratio:** {payout_ratio * 100:.2f}%")
        else:
            st.write("**Payout Ratio:** Není dostupná")

        # Hodnota poslední vyplacené dividendy – získána z historických dat
        dividends_series = ticker_data.dividends
        if not dividends_series.empty:
            last_dividend_value = dividends_series.iloc[-1]
            last_dividend_date = dividends_series.index[-1].strftime('%Y-%m-%d')
            st.write(f"**Poslední vyplacená dividenda:** {last_dividend_value:.2f} (dne {last_dividend_date})")
        else:
            st.write("**Poslední vyplacená dividenda:** Není dostupná")

    with right_col:
        st.subheader("Historie dividend")
        dividends = ticker_data.dividends
        if not dividends.empty:
            # Převod na DataFrame, převedení indexu na formát prostého data a reset indexu
            df_dividends = dividends.to_frame(name='Dividend')
            df_dividends.index = df_dividends.index.strftime('%Y-%m-%d')
            df_dividends = df_dividends.reset_index().rename(columns={'index': 'Date'})
            # Výpočet procentuální změny
            df_dividends['% Change'] = df_dividends['Dividend'].pct_change() * 100
            # Zaokrouhlení hodnot
            df_dividends['Dividend'] = df_dividends['Dividend'].round(2)
            df_dividends['% Change'] = df_dividends['% Change'].round(2)
            st.write(df_dividends)
        else:
            st.write("Dividendová data nejsou k dispozici.")
