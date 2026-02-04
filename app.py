"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 PRO QUANT MARKET TIMING DASHBOARD                      ║
║                                                                              ║
║  A comprehensive market analysis system for Indian equity markets            ║
║  Features: ERP Analysis | VIX Signals | Multi-Cap Valuation | Sector Rotation║
║                                                                              ║
║  USAGE:   streamlit run pro_quant_dashboard.py                               ║
║  REQUIREMENTS: pip install streamlit pandas numpy plotly                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Pro Quant Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root { --bg-dark: #0a0f1a; --bg-card: #111827; --green: #10b981; --red: #ef4444; --blue: #3b82f6; }
.stApp { background: linear-gradient(180deg, #0a0f1a 0%, #111827 50%, #0a0f1a 100%); }
.main-title { font-family: 'Orbitron', monospace; font-size: 2.5rem; font-weight: 800; text-align: center; background: linear-gradient(90deg, #10b981, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0; }
.subtitle { font-family: 'Rajdhani', sans-serif; font-size: 1rem; color: #64748b; text-align: center; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 2rem; }
.metric-card { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 1px solid #1e3a5f; border-radius: 16px; padding: 1.5rem; text-align: center; position: relative; overflow: hidden; }
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #10b981, #06b6d4, #3b82f6); }
.metric-value { font-family: 'Orbitron', monospace; font-size: 2rem; font-weight: 700; color: #e2e8f0; }
.metric-label { font-family: 'Rajdhani', sans-serif; font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 2px; }
.signal-badge { font-family: 'Orbitron', monospace; font-size: 1.2rem; font-weight: 700; padding: 0.8rem 1.5rem; border-radius: 12px; display: inline-block; letter-spacing: 2px; }
.signal-buy { background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
.signal-sell { background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: white; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
.signal-hold { background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%); color: white; }
.regime-banner { font-family: 'Orbitron', monospace; font-size: 1.2rem; font-weight: 700; padding: 1rem; border-radius: 12px; text-align: center; margin: 1rem 0; letter-spacing: 2px; }
.regime-bull { background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; color: #10b981; }
.regime-bear { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; }
.regime-neutral { background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; color: #f59e0b; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HYBRID DATA LOADING (LOCAL -> GITHUB FALLBACK)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def load_market_data():
    """Load market data from Local Files first, then GitHub"""
    
    data = {}
    
    # 1. Configuration
    GITHUB_BASE = "https://raw.githubusercontent.com/sat2567/timing-market/main/"
    
    file_configs = {
        'vix': {'file': 'India_VIX_Yahoo.csv', 'date_col': 'Date'},
        'nifty50': {'file': 'Nifty50_Historical_Yahoo.csv', 'date_col': 'Date'},
        'midcap': {'file': 'NIFTY_MIDCAP_100_Historical_Yahoo.csv', 'date_col': 'Date'},
        'pe_data': {'file': 'Nifty_Index_Valuation_History.csv', 'date_col': 'Date'}, 
        'gsec': {'file': 'Nifty_10Y_Benchmark_GSec_Merged.csv', 'date_col': 'Date'},
    }
    
    # 2. Loop and Load
    for key, config in file_configs.items():
        fname = config['file']
        date_col = config['date_col']
        df = None
        source = "None"
        
        # A. TRY LOCAL FILE
        if os.path.exists(fname):
            try:
                df = pd.read_csv(fname)
                source = "Local"
            except Exception as e:
                st.sidebar.warning(f"⚠️ Local {fname} found but failed: {e}")

        # B. TRY GITHUB (if local failed)
        if df is None:
            try:
                url = GITHUB_BASE + fname.replace(" ", "%20")
                df = pd.read_csv(url)
                source = "GitHub"
            except Exception as e:
                # Silent fail here, we report at the end
                pass
        
        # C. PROCESS DATA (if loaded)
        if df is not None:
            df.columns = df.columns.str.strip()
            
            # Smart Date Parsing
            if date_col in df.columns:
                # Convert varying formats
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                # Remove rows with invalid dates
                df = df.dropna(subset=[date_col])
                data[key] = df
                st.sidebar.success(f"✅ Loaded {key} from {source}")
            else:
                st.sidebar.error(f"❌ Column '{date_col}' missing in {fname}")
                data[key] = None
        else:
            # If GSEC merged file is missing, try to merge parts on the fly? 
            # (Skipping complex logic for now to keep script stable)
            st.sidebar.error(f"❌ Could not load {fname} (Check path or GitHub)")
            data[key] = None
            
    return data

def create_dashboard_data(raw_data):
    """Process raw data into dashboard-ready format"""
    
    # Check if we have minimum required data
    if raw_data.get('nifty50') is None:
        return None, None, None
    
    # ═══ DAILY DATA ═══
    nifty = raw_data['nifty50'].copy()
    daily = nifty[['Date', 'Close']].copy()
    daily.columns = ['Date', 'Nifty50']
    
    # Add VIX
    if raw_data.get('vix') is not None:
        vix = raw_data['vix'][['Date', 'VIX_Close']].copy()
        vix.columns = ['Date', 'VIX']
        daily = pd.merge(daily, vix, on='Date', how='left')
    else:
        daily['VIX'] = 15  # Default
    
    # Add Midcap
    if raw_data.get('midcap') is not None:
        midcap = raw_data['midcap'][['Date', 'Close']].copy()
        midcap.columns = ['Date', 'Midcap100']
        daily = pd.merge(daily, midcap, on='Date', how='left')
    
    # Add G-Sec Yield
    if raw_data.get('gsec') is not None:
        gsec = raw_data['gsec'][['Date', 'Close']].copy()
        # Ensure numeric
        gsec['Close'] = pd.to_numeric(gsec['Close'], errors='coerce')
        
        # Convert Price to Yield Estimate
        # If the file contains Prices (~80-110), we approximate yield.
        # Approx: Yield = 7.2 + (100 - Price) * 0.08
        gsec['GSec_Yield'] = 7.2 + (100 - gsec['Close']) * 0.08 
        
        gsec = gsec[['Date', 'GSec_Yield']]
        daily = pd.merge(daily, gsec, on='Date', how='left')
    else:
        daily['GSec_Yield'] = 7.2
    
    # Sort and fill
    daily = daily.sort_values('Date').reset_index(drop=True)
    daily = daily.ffill()
    
    # Technical Indicators
    daily['SMA_50'] = daily['Nifty50'].rolling(50).mean()
    daily['SMA_200'] = daily['Nifty50'].rolling(200).mean()
    daily['ATH'] = daily['Nifty50'].expanding().max()
    daily['Drawdown'] = ((daily['Nifty50'] / daily['ATH']) - 1) * 100
    
    # RSI
    delta = daily['Nifty50'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    daily['RSI'] = 100 - (100 / (1 + rs))
    
    # ═══ MONTHLY DATA ═══
    monthly = daily.groupby(daily['Date'].dt.to_period('M')).agg({
        'Nifty50': 'last',
        'VIX': 'mean',
        'GSec_Yield': 'last',
        'RSI': 'last',
        'Drawdown': 'last'
    }).reset_index()
    monthly['Date'] = monthly['Date'].dt.to_timestamp() + pd.offsets.MonthEnd(0)
    
    # Add PE Data
    if raw_data.get('pe_data') is not None:
        pe_df = raw_data['pe_data']
        
        # Nifty 50 PE
        n50_pe = pe_df[pe_df['Index'] == 'Nifty 50'][['Date', 'PE_Ratio', 'PB_Ratio', 'Div_Yield']].copy()
        n50_pe['Date'] = pd.to_datetime(n50_pe['Date']) + pd.offsets.MonthEnd(0)
        n50_pe.columns = ['Date', 'Nifty50_PE', 'Nifty50_PB', 'Nifty50_DivYield']
        monthly = pd.merge(monthly, n50_pe, on='Date', how='left')
        
        # Midcap PE
        mid_pe = pe_df[pe_df['Index'] == 'Nifty Midcap 100'][['Date', 'PE_Ratio']].copy()
        mid_pe['Date'] = pd.to_datetime(mid_pe['Date']) + pd.offsets.MonthEnd(0)
        mid_pe.columns = ['Date', 'Midcap_PE']
        monthly = pd.merge(monthly, mid_pe, on='Date', how='left')
        
        # Smallcap PE
        sm_pe = pe_df[pe_df['Index'] == 'Nifty Smallcap 100'][['Date', 'PE_Ratio']].copy()
        sm_pe['Date'] = pd.to_datetime(sm_pe['Date']) + pd.offsets.MonthEnd(0)
        sm_pe.columns = ['Date', 'Smallcap_PE']
        monthly = pd.merge(monthly, sm_pe, on='Date', how='left')
    
    # Fill missing PE with defaults
    monthly['Nifty50_PE'] = monthly.get('Nifty50_PE', pd.Series([22]*len(monthly))).fillna(22)
    monthly['Midcap_PE'] = monthly.get('Midcap_PE', pd.Series([28]*len(monthly))).fillna(28)
    monthly['Smallcap_PE'] = monthly.get('Smallcap_PE', pd.Series([25]*len(monthly))).fillna(25)
    
    # Calculate ERP
    monthly['Earnings_Yield'] = (1 / monthly['Nifty50_PE']) * 100
    monthly['ERP'] = monthly['Earnings_Yield'] - monthly['GSec_Yield']
    
    # PE Percentiles
    monthly['Nifty50_PE_Pct'] = monthly['Nifty50_PE'].rank(pct=True) * 100
    monthly['Midcap_PE_Pct'] = monthly['Midcap_PE'].rank(pct=True) * 100
    monthly['Smallcap_PE_Pct'] = monthly['Smallcap_PE'].rank(pct=True) * 100
    
    # ═══ SECTOR DATA ═══
    sector_data = None
    if raw_data.get('pe_data') is not None:
        pe_df = raw_data['pe_data']
        latest_date = pe_df['Date'].max()
        sector_data = pe_df[pe_df['Date'] == latest_date][['Index', 'PE_Ratio', 'PB_Ratio', 'Div_Yield']].copy()
        
        # Calculate percentiles for each sector
        sector_pcts = []
        for idx in sector_data['Index'].unique():
            idx_hist = pe_df[pe_df['Index'] == idx]['PE_Ratio']
            if len(idx_hist) > 5:
                current_pe = sector_data[sector_data['Index'] == idx]['PE_Ratio'].values[0]
                pct = (idx_hist < current_pe).mean() * 100
                sector_pcts.append({'Index': idx, 'PE_Percentile': pct})
        
        if sector_pcts:
            sector_pct_df = pd.DataFrame(sector_pcts)
            sector_data = pd.merge(sector_data, sector_pct_df, on='Index', how='left')
            sector_data = sector_data.sort_values('PE_Percentile')
    
    return daily, monthly, sector_data


# ══════════════════════════════════════════════════════════════════════════════
# SIGNAL LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def get_erp_signal(erp):
    if pd.isna(erp): return 'NO DATA', 0, '#64748b'
    if erp > 3: return 'VERY CHEAP', 2, '#10b981'
    if erp > 1.5: return 'CHEAP', 1, '#34d399'
    if erp > 0: return 'FAIR', 0, '#f59e0b'
    if erp > -1.5: return 'EXPENSIVE', -1, '#f97316'
    return 'VERY EXPENSIVE', -2, '#ef4444'

def get_vix_signal(vix):
    if pd.isna(vix): return 'NO DATA', 0, '#64748b'
    if vix > 28: return 'EXTREME FEAR', 2, '#10b981'
    if vix > 22: return 'FEAR', 1, '#34d399'
    if vix > 15: return 'NORMAL', 0, '#f59e0b'
    if vix > 12: return 'COMPLACENT', -1, '#f97316'
    return 'EXTREME GREED', -2, '#ef4444'

def get_composite_signal(erp_score, vix_score, pe_score):
    composite = erp_score * 0.4 + vix_score * 0.3 + (1 if pe_score < 40 else -1) * 0.3
    if composite >= 1: return 'AGGRESSIVE BUY', composite, 'signal-buy'
    if composite >= 0.5: return 'BUY', composite, 'signal-buy'
    if composite >= -0.5: return 'HOLD', composite, 'signal-hold'
    if composite >= -1: return 'TRIM', composite, 'signal-trim'
    return 'SELL', composite, 'signal-sell'

# ══════════════════════════════════════════════════════════════════════════════
# CHARTING
# ══════════════════════════════════════════════════════════════════════════════

def create_gauge(val, title, min_v, max_v, steps, colors):
    return go.Figure(go.Indicator(
        mode="gauge+number", value=val, title={'text': title, 'font': {'color': 'white'}},
        gauge={'axis': {'range': [min_v, max_v]}, 'bar': {'color': '#3b82f6'},
               'steps': [{'range': [steps[i], steps[i+1]], 'color': colors[i]} for i in range(len(steps)-1)]},
        number={'font': {'color': 'white'}}
    )).update_layout(height=250, margin=dict(t=30,b=10,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown('<h1 class="main-title">PRO QUANT DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Data Source: Local Files (Priority) > GitHub (Fallback)</p>', unsafe_allow_html=True)
    
    # LOAD
    with st.spinner('🔄 Loading market data...'):
        raw_data = load_market_data()
        daily, monthly, sector_data = create_dashboard_data(raw_data)
    
    if monthly is None or len(monthly) == 0:
        st.error("⚠️ DATA NOT FOUND. Please ensure .csv files are in the same folder as this script.")
        return

    # LATEST
    latest = monthly.iloc[-1]
    
    # SIGNALS
    erp_txt, erp_sc, erp_col = get_erp_signal(latest.get('ERP', 0))
    vix_txt, vix_sc, vix_col = get_vix_signal(latest.get('VIX', 15))
    pe_pct = latest.get('Nifty50_PE_Pct', 50)
    sig_txt, sig_sc, sig_cls = get_composite_signal(erp_sc, vix_sc, pe_pct)
    
    # METRICS ROW
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><div class="metric-label">Nifty PE</div><div class="metric-value">{latest["Nifty50_PE"]:.2f}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div class="metric-label">ERP %</div><div class="metric-value" style="color:{erp_col}">{latest["ERP"]:.2f}%</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><div class="metric-label">VIX</div><div class="metric-value" style="color:{vix_col}">{latest["VIX"]:.2f}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><div class="metric-label">ACTION</div><div class="signal-badge {sig_cls}">{sig_txt}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # CHARTS TAB
    t1, t2, t3 = st.tabs(["💰 PE Valuation", "📊 ERP Analysis", "😱 Sentiment (VIX)"])
    
    with t1:
        st.plotly_chart(go.Figure().add_trace(go.Scatter(x=monthly['Date'], y=monthly['Nifty50_PE'], name='Nifty PE')).update_layout(title="Nifty 50 PE Ratio History", height=400), use_container_width=True)
    
    with t2:
        st.plotly_chart(go.Figure().add_trace(go.Scatter(x=monthly['Date'], y=monthly['ERP'], name='ERP', fill='tozeroy')).add_hline(y=1.5, line_dash='dash', annotation_text='Buy Zone').update_layout(title="Equity Risk Premium (Yield Spread)", height=400), use_container_width=True)
        
    with t3:
        st.plotly_chart(go.Figure().add_trace(go.Scatter(x=monthly['Date'], y=monthly['VIX'], name='VIX', line=dict(color='#8b5cf6'))).update_layout(title="India VIX History", height=400), use_container_width=True)

if __name__ == "__main__":
    main()
