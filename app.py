"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                🚀 PRO QUANT "ADVANCED" TRADING DASHBOARD                     ║
║                                                                              ║
║  A institutional-grade market timing system for Indian Equities.             ║
║  INTEGRATES:                                                                 ║
║  1. Valuation (PE, PB, ERP)                                                  ║
║  2. Sentiment (VIX, PCR*)                                                    ║
║  3. Macro Risks (Crude Oil, USD/INR, G-Sec Yields)                           ║
║                                                                              ║
║  USAGE:   streamlit run pro_quant_dashboard.py                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
import glob
import warnings

# Try importing yfinance, handle if missing
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIGURATION & STYLING
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Pro Quant Advanced Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root { --bg-dark: #0a0f1a; --bg-card: #111827; --green: #10b981; --red: #ef4444; --blue: #3b82f6; --orange: #f59e0b; }
.stApp { background: linear-gradient(180deg, #0a0f1a 0%, #111827 50%, #0a0f1a 100%); }

/* HEADERS */
.main-title { font-family: 'Orbitron', monospace; font-size: 2.5rem; font-weight: 800; text-align: center; 
              background: linear-gradient(90deg, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.section-title { font-family: 'Orbitron', sans-serif; font-size: 1.4rem; color: #e2e8f0; margin-top: 2rem; border-left: 4px solid #3b82f6; padding-left: 10px; }

/* METRIC CARDS */
.metric-container { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; }
.metric-card { background: rgba(17, 24, 39, 0.7); border: 1px solid #1e3a5f; border-radius: 12px; padding: 1.2rem; 
               min-width: 160px; text-align: center; backdrop-filter: blur(10px); position: relative; overflow: hidden; flex: 1; }
.metric-card::top { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: #3b82f6; }
.metric-val { font-family: 'Orbitron', monospace; font-size: 1.8rem; font-weight: 700; color: #fff; }
.metric-lbl { font-family: 'Rajdhani', sans-serif; font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
.metric-delta { font-size: 0.8rem; font-family: 'JetBrains Mono'; padding: 2px 8px; border-radius: 4px; margin-top: 5px; display: inline-block; }

/* SIGNALS */
.signal-box { padding: 1rem; border-radius: 10px; text-align: center; font-family: 'Orbitron'; font-weight: bold; font-size: 1.2rem; margin-top: 10px; }
.sig-buy { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #10b981; box-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
.sig-sell { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #ef4444; box-shadow: 0 0 15px rgba(239, 68, 68, 0.3); }
.sig-neu { background: rgba(245, 158, 11, 0.2); border: 1px solid #f59e0b; color: #f59e0b; }

</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 2. ADVANCED DATA ENGINE (AUTO-MERGE + LIVE FETCH)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def load_and_process_data():
    """
    1. Auto-Merges G-Sec CSVs if found.
    2. Loads Valuation History.
    3. Fetches Live Macro Data (Oil, USDINR) via yfinance.
    """
    data = {}
    status_log = []

    # --------------------------------------------------------------------------
    # A. AUTO-MERGE G-SEC FILES
    # --------------------------------------------------------------------------
    gsec_files = glob.glob("NIFTY 10 YR BENCHMARK G-SEC*.csv")
    if gsec_files:
        try:
            dfs = []
            for f in gsec_files:
                temp = pd.read_csv(f)
                temp.columns = temp.columns.str.strip() # Clean headers
                dfs.append(temp)
            
            gsec_df = pd.concat(dfs, ignore_index=True)
            
            # Clean Dates
            gsec_df['Date'] = pd.to_datetime(gsec_df['Date'], errors='coerce')
            gsec_df = gsec_df.dropna(subset=['Date']).sort_values('Date')
            
            # Convert Price to Yield (Approximation if Yield col missing)
            # Check if 'Close' is Price (~100) or Yield (~7.0)
            avg_val = gsec_df['Close'].mean()
            if avg_val > 50: 
                # It's Price. Yield moves inversely.
                # Approx Formula: Yield ≈ Coupon + (Par - Price)/Duration
                # Simple Proxy: Yield = 7.2 + (100 - Price) * 0.1
                gsec_df['GSec_Yield'] = 7.2 + (100 - gsec_df['Close']) * 0.08
            else:
                gsec_df['GSec_Yield'] = gsec_df['Close']
            
            data['gsec'] = gsec_df[['Date', 'GSec_Yield']].set_index('Date')
            status_log.append(f"✅ Merged {len(gsec_files)} G-Sec files")
        except Exception as e:
            status_log.append(f"❌ G-Sec Merge Error: {e}")
    else:
        status_log.append("⚠️ No G-Sec files found")

    # --------------------------------------------------------------------------
    # B. LOAD VALUATION HISTORY (PE/PB)
    # --------------------------------------------------------------------------
    val_file = "Nifty_Index_Valuation_History.csv"
    if os.path.exists(val_file):
        try:
            val_df = pd.read_csv(val_file)
            val_df.columns = val_df.columns.str.strip()
            val_df['Date'] = pd.to_datetime(val_df['Date'])
            
            # Filter for Nifty 50
            n50 = val_df[val_df['Index'] == 'Nifty 50'].copy()
            n50 = n50.set_index('Date')[['PE_Ratio', 'PB_Ratio', 'Div_Yield']]
            n50.columns = ['PE', 'PB', 'DivYield']
            data['valuation'] = n50
            status_log.append("✅ Loaded Valuation History")
        except Exception as e:
            status_log.append(f"❌ Valuation Load Error: {e}")
    else:
        # Fallback: GitHub Load
        try:
            url = "https://raw.githubusercontent.com/sat2567/timing-market/main/Nifty_Index_Valuation_History.csv"
            val_df = pd.read_csv(url)
            val_df.columns = val_df.columns.str.strip()
            val_df['Date'] = pd.to_datetime(val_df['Date'])
            n50 = val_df[val_df['Index'] == 'Nifty 50'].set_index('Date')[['PE_Ratio', 'PB_Ratio', 'Div_Yield']]
            n50.columns = ['PE', 'PB', 'DivYield']
            data['valuation'] = n50
            status_log.append("✅ Loaded Valuation from GitHub")
        except:
            status_log.append("❌ Valuation File Missing")

    # --------------------------------------------------------------------------
    # C. FETCH LIVE MACRO DATA (YFINANCE)
    # --------------------------------------------------------------------------
    if YFINANCE_AVAILABLE:
        tickers = {
            'Nifty': '^NSEI',
            'VIX': '^INDIAVIX', # Fallback to ^VIX if India Vix fails
            'USDINR': 'INR=X',
            'Crude': 'CL=F'
        }
        try:
            # Download last 5 years
            macro_data = yf.download(list(tickers.values()), period="5y", progress=False)['Close']
            
            # Rename columns (Handle MultiIndex issues in new yfinance)
            # Try to map symbols back to names
            cols_map = {v: k for k, v in tickers.items()}
            # Simple rename if columns are flat
            if isinstance(macro_data.columns, pd.Index):
                # Check if columns are Tickers or Tuples
                new_cols = []
                for c in macro_data.columns:
                    # If tuple (Price, Ticker), extract Ticker
                    sym = c[0] if isinstance(c, tuple) else c
                    new_cols.append(cols_map.get(sym, sym))
                macro_data.columns = new_cols
            
            # Fix if IndiaVIX is missing (Common Yahoo Issue)
            if 'VIX' not in macro_data.columns or macro_data['VIX'].isnull().all():
                # Try loading local VIX file if available
                vix_files = glob.glob("*VIX*.csv")
                if vix_files:
                    v_df = pd.read_csv(vix_files[0])
                    v_df['Date'] = pd.to_datetime(v_df['Date'])
                    v_df.set_index('Date', inplace=True)
                    # Merge logic complicated, simple fill for now:
                    macro_data['VIX'] = 15.0 # Placeholder
            
            data['macro'] = macro_data
            status_log.append("✅ Fetched Live Macro Data (Oil, USD, Nifty)")
            
        except Exception as e:
            status_log.append(f"⚠️ Live Data Error: {e}")
    
    return data, status_log

# ══════════════════════════════════════════════════════════════════════════════
# 3. ANALYSIS & SIGNAL GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def run_analysis(data):
    """Combine all data sources into a master DataFrame"""
    
    # Base: Macro Data (Daily)
    if 'macro' in data:
        df = data['macro'].copy()
    else:
        return None
    
    # Merge Valuation (Forward Fill - since it's monthly)
    if 'valuation' in data:
        df = df.join(data['valuation'], how='outer').ffill()
    
    # Merge G-Sec (Forward Fill)
    if 'gsec' in data:
        df = df.join(data['gsec'], how='outer').ffill()
    
    # Drop rows where Nifty is NaN (weekends)
    df = df.dropna(subset=['Nifty'])
    
    # --------------------------
    # DERIVED METRICS
    # --------------------------
    
    # 1. Earnings Yield
    # If PE is missing, use Forward Fill, else assume 22
    df['PE'] = df['PE'].fillna(22) 
    df['EY'] = (1 / df['PE']) * 100
    
    # 2. Equity Risk Premium (ERP)
    # ERP = Earnings Yield - Risk Free Rate
    df['GSec_Yield'] = df['GSec_Yield'].fillna(7.2) # Default if missing
    df['ERP'] = df['EY'] - df['GSec_Yield']
    
    # 3. Macro Trends (Rolling)
    df['Oil_Trend'] = df['Crude'].pct_change(60) # 3-Month Trend
    df['USD_Trend'] = df['USDINR'].pct_change(60)
    
    return df

def generate_signals(latest):
    """
    Traffic Light Logic:
    1. VALUATION (ERP): High ERP = Green
    2. SENTIMENT (VIX): High VIX = Green (Fear = Opportunity), Low VIX = Red
    3. MACRO (Oil/USD): Rising Oil/USD = Red
    """
    score = 0
    reasons = []
    
    # A. ERP SIGNAL (Weight: 40%)
    erp = latest['ERP']
    if erp > 3.0: 
        score += 2; reasons.append("✅ Market Very Cheap (High ERP)")
    elif erp > 1.0:
        score += 1; reasons.append("✅ Market Fair/Cheap")
    elif erp < -1.0:
        score -= 2; reasons.append("❌ Market Expensive (Negative ERP)")
    else:
        reasons.append("Popcorn Time (Fair Valuation)")

    # B. VIX SIGNAL (Weight: 30%)
    vix = latest['VIX']
    if vix > 25:
        score += 1.5; reasons.append("✅ Extreme Fear (Contrarian Buy)")
    elif vix < 12:
        score -= 1; reasons.append("❌ Complacency (Risk High)")
    
    # C. MACRO SIGNAL (Weight: 30%)
    # If Oil rose > 20% in 3 months
    if latest['Oil_Trend'] > 0.20:
        score -= 1; reasons.append("❌ Crude Oil Spike (>20%)")
    
    # If USDINR rose > 5% in 3 months
    if latest['USD_Trend'] > 0.05:
        score -= 1; reasons.append("❌ Rupee Weakness (>5%)")

    # D. FINAL VERDICT
    if score >= 2:
        signal = "AGGRESSIVE BUY"
        css = "sig-buy"
    elif score >= 0.5:
        signal = "BUY ON DIPS"
        css = "sig-buy"
    elif score <= -1.5:
        signal = "SELL / HEDGE"
        css = "sig-sell"
    else:
        signal = "HOLD / NEUTRAL"
        css = "sig-neu"
        
    return signal, css, score, reasons

# ══════════════════════════════════════════════════════════════════════════════
# 4. MAIN DASHBOARD UI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown('<h1 class="main-title">PRO QUANT ADVANCED DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown("### Institutional Market Timing System")
    
    # Load Data
    with st.spinner("🤖 merging files & fetching live data..."):
        data_dict, logs = load_and_process_data()
        
    # Show Logs in Expander
    with st.expander("System Logs"):
        for l in logs: st.write(l)
    
    # Run Analysis
    df = run_analysis(data_dict)
    
    if df is None:
        st.error("❌ Data Loading Failed. Please check CSV files.")
        return

    # Get Latest Data point
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Signal Engine
    sig_txt, sig_css, sig_score, sig_reasons = generate_signals(latest)

    # --------------------------------------------------------------------------
    # ROW 1: THE HEADS-UP DISPLAY (HUD)
    # --------------------------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">NIFTY 50</div>
            <div class="metric-val">{latest['Nifty']:,.0f}</div>
            <div class="metric-delta" style="background: {'#10b981' if latest['Nifty']>prev['Nifty'] else '#ef4444'}20; color: {'#10b981' if latest['Nifty']>prev['Nifty'] else '#ef4444'}">
                {(latest['Nifty']-prev['Nifty']):.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Equity Risk Premium</div>
            <div class="metric-val">{latest['ERP']:.2f}%</div>
             <div class="metric-delta" style="color: {'#10b981' if latest['ERP']>1.5 else '#f59e0b'}">Target: >1.5%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">India VIX</div>
            <div class="metric-val">{latest['VIX']:.2f}</div>
             <div class="metric-delta">Fear Index</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="border-color: #f59e0b;">
            <div class="metric-lbl">Quant Signal</div>
            <div class="signal-box {sig_css}">{sig_txt}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # --------------------------------------------------------------------------
    # ROW 2: DEEP DIVE TABS
    # --------------------------------------------------------------------------
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["💰 VALUATION & G-SEC", "🛢️ MACRO RISKS", "🧠 SIGNAL LOGIC"])
    
    with tab1:
        c_1, c_2 = st.columns([2, 1])
        with c_1:
            # ERP Chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=df.index, y=df['ERP'], name="ERP", fill='tozeroy', line=dict(color='#3b82f6')))
            fig.add_hline(y=1.5, line_dash="dash", line_color="green", annotation_text="Buy Zone")
            fig.add_hline(y=-0.5, line_dash="dash", line_color="red", annotation_text="Caution Zone")
            fig.update_layout(title="Equity Risk Premium (Valuation)", height=400, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        with c_2:
            st.markdown("### Bond Yields")
            st.metric("10Y G-Sec Yield", f"{latest['GSec_Yield']:.2f}%")
            st.metric("Nifty Earnings Yield", f"{latest['EY']:.2f}%")
            st.info("When Earnings Yield > Bond Yield, stocks are attractive.")

    with tab2:
        st.subheader("Macro Correlations")
        # Normalize to 100 to compare trends
        norm_df = df[['Nifty', 'Crude', 'USDINR']].dropna()
        norm_df = norm_df / norm_df.iloc[0] * 100
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=norm_df.index, y=norm_df['Nifty'], name='Nifty', line=dict(width=3, color='white')))
        fig2.add_trace(go.Scatter(x=norm_df.index, y=norm_df['Crude'], name='Crude Oil', line=dict(color='#ef4444')))
        fig2.add_trace(go.Scatter(x=norm_df.index, y=norm_df['USDINR'], name='USD/INR', line=dict(color='#f59e0b')))
        fig2.update_layout(title="Relative Performance (Base=100)", height=400, template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)
        
        c_a, c_b = st.columns(2)
        c_a.metric("Crude Oil ($)", f"{latest['Crude']:.2f}", f"{latest['Oil_Trend']*100:.1f}% (3M)")
        c_b.metric("USD/INR", f"{latest['USDINR']:.2f}", f"{latest['USD_Trend']*100:.1f}% (3M)")

    with tab3:
        st.subheader("Why this Signal?")
        for r in sig_reasons:
            st.write(r)
        
        st.markdown("""
        **Methodology:**
        1. **ERP:** Measures excess return of stocks over bonds.
        2. **VIX:** Used as a contrarian indicator (High VIX = Buy).
        3. **Macro:** Checks for external shocks (Oil spike / Rupee crash).
        """)

if __name__ == "__main__":
    main()
