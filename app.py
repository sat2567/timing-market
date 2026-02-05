import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# ==========================================
# 1. CONFIGURATION & STYLE
# ==========================================
st.set_page_config(layout="wide", page_title="Institutional Quant Dashboard", page_icon="📈")

# Custom CSS for the "Dark Quant" look
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .metric-card {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .metric-title {
        color: #888;
        font-size: 14px;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #FFF;
        font-size: 24px;
        font-weight: bold;
    }
    .bullish { color: #00FF00; }
    .bearish { color: #FF4444; }
    .neutral { color: #FFBB00; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADER ENGINE
# ==========================================
@st.cache_data
def load_and_process_data():
    # --- A. Define File Paths ---
    files = {
        'Global_Gold': 'gold_data.csv',
        'Global_SP500': 'sp500_data.csv',
        'Global_US10Y': 'us10y_data.csv',
        'Domestic_Nifty_Price': 'Nifty50_Historical_Yahoo.csv',
        'Domestic_Midcap_Price': 'NIFTY_MIDCAP_100_Historical_Yahoo.csv',
        'Domestic_VIX': 'India_VIX_Yahoo.csv',
        'Domestic_Bond': 'India 10-Year Bond Yield Historical Data.csv',
        'Val_Nifty': 'Nifty50_PE_PB_Div_Merged.csv',
        'Val_Midcap': 'NiftyMidcap100_PE_PB_Div_Merged.csv',
        'Val_Smallcap': 'NiftySmallcap250_PE_PB_Div_Merged.csv'
    }

    # --- B. Helper: Clean & Standardize ---
    def load_csv(path, date_col='Date', val_col=None, rename_to=None):
        try:
            df = pd.read_csv(path)
            # Handle different date formats (Investing.com vs Yahoo)
            try:
                df[date_col] = pd.to_datetime(df[date_col], format='%d-%m-%Y') # Try India format first
            except:
                df[date_col] = pd.to_datetime(df[date_col]) # Auto-detect (usually YYYY-MM-DD)
            
            df = df.set_index(date_col)
            
            if val_col and rename_to:
                # If column name differs (e.g., 'Price' vs 'Close')
                if val_col not in df.columns and 'Price' in df.columns: val_col = 'Price'
                if val_col not in df.columns and 'Close' in df.columns: val_col = 'Close'
                
                df = df[[val_col]].rename(columns={val_col: rename_to})
                # Clean numeric data (remove % symbols if any)
                if df[rename_to].dtype == 'O':
                    df[rename_to] = df[rename_to].astype(str).str.replace('%', '').str.replace(',', '').astype(float)
            return df
        except Exception as e:
            st.error(f"Error loading {path}: {e}")
            return pd.DataFrame()

    # --- C. Load All Datasets ---
    # Global
    gold = load_csv(files['Global_Gold'], val_col='Gold', rename_to='Gold_Price')
    sp500 = load_csv(files['Global_SP500'], val_col='SP500', rename_to='SP500_Price')
    us10y = load_csv(files['Global_US10Y'], val_col='US10Y_Yield', rename_to='US10Y')
    
    # Domestic Prices
    nifty = load_csv(files['Domestic_Nifty_Price'], val_col='Close', rename_to='Nifty_Price')
    midcap = load_csv(files['Domestic_Midcap_Price'], val_col='Close', rename_to='Midcap_Price')
    vix = load_csv(files['Domestic_VIX'], val_col='VIX_Close', rename_to='VIX')
    bond = load_csv(files['Domestic_Bond'], val_col='Price', rename_to='India_10Y')
    
    # Domestic Valuations (Need PE)
    nifty_pe = load_csv(files['Val_Nifty'], val_col='PE', rename_to='Nifty_PE')
    mid_pe = load_csv(files['Val_Midcap'], val_col='PE', rename_to='Midcap_PE')
    small_pe = load_csv(files['Val_Smallcap'], val_col='PE', rename_to='Smallcap_PE')

    # --- D. Merge into Master Dataframe ---
    dfs = [nifty, midcap, gold, sp500, us10y, vix, bond, nifty_pe, mid_pe, small_pe]
    master = dfs[0]
    for df in dfs[1:]:
        master = master.join(df, how='outer')
    
    master = master.sort_index().ffill().dropna()
    return master

# ==========================================
# 3. ANALYSIS ALGORITHMS
# ==========================================
def run_quant_analysis(df):
    # 1. Yield Gap (Fed Model)
    # Nifty Earnings Yield = 100 / PE
    # Gap = EY - Bond Yield. Negative = Stocks Expensive.
    df['Earnings_Yield'] = 100 / df['Nifty_PE']
    df['Yield_Gap'] = df['Earnings_Yield'] - df['India_10Y']
    
    # 2. Valuation Spreads (Z-Scores)
    # Rolling 2-Year Mean/Std to normalize "Cheapness"
    window = 252 * 2
    
    # Midcap
    df['Mid_Nifty_Ratio'] = df['Midcap_PE'] / df['Nifty_PE']
    df['Mid_Z'] = (df['Mid_Nifty_Ratio'] - df['Mid_Nifty_Ratio'].rolling(window).mean()) / df['Mid_Nifty_Ratio'].rolling(window).std()
    
    # Smallcap
    df['Small_Nifty_Ratio'] = df['Smallcap_PE'] / df['Nifty_PE']
    df['Small_Z'] = (df['Small_Nifty_Ratio'] - df['Small_Nifty_Ratio'].rolling(window).mean()) / df['Small_Nifty_Ratio'].rolling(window).std()
    
    # 3. Global Risk Regime
    # Gold/Nifty Ratio Trend
    df['Gold_Nifty'] = df['Gold_Price'] / df['Nifty_Price']
    df['Risk_MA'] = df['Gold_Nifty'].rolling(200).mean()
    df['Regime'] = np.where(df['Gold_Nifty'] > df['Risk_MA'], "RISK OFF", "RISK ON")
    
    # 4. Master Signal Logic
    # IF Risk Off OR VIX > 22 -> GOLD/CASH
    # IF Risk On AND Midcap Cheap (Z < -1) -> MIDCAP
    # ELSE -> NIFTY
    conditions = [
        (df['Regime'] == "RISK OFF") | (df['VIX'] > 22),
        (df['Regime'] == "RISK ON") & (df['Mid_Z'] < -1.0)
    ]
    choices = ["🛡️ GOLD / CASH", "🚀 MIDCAPS"]
    df['Signal'] = np.select(conditions, choices, default="🏢 NIFTY 50")
    
    return df

# ==========================================
# 4. DASHBOARD UI
# ==========================================
st.title("🇮🇳 Institutional Market Scanner")
st.markdown("Global Macro Inputs + Domestic Valuation Spreads")

# Load & Analyze
try:
    data = load_and_process_data()
    df = run_quant_analysis(data)
    latest = df.iloc[-1]
    
    # --- HEADER: MASTER SIGNAL ---
    st.divider()
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        st.subheader("📢 MASTER STRATEGY SIGNAL")
        color = "#FF4444" if "GOLD" in latest['Signal'] else "#00FF00"
        st.markdown(f"<h1 style='color:{color};'>{latest['Signal']}</h1>", unsafe_allow_html=True)
        st.markdown(f"**Regime:** {latest['Regime']} | **VIX:** {latest['VIX']:.2f}")

    with c2:
        st.markdown("**Yield Gap (Valuation)**")
        gap_color = "bearish" if latest['Yield_Gap'] < 0.5 else "bullish"
        st.markdown(f"<span class='metric-value {gap_color}'>{latest['Yield_Gap']:.2f}%</span>", unsafe_allow_html=True)
        st.caption("Negative = Bonds Attractive")
        
    with c3:
        st.markdown("**Midcap Spread (Z-Score)**")
        mid_color = "bullish" if latest['Mid_Z'] < -1 else ("bearish" if latest['Mid_Z'] > 1.5 else "neutral")
        st.markdown(f"<span class='metric-value {mid_color}'>{latest['Mid_Z']:.2f}</span>", unsafe_allow_html=True)
        st.caption("<-1.0 is Cheap")

    st.divider()

    # --- TABS FOR DETAILED ANALYSIS ---
    tab1, tab2, tab3 = st.tabs(["📊 Valuation Radar", "🌍 Global Macro", "📈 Backtest Performance"])
    
    with tab1:
        st.subheader("Domestic Valuation Spreads")
        
        # Plot 1: Yield Gap
        fig_gap = go.Figure()
        fig_gap.add_trace(go.Scatter(x=df.index, y=df['Yield_Gap'], fill='tozeroy', name='Earnings Yield Gap', line=dict(color='#00CC96')))
        fig_gap.add_hline(y=0, line_dash="dash", line_color="red")
        fig_gap.update_layout(title="Equity vs Bond Yield Gap (The 'Fed Model')", height=350, template="plotly_dark")
        st.plotly_chart(fig_gap, use_container_width=True)
        
        # Plot 2: Mid/Small Cap Z-Scores
        fig_z = go.Figure()
        fig_z.add_trace(go.Scatter(x=df.index, y=df['Mid_Z'], name='Midcap Premium (Z)', line=dict(color='cyan')))
        fig_z.add_trace(go.Scatter(x=df.index, y=df['Small_Z'], name='Smallcap Premium (Z)', line=dict(color='magenta')))
        fig_z.add_hline(y=1.5, line_dash="dash", line_color="red", annotation_text="Expensive")
        fig_z.add_hline(y=-1.5, line_dash="dash", line_color="#00FF00", annotation_text="Buy Zone")
        fig_z.update_layout(title="Mid & Small Cap Relative Valuations (Z-Scores)", height=350, template="plotly_dark")
        st.plotly_chart(fig_z, use_container_width=True)

    with tab2:
        st.subheader("Global Liquidity & Risk")
        c_a, c_b = st.columns(2)
        
        with c_a:
            # Plot 3: US 10Y Yield
            fig_us = go.Figure()
            fig_us.add_trace(go.Scatter(x=df.index, y=df['US10Y'], name='US 10Y Yield', line=dict(color='yellow')))
            fig_us.update_layout(title="Global Cost of Capital (US 10Y Yield)", height=300, template="plotly_dark")
            st.plotly_chart(fig_us, use_container_width=True)
            
        with c_b:
            # Plot 4: Gold/Nifty Ratio
            fig_risk = go.Figure()
            fig_risk.add_trace(go.Scatter(x=df.index, y=df['Gold_Nifty'], name='Gold/Nifty Ratio', line=dict(color='gold')))
            fig_risk.add_trace(go.Scatter(x=df.index, y=df['Risk_MA'], name='Regime Trend', line=dict(color='white', dash='dot')))
            fig_risk.update_layout(title="Risk-Off Detector (Gold Outperformance)", height=300, template="plotly_dark")
            st.plotly_chart(fig_risk, use_container_width=True)

    with tab3:
        st.subheader("Strategy Backtest (Switching Logic)")
        
        # Simple Backtest Calculation
        df['Nifty_Ret'] = df['Nifty_Price'].pct_change()
        df['Midcap_Ret'] = df['Midcap_Price'].pct_change()
        df['Gold_Ret'] = df['Gold_Price'].pct_change()
        
        # Shift Signal for Next Day Execution
        df['Position'] = df['Signal'].shift(1)
        
        df['Strat_Ret'] = 0.0
        df.loc[df['Position'].astype(str).str.contains('NIFTY'), 'Strat_Ret'] = df['Nifty_Ret']
        df.loc[df['Position'].astype(str).str.contains('MIDCAP'), 'Strat_Ret'] = df['Midcap_Ret']
        df.loc[df['Position'].astype(str).str.contains('GOLD'), 'Strat_Ret'] = df['Gold_Ret']
        
        # Cumulative
        df['Equity_Curve'] = (1 + df['Strat_Ret']).cumprod()
        df['Benchmark'] = (1 + df['Nifty_Ret']).cumprod()
        
        # Plot Performance
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Scatter(x=df.index, y=df['Equity_Curve'], name='Quant Strategy', line=dict(color='#00FF00', width=2)))
        fig_perf.add_trace(go.Scatter(x=df.index, y=df['Benchmark'], name='Nifty 50 Buy & Hold', line=dict(color='gray', dash='dash')))
        fig_perf.update_layout(title="Strategy vs Benchmark", height=400, template="plotly_dark")
        st.plotly_chart(fig_perf, use_container_width=True)
        
        st.markdown("#### Recent Signals")
        st.dataframe(df[['Signal', 'Yield_Gap', 'Mid_Z', 'Regime']].tail(10).sort_index(ascending=False))

except Exception as e:
    st.error(f"Data Processing Error: {e}")
    st.info("Please ensure all 10 CSV files are in the same folder as this script.")
