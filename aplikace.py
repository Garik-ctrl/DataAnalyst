import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# ---------------------------------------------
# 📅 Sidebar vstupy
# ---------------------------------------------
st.set_page_config(page_title="Finanční dashboard", layout="wide")

# Načtení seznamu S&P 500 firem
@st.cache_data
def load_sp500():
    url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
    return pd.read_csv(url)

sp500_df = load_sp500()
tickers = sp500_df['Symbol'].tolist()

# Funkce pro stažení dat (P/E, ROE, sektor)
@st.cache_data
def fetch_extended_data(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            roe = info.get('returnOnEquity')
            data.append({
                'Ticker': ticker,
                'Name': info.get('shortName'),
                'Sector': info.get('sector'),
                'P/E': info.get('trailingPE'),
                'ROE': roe * 100 if roe is not None else None
            })
        except:
            continue
    return pd.DataFrame(data)

financial_df = fetch_extended_data(tickers)
financial_df.dropna(subset=['Sector', 'P/E', 'ROE'], inplace=True)



# ---------------------------------------------
# Karty
# ---------------------------------------------
tab1, tab4 = st.tabs([
    "📊 Tabulka firem",
    "🏦 Detail firmy"
])

with tab1:
    # Sektor na výběr
    sectors = financial_df['Sector'].dropna().unique()
    selected_sector = st.selectbox("Vyber sektor:", sorted(sectors))

    # Filtrování podle sektoru
    sector_df = financial_df[financial_df['Sector'] == selected_sector].copy()
    sector_df.sort_values('P/E', inplace=True)
    sector_df['Quartile'] = pd.qcut(sector_df['P/E'], 4, labels=["Q1", "Q2", "Q3", "Q4"])

    st.subheader(f"Firmy v sektoru: {selected_sector}")
    st.dataframe(sector_df)

    st.subheader(f"Interaktivní boxplot P/E")
    fig = px.box(
        sector_df,
        x='P/E',
        points='all',
        hover_name='Name',
        hover_data={'Ticker': True, 'P/E': ':.2f'},
        title=f'Distribuce P/E - {selected_sector}'
    )
    fig.update_traces(marker=dict(size=6, opacity=0.5))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Interaktivní scatter plot P/E vs ROE")
    fig = px.scatter(
        sector_df,
        x='P/E',
        y='ROE',
        hover_name='Name',
        hover_data={'Ticker': True, 'P/E': ':.2f', 'ROE': ':.2f'},
        text='Ticker',
        title=f"P/E vs ROE - {selected_sector}"
    )
    fig.update_traces(marker=dict(size=12, opacity=0.7), textposition='top center')
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)




# Tab 4 - Detail tickeru
with tab4:
    st.title("Finanční data a dividendy")
    ticker_symbol = st.text_input("Zadejte ticker (např. AAPL, MSFT):", "AAPL")
    start_date = st.date_input("Od", value=date(2020, 1, 1))
    end_date = st.date_input("Do", value=date.today())

    if ticker_symbol:
        ticker_data = yf.Ticker(ticker_symbol)
        info = ticker_data.info

        st.header("Informace o společnosti")
        st.write(f"**Název společnosti:** {info.get('shortName', 'N/A')}")
        st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
        st.write(f"**Průmysl:** {info.get('industry', 'N/A')}")

        hist_data = ticker_data.history(start=start_date, end=end_date)
        hist_data['MA50'] = hist_data['Close'].rolling(window=50).mean()
        hist_data['MA200'] = hist_data['Close'].rolling(window=200).mean()

        st.subheader("Graf uzavíracích cen s MA50 a MA200")
        st.line_chart(hist_data[['Close', 'MA50', 'MA200']])

        st.subheader("Historická data")
        st.write(hist_data)

        st.markdown("---")
        st.header("Dividendy a ex-dividend data")

        left_col, right_col = st.columns(2)

        with left_col:
            st.subheader("Hodnoty")
            ex_dividend_date = info.get('exDividendDate')
            if ex_dividend_date:
                ex_dividend_date_str = datetime.fromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
                st.write(f"**Ex-Dividend Date:** {ex_dividend_date_str}")
            else:
                st.write("**Ex-Dividend Date:** Ní dostupné")

            dividend_yield = info.get('dividendYield')
            if dividend_yield is not None:
                st.write(f"**Dividend Yield:** {dividend_yield * 100:.2f}%")
            else:
                st.write("**Dividend Yield:** Není dostupná")

            payout_ratio = info.get('payoutRatio')
            if payout_ratio is not None:
                st.write(f"**Payout Ratio:** {payout_ratio * 100:.2f}%")
            else:
                st.write("**Payout Ratio:** Není dostupná")

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
                df_dividends = dividends.to_frame(name='Dividend')
                df_dividends.index = df_dividends.index.strftime('%Y-%m-%d')
                df_dividends = df_dividends.reset_index().rename(columns={'index': 'Date'})
                df_dividends['% Change'] = df_dividends['Dividend'].pct_change() * 100
                df_dividends['Dividend'] = df_dividends['Dividend'].round(2)
                df_dividends['% Change'] = df_dividends['% Change'].round(2)
                st.write(df_dividends)
            else:
                st.write("Dividendová data nejsou k dispozici.")
