import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# ---------------------------------------------
# 📅 Sidebar vstupy
# ---------------------------------------------
st.set_page_config(page_title="Finanční dashboard", layout="wide")
@st.cache_data
def load_data(market):
    if market == "USA S&P 500":
        url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
    elif market == "USA NYSE":
        url = "https://raw.githubusercontent.com/Garik-ctrl/DataAnalyst/refs/heads/main/NYSE.csv"
    elif market == "USA NASDAQ - Global select":
        url = "https://raw.githubusercontent.com/Garik-ctrl/DataAnalyst/refs/heads/main/NASDAQ%20-%20Global%20select.csv"
    elif market == "USA NASDAQ - Capital market":
        url = "https://raw.githubusercontent.com/Garik-ctrl/DataAnalyst/refs/heads/main/NASDAQ%20-%20Capital%20market.csv"
    elif market == "USA NASDAQ - ADR":
        url = "https://raw.githubusercontent.com/Garik-ctrl/DataAnalyst/refs/heads/main/NASDAQ%20-%20ADR.csv"
    elif market == "USA NASDAQ - Global market":
        url = "https://raw.githubusercontent.com/Garik-ctrl/DataAnalyst/refs/heads/main/NASDAQ%20%20-%20Global%20market.csv"
    elif market == "USA AMEX":
        url = "https://raw.githubusercontent.com/Garik-ctrl/DataAnalyst/refs/heads/main/AMEX.csv"
    else:
        return pd.DataFrame()
    df = pd.read_csv(url)
    return df

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
    df=pd.DataFrame(data)
    return df

def assign_quartiles(series, labels=["Q1", "Q2", "Q3", "Q4"]):
    try:
        binned = pd.qcut(series, q=4, labels=labels, duplicates='drop')
        return binned
    except ValueError:
        return pd.Series(["N/A"] * len(series), index=series.index)

# ---------------------------------------------
# Karty
# ---------------------------------------------
tab1, tab4 = st.tabs([
    "🏦 Detail konkrétní firmy",
    "📊 Tabulka sektorů"
])

with tab1:
    st.title("Finanční data a dividendy")
    ticker_symbol = st.text_input("Zadejte ticker:", "SPG")
    start_date = st.date_input("Od", value=date(2022, 1, 1))
    end_date = st.date_input("Do", value=date.today())

    if ticker_symbol:
        ticker_data = yf.Ticker(ticker_symbol)
        info = ticker_data.info

        st.header("Informace o společnosti")
        st.write(f"**Název společnosti:** {info.get('shortName', 'N/A')}")
        st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
        st.write(f"**Průmysl:** {info.get('industry', 'N/A')}")

        hist_data = ticker_data.history(start=start_date, end=end_date)

        hist_data.index = hist_data.index.date
        hist_data['MA50'] = hist_data['Close'].rolling(window=50).mean()
        hist_data['MA200'] = hist_data['Close'].rolling(window=200).mean()

        st.subheader("Graf uzavíracích cen s MA50 a MA200")
        st.line_chart(hist_data[['Close', 'MA50', 'MA200']])

        st.subheader("Historická data")
        st.write(hist_data[::-1])

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
                st.write(f"**Dividend Yield:** {dividend_yield:.2f}%")
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
                st.write(df_dividends[::-1])
            else:
                st.write("Dividendová data nejsou k dispozici.")



# Tab 4 - Detail tickeru
with tab4:
    market = st.selectbox("Vyber burzu:", ["— vyberte —"] + [
        "USA S&P 500",
        "USA NYSE",
        "USA NASDAQ - Global select",
        "USA NASDAQ - Capital market",
        "USA NASDAQ - ADR",
        "USA NASDAQ - Global market",
        "USA AMEX"
    ])
    if market!="— vyberte —":
        sp500_df = load_data(market)
        tickers = sp500_df['Symbol'].to_list()

        financial_df = fetch_extended_data(tickers)
        financial_df.dropna(subset=['Sector', 'P/E', 'ROE'], inplace=True)

        sectors = financial_df['Sector'].dropna().unique()
        selected_sector = st.selectbox("Vyber sektor:", sorted(sectors))

        sector_df = financial_df[financial_df['Sector'] == selected_sector].copy()
        sector_df.sort_values('P/E', inplace=True)
        sector_df['Quartile'] = assign_quartiles(sector_df['P/E'])

        st.subheader(f"Firmy v sektoru: {selected_sector}")
        st.dataframe(sector_df[['Ticker','Name','P/E','ROE','Quartile']].set_index('Ticker'))
        # ----------------------------------------------------------------------------------------
        st.subheader(f"Boxplot P/E")
        fig = px.box(
            sector_df,
            x='P/E',
            points='all',
            hover_name='Name',
            hover_data={'Ticker': True, 'P/E': ':.2f'},
            title=f'Distribuce P/E - {selected_sector}'
        )
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(visible=True),
                fixedrange=False
            ),
            yaxis=dict(
                fixedrange=False
            ),
            dragmode="pan",
            height=500
        )
        fig.update_traces(marker=dict(size=6, opacity=0.5))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        #----------------------------------------------------------------------------------------
        st.subheader(f"Scatter plot P/E vs ROE")
        fig = px.scatter(
            sector_df,
            x='P/E',
            y='ROE',
            hover_name='Name',
            hover_data={'Ticker': True, 'P/E': ':.2f', 'ROE': ':.2f'},
            text='Ticker',
            title=f"P/E vs ROE - {selected_sector}"
        )
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(visible=True),  # posuvník dole pro osu X
                fixedrange=False,  # povolí zoom/scroll X
            ),
            yaxis=dict(
                fixedrange=False  # povolí zoom/scroll Y
            ),
            dragmode='pan',  # myší můžeš táhnout plochu
            height=600
        )

        fig.update_traces(marker=dict(size=12, opacity=0.7), textposition='top center')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Prosím, nejprve vyber burzu/index.")
        st.stop()
