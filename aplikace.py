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
            mcap = info.get('marketCap')
            if info.get('trailingPE',None)!='Infinity':
                data.append({
                    'Ticker': ticker,
                    'Name': info.get('shortName',None),
                    'Sector': info.get('sector',None),
                    'P/E': info.get('trailingPE',None),
                    'ROE': roe * 100 if roe is not None else None,
                    'Div': info.get('dividendYield',0),
                    'Market Cap': mcap
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
    col_1, left_col, right_col = st.columns(3)
    with col_1:
        ticker_symbol = st.text_input("Zadejte ticker:", "SPG")
        start_date = st.date_input("Od", value=date(2022, 1, 1))
        end_date = st.date_input("Do", value=date.today())

        if ticker_symbol:
            ticker_data = yf.Ticker(ticker_symbol)
            info = ticker_data.info

    with left_col:
        st.subheader("Hodnoty")
        ex_dividend_date = info.get('exDividendDate')
        if ex_dividend_date:
            ex_dividend_date_str = datetime.fromtimestamp(ex_dividend_date).strftime('%Y-%m-%d')
            st.write(f"**Ex-Dividend Date:** {ex_dividend_date_str}")
        else:
            st.write("**Ex-Dividend Date:** Není dostupné")

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

            # Výpočet a zaokrouhlení
            df_dividends['% Change'] = df_dividends['Dividend'].pct_change() * 100
            df_dividends['Dividend'] = df_dividends['Dividend'].round(2)
            df_dividends['% Change'] = df_dividends['% Change'].round(2)

            # Funkce pro podmíněné formátování
            def background_change(val):
                if pd.isna(val):
                    return ''
                color = 'lightgreen' if val > 0 else 'lightcoral' if val < 0 else ''
                return f'background-color: {color}'

            styled_dividends = (
                df_dividends[::-1]
                .style
                .format({'Dividend': '{:.2f}', '% Change': '{:.2f}'})
                .applymap(background_change, subset=['% Change'])
            )
            st.dataframe(styled_dividends, use_container_width=True)
        else:
            st.write("Dividendová data nejsou k dispozici.")

    st.markdown("---")
    col_info, col_history = st.columns(2)
    with col_info:
        st.header("Informace o společnosti")
        st.write(f"**Název společnosti:** {info.get('shortName', 'N/A')}")
        st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
        st.write(f"**Průmysl:** {info.get('industry', 'N/A')}")
    with col_history:
        hist_data = ticker_data.history(start=start_date, end=end_date)
        hist_data.index = hist_data.index.date
        hist_data['MA50'] = hist_data['Close'].rolling(window=50).mean()
        hist_data['MA200'] = hist_data['Close'].rolling(window=200).mean()

        st.subheader("Graf uzavíracích cen s MA50 a MA200")
        st.line_chart(hist_data[['Close', 'MA50', 'MA200']])

    st.markdown("---")
    st.subheader("Historická data")
    st.write(hist_data[::-1])



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
        financial_df.dropna(subset=['Sector', 'P/E', 'ROE','Div', 'Market Cap'], inplace=True)

        sectors = financial_df['Sector'].dropna().unique()
        selected_sector = st.selectbox("Vyber sektor:", sorted(sectors))

        sector_df = financial_df[financial_df['Sector'] == selected_sector].copy()
        sector_df = sector_df[~sector_df['P/E'].astype(str).str.contains('infi', na=False)]
        sector_df['P/E'] = round(pd.to_numeric(sector_df['P/E'], errors='coerce'),2)
        sector_df['ROE'] = round(pd.to_numeric(sector_df['ROE'], errors='coerce'),2)
        sector_df['Div'] = round(pd.to_numeric(sector_df['Div'], errors='coerce'),2)
        sector_df['Market Cap'] = round(pd.to_numeric(sector_df['Market Cap'], errors='coerce'),2)
        sector_df['Market Cap (B)'] = round(pd.to_numeric(sector_df['Market Cap'], errors='coerce')/1e9,2)
        sector_df = sector_df.dropna(subset=['P/E'])
        sector_df = sector_df.dropna(subset=['ROE'])
        sector_df = sector_df.dropna(subset=['Div'])
        sector_df = sector_df.dropna(subset=['Market Cap (B)'])
        sector_df.sort_values('P/E', inplace=True)
        sector_df['Quartile'] = assign_quartiles(sector_df['P/E'])

        st.subheader(f"Firmy v sektoru: {selected_sector}")
        st.dataframe(sector_df[['Ticker','Name','P/E','ROE','Div','Market Cap (B)','Quartile']].set_index('Ticker'))
        # ----------------------------------------------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            min_pe = float(sector_df['P/E'].min())
            max_pe = float(sector_df['P/E'].max())
            
            if min_pe!=max_pe:
                pe_range = st.slider(
                    "Vyber rozsah P/E pro zobrazení",
                    min_value=min_pe,
                    max_value=max_pe,
                    value=(min_pe, max_pe),
                    step=0.5
                )
            else:
                pe_range=(min_pe,max_pe)

        with col2:
            min_ROE = float(sector_df['ROE'].min())
            max_ROE = float(sector_df['ROE'].max())

            if min_ROE != max_ROE:
                ROE_range = st.slider(
                    "Vyber rozsah ROE pro zobrazení",
                    min_value=min_ROE,
                    max_value=max_ROE,
                    value=(min_ROE, max_ROE),
                    step=0.5
                )
            else:
                ROE_range=(min_ROE,max_ROE)

        with col3:
            min_Div = float(sector_df['Div'].min())
            max_Div = float(sector_df['Div'].max())

            if min_Div != max_Div:
                Div_range = st.slider(
                    "Vyber rozsah Div pro zobrazení",
                    min_value=min_Div,
                    max_value=max_Div,
                    value=(min_Div, max_Div),
                    step=0.5
                )
            else:
                Div_range = (min_Div, max_Div)
        with col4:
            min_MC = float(sector_df['Market Cap (B)'].min())
            max_MC = float(sector_df['Market Cap (B)'].max())

            if min_MC != max_MC:
                MC_range = st.slider(
                    "Vyber rozsah Market Cap pro zobrazení",
                    min_value=min_MC,
                    max_value=max_MC,
                    value=(min_MC, max_MC),
                    step=0.5
                )
            else:
                MC_range=(min_MC,max_MC)
                
        filtered_df = sector_df[
            (sector_df['P/E'] >= pe_range[0]) &
            (sector_df['P/E'] <= pe_range[1]) &
            (sector_df['ROE'] >= ROE_range[0]) &
            (sector_df['ROE'] <= ROE_range[1]) &
            (sector_df['Div'] >= Div_range[0]) &
            (sector_df['Div'] <= Div_range[1]) &
            (sector_df['Market Cap (B)'] >= MC_range[0]) &
            (sector_df['Market Cap (B)'] <= MC_range[1])
                ]

        left_col, middle_col, right_col = st.columns(3)

        with left_col:
            #----------------------------------------------------------------------------------------
            fig = px.scatter(
                filtered_df,
                x='P/E',
                y='ROE',
                hover_name='Name',
                hover_data={'Ticker': True, 'P/E': ':.2f', 'ROE': ':.2f', 'Div': ':.2f','Market Cap (B)': ':.2f'},
                text='Ticker',
                title=f"P/E vs ROE - {selected_sector}"
            )

            fig.update_traces(marker=dict(size=12, opacity=0.7), textposition='top center')
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

        with middle_col:
            # ----------------------------------------------------------------------------------------
            fig = px.scatter(
                filtered_df,
                x='P/E',
                y='Div',
                hover_name='Name',
                hover_data={'Ticker': True, 'P/E': ':.2f', 'ROE': ':.2f', 'Div': ':.2f','Market Cap (B)': ':.2f'},
                text='Ticker',
                title=f"P/E vs Div - {selected_sector}"
            )
            fig.update_traces(marker=dict(size=12, opacity=0.7), textposition='top center')
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        with right_col:
            # ----------------------------------------------------------------------------------------
            fig = px.scatter(
                filtered_df,
                x='P/E',
                y='Market Cap (B)',
                hover_name='Name',
                hover_data={'Ticker': True, 'P/E': ':.2f', 'ROE': ':.2f', 'Div': ':.2f','Market Cap (B)': ':.2f'},
                text='Ticker',
                title=f"P/E vs Market Cap - {selected_sector}"
            )
            fig.update_traces(marker=dict(size=12, opacity=0.7), textposition='top center')
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Prosím, nejprve vyber burzu/index.")
        st.stop()
