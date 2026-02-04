"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 PRO QUANT MARKET TIMING DASHBOARD                      ║
║                                                                              ║
║  A comprehensive market analysis system for Indian equity markets            ║
║  Features: ERP Analysis | VIX Signals | Multi-Cap Valuation | Sector Rotation║
║                                                                              ║
║  USAGE:  streamlit run pro_quant_dashboard.py                                ║
║  REQUIREMENTS: pip install streamlit pandas numpy plotly                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
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
# CUSTOM CSS - DARK FUTURISTIC THEME
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ═══ ROOT VARIABLES ═══ */
:root {
    --bg-dark: #0a0f1a;
    --bg-card: #111827;
    --bg-card-hover: #1f2937;
    --border: #1e3a5f;
    --text-primary: #e2e8f0;
    --text-secondary: #64748b;
    --green: #10b981;
    --green-glow: rgba(16, 185, 129, 0.5);
    --red: #ef4444;
    --red-glow: rgba(239, 68, 68, 0.5);
    --yellow: #f59e0b;
    --blue: #3b82f6;
    --purple: #8b5cf6;
    --cyan: #06b6d4;
}

/* ═══ GLOBAL STYLES ═══ */
.stApp {
    background: linear-gradient(180deg, #0a0f1a 0%, #111827 50%, #0a0f1a 100%);
}

#MainMenu, footer, header {visibility: hidden;}

/* ═══ HEADER STYLES ═══ */
.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.8rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #10b981, #06b6d4, #3b82f6, #8b5cf6);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient-shift 5s ease infinite;
    padding: 1rem 0 0.5rem 0;
    letter-spacing: 4px;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    color: #64748b;
    text-align: center;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* ═══ METRIC CARDS ═══ */
.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #10b981, #06b6d4, #3b82f6);
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: #3b82f6;
    box-shadow: 0 20px 40px rgba(59, 130, 246, 0.15);
}

.metric-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.75rem;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.5rem;
}

.metric-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    display: inline-block;
}

.delta-positive { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.delta-negative { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.delta-neutral { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }

/* ═══ SIGNAL BADGES ═══ */
.signal-container {
    text-align: center;
    padding: 1rem;
}

.signal-badge {
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    font-weight: 700;
    padding: 1rem 2rem;
    border-radius: 12px;
    display: inline-block;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.signal-buy {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    color: white;
    box-shadow: 0 0 30px rgba(16, 185, 129, 0.5);
    animation: pulse-buy 2s ease-in-out infinite;
}

.signal-sell {
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
    color: white;
    box-shadow: 0 0 30px rgba(239, 68, 68, 0.5);
    animation: pulse-sell 2s ease-in-out infinite;
}

.signal-hold {
    background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
    color: white;
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.4);
}

.signal-trim {
    background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
    color: white;
    box-shadow: 0 0 20px rgba(249, 115, 22, 0.4);
}

@keyframes pulse-buy {
    0%, 100% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
    50% { box-shadow: 0 0 40px rgba(16, 185, 129, 0.8); }
}

@keyframes pulse-sell {
    0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }
    50% { box-shadow: 0 0 40px rgba(239, 68, 68, 0.8); }
}

/* ═══ REGIME BANNER ═══ */
.regime-banner {
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    padding: 1.5rem;
    border-radius: 16px;
    text-align: center;
    letter-spacing: 3px;
    margin: 1rem 0;
}

.regime-bull {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
    border: 2px solid #10b981;
    color: #10b981;
    box-shadow: inset 0 0 30px rgba(16, 185, 129, 0.2);
}

.regime-bear {
    background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%);
    border: 2px solid #ef4444;
    color: #ef4444;
    box-shadow: inset 0 0 30px rgba(239, 68, 68, 0.2);
}

.regime-neutral {
    background: linear-gradient(135deg, #451a03 0%, #78350f 100%);
    border: 2px solid #f59e0b;
    color: #f59e0b;
    box-shadow: inset 0 0 30px rgba(245, 158, 11, 0.2);
}

/* ═══ INFO BOXES ═══ */
.info-box {
    border-radius: 12px;
    padding: 1.25rem;
    margin: 1rem 0;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
}

.info-success {
    background: linear-gradient(135deg, #064e3b 0%, #111827 100%);
    border-left: 4px solid #10b981;
    color: #e2e8f0;
}

.info-warning {
    background: linear-gradient(135deg, #451a03 0%, #111827 100%);
    border-left: 4px solid #f59e0b;
    color: #e2e8f0;
}

.info-danger {
    background: linear-gradient(135deg, #450a0a 0%, #111827 100%);
    border-left: 4px solid #ef4444;
    color: #e2e8f0;
}

/* ═══ SECTION HEADERS ═══ */
.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 600;
    color: #e2e8f0;
    padding: 0.75rem 1.25rem;
    margin: 2rem 0 1rem 0;
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.2), transparent);
    border-left: 4px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    letter-spacing: 2px;
}

/* ═══ DIVIDERS ═══ */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #3b82f6, transparent);
    margin: 2rem 0;
}

/* ═══ SIDEBAR ═══ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0a0f1a 100%);
    border-right: 1px solid #1e3a5f;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ═══ TABS ═══ */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #111827;
    padding: 8px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    color: #64748b;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1e3a5f 0%, #1f2937 100%);
    color: #3b82f6 !important;
}

/* ═══ SCROLLBAR ═══ */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #111827; }
::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #60a5fa; }

/* ═══ TABLE STYLES ═══ */
.dataframe { font-family: 'JetBrains Mono', monospace !important; }

</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING & PROCESSING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def load_market_data():
    """Load all market data from CSV files"""
    
    data = {}
    
    # File configurations
    file_configs = {
        'vix': {'file': 'India_VIX_Yahoo.csv', 'date_col': 'Date'},
        'nifty50': {'file': 'Nifty50_Historical_Yahoo.csv', 'date_col': 'Date'},
        'midcap': {'file': 'NIFTY_MIDCAP_100_Historical_Yahoo.csv', 'date_col': 'Date'},
        'pe_data': {'file': 'Nifty_Index_Valuation_History.csv', 'date_col': 'Date'},
        'gsec': {'file': 'Nifty_10Y_Benchmark_GSec_Merged.csv', 'date_col': 'Date'},
    }
    
    for key, config in file_configs.items():
        try:
            df = pd.read_csv(config['file'])
            df[config['date_col']] = pd.to_datetime(df[config['date_col']])
            data[key] = df
        except FileNotFoundError:
            data[key] = None
        except Exception as e:
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
        gsec['GSec_Yield'] = 17 - (gsec['Close'] / 100)
        gsec = gsec[['Date', 'GSec_Yield']]
        daily = pd.merge(daily, gsec, on='Date', how='left')
    else:
        daily['GSec_Yield'] = 7.5
    
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
# SIGNAL CALCULATIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_erp_signal(erp):
    """Calculate ERP signal"""
    if pd.isna(erp):
        return 'NO DATA', 0, '#64748b'
    if erp > 3:
        return 'VERY CHEAP', 2, '#10b981'
    if erp > 1.5:
        return 'CHEAP', 1, '#34d399'
    if erp > 0:
        return 'FAIR', 0, '#f59e0b'
    if erp > -1.5:
        return 'EXPENSIVE', -1, '#f97316'
    return 'VERY EXPENSIVE', -2, '#ef4444'


def get_vix_signal(vix):
    """Calculate VIX signal"""
    if pd.isna(vix):
        return 'NO DATA', 0, '#64748b'
    if vix > 30:
        return 'EXTREME FEAR', 2, '#10b981'
    if vix > 25:
        return 'HIGH FEAR', 1.5, '#34d399'
    if vix > 20:
        return 'FEAR', 1, '#84cc16'
    if vix > 15:
        return 'ELEVATED', 0.5, '#f59e0b'
    if vix > 12:
        return 'NORMAL', 0, '#64748b'
    return 'COMPLACENCY', -1, '#ef4444'


def get_pe_signal(pe_pct):
    """Calculate PE percentile signal"""
    if pd.isna(pe_pct):
        return 'NO DATA', 0
    if pe_pct < 20:
        return 'VERY CHEAP', 2
    if pe_pct < 40:
        return 'CHEAP', 1
    if pe_pct < 60:
        return 'FAIR', 0
    if pe_pct < 80:
        return 'EXPENSIVE', -1
    return 'VERY EXPENSIVE', -2


def get_composite_signal(erp_score, vix_score, pe_score):
    """Calculate composite signal"""
    composite = erp_score * 0.35 + vix_score * 0.35 + pe_score * 0.30
    
    if composite >= 1.5:
        return 'AGGRESSIVE BUY', composite, 'signal-buy'
    if composite >= 0.75:
        return 'BUY', composite, 'signal-buy'
    if composite >= 0.25:
        return 'ACCUMULATE', composite, 'signal-hold'
    if composite >= -0.25:
        return 'HOLD', composite, 'signal-hold'
    if composite >= -0.75:
        return 'TRIM', composite, 'signal-trim'
    if composite >= -1.25:
        return 'REDUCE', composite, 'signal-sell'
    return 'SELL', composite, 'signal-sell'


def get_market_regime(vix, erp_score, drawdown):
    """Determine market regime"""
    vix = vix if not pd.isna(vix) else 15
    drawdown = drawdown if not pd.isna(drawdown) else 0
    
    if erp_score >= 1 and vix > 25 and drawdown < -15:
        return '🎯 IDEAL BOTTOM', 'regime-bull'
    if vix > 30 and drawdown < -20:
        return '📉 CRASH MODE', 'regime-bear'
    if vix < 15 and drawdown > -5:
        return '🚀 BULL RUN', 'regime-bull'
    if vix < 12 and erp_score <= -1:
        return '⚠️ MARKET TOP', 'regime-bear'
    if -20 < drawdown < -10:
        return '📈 RECOVERY', 'regime-neutral'
    return '↔️ TRANSITIONAL', 'regime-neutral'


# ══════════════════════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def create_gauge_chart(value, title, min_val, max_val, thresholds, colors):
    """Create a gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 14, 'color': '#e2e8f0', 'family': 'Rajdhani'}},
        number={'font': {'size': 32, 'color': '#e2e8f0', 'family': 'Orbitron'}, 'suffix': ''},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickcolor': '#64748b',
                    'tickfont': {'color': '#64748b', 'size': 10, 'family': 'JetBrains Mono'}},
            'bar': {'color': '#3b82f6', 'thickness': 0.3},
            'bgcolor': '#1f2937',
            'borderwidth': 2,
            'bordercolor': '#1e3a5f',
            'steps': [{'range': [thresholds[i], thresholds[i+1]], 'color': colors[i]}
                     for i in range(len(thresholds)-1)],
            'threshold': {'line': {'color': '#ffffff', 'width': 3}, 'thickness': 0.8, 'value': value}
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e2e8f0'},
        height=220,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def create_time_series_chart(df, x_col, y_cols, title, colors=None, show_legend=True):
    """Create time series line chart"""
    fig = go.Figure()
    
    default_colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    colors = colors or default_colors
    
    for i, col in enumerate(y_cols):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                name=col.replace('_', ' '),
                line=dict(color=colors[i % len(colors)], width=2.5),
                mode='lines'
            ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#e2e8f0', family='Orbitron'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0', family='Rajdhani'),
        xaxis=dict(gridcolor='#1e3a5f', zerolinecolor='#1e3a5f', tickfont=dict(size=11)),
        yaxis=dict(gridcolor='#1e3a5f', zerolinecolor='#1e3a5f', tickfont=dict(size=11)),
        legend=dict(
            bgcolor='rgba(17,24,39,0.9)',
            bordercolor='#1e3a5f',
            font=dict(color='#e2e8f0', size=11),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        showlegend=show_legend,
        hovermode='x unified',
        height=420,
        margin=dict(l=60, r=30, t=80, b=50)
    )
    return fig


def create_vix_chart(df):
    """Create VIX chart with fear zones"""
    fig = go.Figure()
    
    # Fear zones
    fig.add_hrect(y0=0, y1=12, fillcolor="rgba(239,68,68,0.1)", line_width=0,
                 annotation_text="Complacency", annotation_position="top left")
    fig.add_hrect(y0=12, y1=20, fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hrect(y0=20, y1=50, fillcolor="rgba(16,185,129,0.1)", line_width=0,
                 annotation_text="Fear Zone", annotation_position="top left")
    
    # VIX line
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['VIX'],
        name='India VIX',
        line=dict(color='#8b5cf6', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(139,92,246,0.2)'
    ))
    
    # Threshold lines
    fig.add_hline(y=12, line_dash="dash", line_color="#ef4444", line_width=1)
    fig.add_hline(y=20, line_dash="dash", line_color="#f59e0b", line_width=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981", line_width=1)
    
    fig.update_layout(
        title=dict(text='📊 India VIX - Fear & Greed Indicator', 
                  font=dict(size=18, color='#e2e8f0', family='Orbitron'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0', family='Rajdhani'),
        xaxis=dict(gridcolor='#1e3a5f'),
        yaxis=dict(gridcolor='#1e3a5f', title='VIX Level'),
        showlegend=False,
        height=420,
        margin=dict(l=60, r=30, t=80, b=50)
    )
    return fig


def create_erp_chart(df):
    """Create ERP chart with zones"""
    fig = go.Figure()
    
    # Zones
    fig.add_hrect(y0=-10, y1=0, fillcolor="rgba(239,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=0, y1=10, fillcolor="rgba(16,185,129,0.1)", line_width=0)
    
    # ERP line
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['ERP'],
        name='ERP',
        line=dict(color='#06b6d4', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(6,182,212,0.2)'
    ))
    
    # Threshold lines
    fig.add_hline(y=0, line_color="#ffffff", line_width=2)
    fig.add_hline(y=1.5, line_dash="dash", line_color="#10b981", line_width=1,
                 annotation_text="Cheap", annotation_position="right")
    fig.add_hline(y=-1.5, line_dash="dash", line_color="#ef4444", line_width=1,
                 annotation_text="Expensive", annotation_position="right")
    
    fig.update_layout(
        title=dict(text='📈 Equity Risk Premium (Earnings Yield - G-Sec Yield)', 
                  font=dict(size=18, color='#e2e8f0', family='Orbitron'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0', family='Rajdhani'),
        xaxis=dict(gridcolor='#1e3a5f'),
        yaxis=dict(gridcolor='#1e3a5f', title='ERP %'),
        showlegend=False,
        height=420,
        margin=dict(l=60, r=30, t=80, b=50)
    )
    return fig


def create_multicap_chart(latest):
    """Create multi-cap comparison bar chart"""
    caps = ['Large Cap', 'Mid Cap', 'Small Cap']
    percentiles = [
        latest.get('Nifty50_PE_Pct', 50),
        latest.get('Midcap_PE_Pct', 50),
        latest.get('Smallcap_PE_Pct', 50)
    ]
    pes = [
        latest.get('Nifty50_PE', 22),
        latest.get('Midcap_PE', 28),
        latest.get('Smallcap_PE', 25)
    ]
    
    colors = ['#10b981' if p < 40 else '#ef4444' if p > 60 else '#f59e0b' for p in percentiles]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=caps,
        y=percentiles,
        marker_color=colors,
        text=[f'{p:.0f}%<br>PE: {pe:.1f}' for p, pe in zip(percentiles, pes)],
        textposition='outside',
        textfont=dict(color='#e2e8f0', size=12, family='JetBrains Mono')
    ))
    
    # Add reference lines
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981", line_width=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", line_width=1)
    
    fig.update_layout(
        title=dict(text='🏛️ Multi-Cap PE Percentile Comparison', 
                  font=dict(size=18, color='#e2e8f0', family='Orbitron'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0', family='Rajdhani'),
        xaxis=dict(gridcolor='#1e3a5f'),
        yaxis=dict(gridcolor='#1e3a5f', title='Percentile', range=[0, 100]),
        showlegend=False,
        height=420,
        margin=dict(l=60, r=30, t=80, b=50)
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ═══ HEADER ═══
    st.markdown('<h1 class="main-title">PRO QUANT DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Real-Time Market Timing & Valuation Intelligence</p>', unsafe_allow_html=True)
    
    # ═══ LOAD DATA ═══
    with st.spinner('🔄 Loading market data...'):
        raw_data = load_market_data()
        daily, monthly, sector_data = create_dashboard_data(raw_data)
    
    # Check data availability
    if monthly is None or len(monthly) == 0:
        st.error("⚠️ Could not load market data. Please ensure CSV files are in the correct location.")
        st.info("""
        **Required Files:**
        - `Nifty50_Historical_Yahoo.csv`
        - `India_VIX_Yahoo.csv`
        - `Nifty_Index_Valuation_History.csv`
        - `Nifty_10Y_Benchmark_GSec_Merged.csv`
        """)
        
        # Use sample data for demo
        st.warning("📊 Showing demo with sample data...")
        np.random.seed(42)
        dates = pd.date_range('2018-01-01', '2026-01-31', freq='M')
        monthly = pd.DataFrame({
            'Date': dates,
            'Nifty50': np.cumsum(np.random.randn(len(dates)) * 500) + 10000 + np.arange(len(dates)) * 100,
            'Nifty50_PE': np.random.uniform(18, 32, len(dates)),
            'Midcap_PE': np.random.uniform(22, 40, len(dates)),
            'Smallcap_PE': np.random.uniform(20, 38, len(dates)),
            'VIX': np.random.uniform(10, 30, len(dates)),
            'GSec_Yield': np.random.uniform(6.5, 8.5, len(dates)),
            'Drawdown': np.random.uniform(-15, 0, len(dates)),
            'RSI': np.random.uniform(30, 70, len(dates))
        })
        monthly['Earnings_Yield'] = (1 / monthly['Nifty50_PE']) * 100
        monthly['ERP'] = monthly['Earnings_Yield'] - monthly['GSec_Yield']
        monthly['Nifty50_PE_Pct'] = monthly['Nifty50_PE'].rank(pct=True) * 100
        monthly['Midcap_PE_Pct'] = monthly['Midcap_PE'].rank(pct=True) * 100
        monthly['Smallcap_PE_Pct'] = monthly['Smallcap_PE'].rank(pct=True) * 100
    
    # Get latest data with valid PE
    monthly_valid = monthly.dropna(subset=['Nifty50_PE']) if 'Nifty50_PE' in monthly.columns else monthly
    if len(monthly_valid) == 0:
        monthly_valid = monthly
    latest = monthly_valid.iloc[-1]
    
    # ═══ CALCULATE SIGNALS ═══
    erp_text, erp_score, erp_color = get_erp_signal(latest.get('ERP', 0))
    vix_text, vix_score, vix_color = get_vix_signal(latest.get('VIX', 15))
    pe_text, pe_score = get_pe_signal(latest.get('Nifty50_PE_Pct', 50))
    signal_text, signal_score, signal_class = get_composite_signal(erp_score, vix_score, pe_score)
    regime_text, regime_class = get_market_regime(latest.get('VIX', 15), erp_score, latest.get('Drawdown', 0))
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════════════════════════
    
    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Controls")
        st.markdown("---")
        
        # Quick Metrics
        st.markdown("### 📊 Quick Stats")
        
        nifty_val = latest.get('Nifty50', 0)
        drawdown = latest.get('Drawdown', 0)
        st.metric("Nifty 50", f"{nifty_val:,.0f}", f"{drawdown:.1f}% from ATH",
                 delta_color="inverse" if drawdown < -5 else "normal")
        
        vix_val = latest.get('VIX', 0)
        st.metric("India VIX", f"{vix_val:.2f}", vix_text,
                 delta_color="inverse" if vix_score < 0 else "normal")
        
        gsec_val = latest.get('GSec_Yield', 0)
        st.metric("10Y G-Sec Yield", f"{gsec_val:.2f}%")
        
        st.markdown("---")
        
        # Signal Legend
        st.markdown("### 📋 Signal Guide")
        st.markdown("""
        | Signal | Meaning |
        |:------:|:--------|
        | 🟢 | Buy/Accumulate |
        | 🟡 | Hold/Wait |
        | 🟠 | Trim/Caution |
        | 🔴 | Sell/Reduce |
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ Data Info")
        st.caption(f"**Last Updated:** {latest['Date'].strftime('%Y-%m-%d')}")
        st.caption(f"**Data Points:** {len(monthly_valid)} months")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN CONTENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ═══ ROW 1: KEY METRICS ═══
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pe_val = latest.get('Nifty50_PE', 0)
        pe_pct = latest.get('Nifty50_PE_Pct', 50)
        delta_class = 'delta-positive' if pe_pct < 40 else 'delta-negative' if pe_pct > 60 else 'delta-neutral'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Nifty 50 PE Ratio</div>
            <div class="metric-value">{pe_val:.2f}</div>
            <div class="metric-delta {delta_class}">{pe_pct:.0f}th Percentile</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        erp_val = latest.get('ERP', 0)
        delta_class = 'delta-positive' if erp_score > 0 else 'delta-negative'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Equity Risk Premium</div>
            <div class="metric-value" style="color:{erp_color}">{erp_val:.2f}%</div>
            <div class="metric-delta {delta_class}">{erp_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        vix_val = latest.get('VIX', 0)
        delta_class = 'delta-positive' if vix_score > 0 else 'delta-negative' if vix_score < 0 else 'delta-neutral'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">India VIX</div>
            <div class="metric-value" style="color:{vix_color}">{vix_val:.2f}</div>
            <div class="metric-delta {delta_class}">{vix_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Final Signal</div>
            <div class="signal-container">
                <div class="signal-badge {signal_class}">{signal_text}</div>
            </div>
            <div class="metric-delta delta-neutral">Score: {signal_score:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ═══ ROW 2: REGIME & GAUGES ═══
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f'<div class="regime-banner {regime_class}">{regime_text}</div>', unsafe_allow_html=True)
        
        # Recommendation Box
        if signal_score >= 0.5:
            st.markdown("""
            <div class="info-box info-success">
                <strong>💡 Recommendation:</strong><br>
                Favorable conditions for equity accumulation. Consider increasing SIP amounts 
                and deploying cash reserves on market dips.
            </div>
            """, unsafe_allow_html=True)
        elif signal_score <= -0.5:
            st.markdown("""
            <div class="info-box info-danger">
                <strong>⚠️ Warning:</strong><br>
                Elevated valuations and/or complacent sentiment suggest caution. 
                Consider profit booking and maintaining defensive positions.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box info-warning">
                <strong>📊 Observation:</strong><br>
                Mixed signals suggest maintaining current allocations. 
                Wait for clearer directional cues before making major portfolio changes.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        g1, g2, g3 = st.columns(3)
        
        with g1:
            fig = create_gauge_chart(
                latest.get('Nifty50_PE', 22), "PE RATIO", 15, 40,
                [15, 20, 25, 30, 35, 40],
                ['#059669', '#10b981', '#f59e0b', '#f97316', '#ef4444']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with g2:
            fig = create_gauge_chart(
                latest.get('VIX', 15), "VIX LEVEL", 8, 40,
                [8, 12, 18, 25, 32, 40],
                ['#ef4444', '#f97316', '#f59e0b', '#10b981', '#059669']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with g3:
            fig = create_gauge_chart(
                latest.get('ERP', -2), "ERP %", -6, 4,
                [-6, -3, 0, 1.5, 3, 4],
                ['#ef4444', '#f97316', '#f59e0b', '#10b981', '#059669']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ═══ ROW 3: CHARTS ═══
    st.markdown('<div class="section-header">📈 Historical Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Valuations", "😱 VIX Sentiment", "📊 ERP Analysis", "🏛️ Multi-Cap"])
    
    with tab1:
        fig = create_time_series_chart(
            monthly_valid, 'Date',
            ['Nifty50_PE', 'Midcap_PE', 'Smallcap_PE'],
            '📊 PE Ratio Trends Across Market Caps',
            ['#3b82f6', '#10b981', '#f59e0b']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = create_vix_chart(monthly_valid)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = create_erp_chart(monthly_valid)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = create_multicap_chart(latest)
        st.plotly_chart(fig, use_container_width=True)
    
    # ═══ ROW 4: SIGNAL HISTORY ═══
    st.markdown('<div class="section-header">📋 Recent Signal History</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Prepare display data
        display_df = monthly_valid.tail(12).copy()
        display_df['Month'] = display_df['Date'].dt.strftime('%Y-%m')
        display_df['ERP_Signal'] = display_df['ERP'].apply(lambda x: get_erp_signal(x)[0])
        display_df['VIX_Signal'] = display_df['VIX'].apply(lambda x: get_vix_signal(x)[0])
        
        display_cols = ['Month', 'Nifty50', 'Nifty50_PE', 'VIX', 'ERP', 'ERP_Signal', 'VIX_Signal']
        display_df = display_df[[c for c in display_cols if c in display_df.columns]]
        
        # Round numeric columns
        for col in ['Nifty50', 'Nifty50_PE', 'VIX', 'ERP']:
            if col in display_df.columns:
                display_df[col] = display_df[col].round(2)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
    
    with col2:
        # Signal distribution pie chart
        st.markdown("#### 📊 Signal Distribution")
        
        if 'ERP_Signal' in display_df.columns:
            signal_counts = monthly_valid['ERP'].apply(lambda x: get_erp_signal(x)[0]).value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=signal_counts.index,
                values=signal_counts.values,
                hole=0.5,
                marker_colors=['#10b981', '#34d399', '#f59e0b', '#f97316', '#ef4444']
            )])
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0', family='Rajdhani'),
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=-0.2,
                    xanchor='center',
                    x=0.5,
                    font=dict(size=10)
                ),
                height=300,
                margin=dict(l=20, r=20, t=20, b=60)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ═══ FOOTER ═══
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: #64748b; font-family: 'Rajdhani', sans-serif;">
        <p style="font-size: 1rem;">🚀 <strong>Pro Quant Market Dashboard</strong> | Built with Streamlit & Plotly</p>
        <p style="font-size: 0.85rem;">Data Sources: NSE India, Yahoo Finance | Signals are for educational purposes only</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">© 2026 Pro Quant Analytics</p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RUN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
