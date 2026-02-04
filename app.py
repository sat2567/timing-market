"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🇮🇳 PRO QUANT INDIA MARKET TIMING DASHBOARD 🇮🇳                      ║
║                                                                              ║
║  India-Calibrated Valuation & Sentiment Analysis System                      ║
║  Features: Recalibrated ERP | PE/PB/Div Analysis | VIX Signals              ║
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
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Pro Quant India Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get script directory
try:
    SCRIPT_DIR = Path(__file__).parent.resolve()
except:
    SCRIPT_DIR = Path.cwd()

# ══════════════════════════════════════════════════════════════════════════════
# INDIA MARKET CONSTANTS - CALIBRATED THRESHOLDS
# ══════════════════════════════════════════════════════════════════════════════

"""
KEY INSIGHT: Indian ERP is STRUCTURALLY NEGATIVE

In India:
- G-Sec yields are HIGH (6-8%) due to inflation, fiscal deficit
- PE ratios are moderate (18-28) giving Earnings Yield of 3.5-5.5%
- Therefore: ERP = 4.5% - 7.5% = -3% (typically)

This is DIFFERENT from US/Developed markets where ERP is positive.

Historical Indian ERP (2016-2026):
- Mean: -3.73%
- Median: -3.74%
- Range: -5.19% (expensive) to -1.61% (cheap)
"""

# India-Calibrated ERP Thresholds (based on percentile analysis)
INDIA_ERP_THRESHOLDS = {
    'very_cheap': -2.5,    # Top 5% historically (rare buying opportunity)
    'cheap': -3.2,         # Top 25% 
    'fair': -3.7,          # Median
    'expensive': -4.2,     # Bottom 25%
    'very_expensive': -4.5 # Bottom 10%
}

# India PE Thresholds (Nifty 50 historical: Mean 24.8, Range 17-42)
INDIA_PE_THRESHOLDS = {
    'undervalued': 20,
    'cheap': 22,
    'fair': 25,
    'expensive': 28,
    'overvalued': 32
}

# VIX Thresholds (Same globally)
VIX_THRESHOLDS = {
    'extreme_fear': 30,
    'high_fear': 25,
    'fear': 20,
    'elevated': 15,
    'normal': 12,
    'complacent': 10
}

# ══════════════════════════════════════════════════════════════════════════════
# CSS STYLES - SAFFRON, WHITE, GREEN THEME (Indian Flag Colors)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-dark: #0a0f1a;
    --bg-card: #111827;
    --border: #1e3a5f;
    --text-primary: #e2e8f0;
    --text-secondary: #64748b;
    --saffron: #ff9933;
    --green-india: #138808;
    --blue-chakra: #000080;
    --green: #10b981;
    --red: #ef4444;
    --yellow: #f59e0b;
    --blue: #3b82f6;
}

.stApp { background: linear-gradient(180deg, #0a0f1a 0%, #111827 100%); }
#MainMenu, footer, header {visibility: hidden;}

.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #ff9933, #ffffff, #138808);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 0.75rem 0;
    letter-spacing: 2px;
}

.subtitle {
    font-family: 'Rajdhani', sans-serif;
    color: #64748b;
    text-align: center;
    letter-spacing: 3px;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.metric-card {
    background: linear-gradient(135deg, #111827, #1f2937);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 20px rgba(59,130,246,0.2);
}

.metric-card::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #ff9933, #ffffff, #138808);
    margin: -1.25rem -1.25rem 1rem -1.25rem;
    border-radius: 16px 16px 0 0;
}

.metric-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0.4rem 0;
}

.metric-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    padding: 0.2rem 0.6rem;
    border-radius: 15px;
    display: inline-block;
}

.delta-positive { background: rgba(16,185,129,0.2); color: #10b981; }
.delta-negative { background: rgba(239,68,68,0.2); color: #ef4444; }
.delta-neutral { background: rgba(245,158,11,0.2); color: #f59e0b; }

.signal-badge {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    font-weight: 700;
    padding: 0.6rem 1.2rem;
    border-radius: 10px;
    display: inline-block;
    letter-spacing: 1px;
}

.signal-buy { background: linear-gradient(135deg, #059669, #10b981); color: white; box-shadow: 0 0 20px rgba(16,185,129,0.5); }
.signal-sell { background: linear-gradient(135deg, #dc2626, #ef4444); color: white; box-shadow: 0 0 20px rgba(239,68,68,0.5); }
.signal-hold { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }
.signal-trim { background: linear-gradient(135deg, #ea580c, #f97316); color: white; }
.signal-accumulate { background: linear-gradient(135deg, #0891b2, #06b6d4); color: white; }

.regime-banner {
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    font-weight: 700;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    letter-spacing: 2px;
    margin: 0.75rem 0;
}

.regime-bull { background: linear-gradient(135deg, #064e3b, #065f46); border: 2px solid #10b981; color: #10b981; }
.regime-bear { background: linear-gradient(135deg, #450a0a, #7f1d1d); border: 2px solid #ef4444; color: #ef4444; }
.regime-neutral { background: linear-gradient(135deg, #451a03, #78350f); border: 2px solid #f59e0b; color: #f59e0b; }

.info-box { border-radius: 10px; padding: 1rem; margin: 0.5rem 0; font-family: 'Rajdhani', sans-serif; font-size: 0.95rem; }
.info-success { background: linear-gradient(135deg, #064e3b, #111827); border-left: 4px solid #10b981; color: #e2e8f0; }
.info-warning { background: linear-gradient(135deg, #451a03, #111827); border-left: 4px solid #f59e0b; color: #e2e8f0; }
.info-danger { background: linear-gradient(135deg, #450a0a, #111827); border-left: 4px solid #ef4444; color: #e2e8f0; }
.info-primary { background: linear-gradient(135deg, #1e3a5f, #111827); border-left: 4px solid #3b82f6; color: #e2e8f0; }

.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    color: #e2e8f0;
    padding: 0.6rem 1rem;
    margin: 1.25rem 0 0.75rem 0;
    background: linear-gradient(90deg, rgba(59,130,246,0.2), transparent);
    border-left: 4px solid #3b82f6;
    border-radius: 0 8px 8px 0;
}

.divider { height: 1px; background: linear-gradient(90deg, transparent, #ff9933, #138808, transparent); margin: 1.25rem 0; }

.calibration-note {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    color: #64748b;
    background: rgba(30, 58, 95, 0.3);
    padding: 0.75rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 3px solid #ff9933;
}

[data-testid="stSidebar"] { background: linear-gradient(180deg, #111827, #0a0f1a); }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.stTabs [data-baseweb="tab-list"] { background: #111827; padding: 6px; border-radius: 10px; }
.stTabs [data-baseweb="tab"] { font-family: 'Rajdhani', sans-serif; font-weight: 600; color: #64748b; }
.stTabs [aria-selected="true"] { background: #1e3a5f; color: #3b82f6 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

def find_file(names):
    """Search for file in multiple locations"""
    locations = [SCRIPT_DIR, Path.cwd(), SCRIPT_DIR/"data", Path.cwd()/"data"]
    for loc in locations:
        if loc.exists():
            for name in names:
                path = loc / name
                if path.exists():
                    return path
    return None

@st.cache_data(ttl=3600)
def load_data():
    """Load all market data"""
    data, status = {}, {}
    
    configs = {
        'nifty50_pe': ['Nifty50_PE_PB_Div_Merged.csv', 'nifty50_pe_pb_div_merged.csv'],
        'midcap_pe': ['NiftyMidcap100_PE_PB_Div_Merged.csv', 'niftymidcap100_pe_pb_div_merged.csv'],
        'nifty50': ['Nifty50_Historical_Yahoo.csv', 'nifty50_historical_yahoo.csv'],
        'vix': ['India_VIX_Yahoo.csv', 'india_vix_yahoo.csv'],
        'gsec': ['Nifty_10Y_Benchmark_GSec_Merged.csv'],
    }
    
    for key, names in configs.items():
        path = find_file(names)
        if path:
            try:
                df = pd.read_csv(path)
                df['Date'] = pd.to_datetime(df['Date'])
                data[key] = df
                status[key] = f"✅ {path.name}"
            except Exception as e:
                status[key] = f"❌ {str(e)[:30]}"
        else:
            status[key] = "⚠️ Not found"
    
    return data, status

def process_data(raw):
    """Process raw data into dashboard format"""
    
    # Check for PE data (primary source)
    if raw.get('nifty50_pe') is None:
        return None
    
    # Start with PE data
    df = raw['nifty50_pe'].copy()
    df = df.rename(columns={'PE': 'Nifty50_PE', 'PB': 'Nifty50_PB', 'DivYield': 'Nifty50_DivYield'})
    
    # Merge Nifty prices
    if raw.get('nifty50') is not None:
        prices = raw['nifty50'][['Date', 'Close']].copy()
        prices.columns = ['Date', 'Nifty50']
        df = pd.merge(df, prices, on='Date', how='left')
    
    # Merge VIX
    if raw.get('vix') is not None:
        vix = raw['vix'].copy()
        col = 'VIX_Close' if 'VIX_Close' in vix.columns else 'Close'
        if col in vix.columns:
            vix_df = vix[['Date', col]].copy()
            vix_df.columns = ['Date', 'VIX']
            df = pd.merge(df, vix_df, on='Date', how='left')
    if 'VIX' not in df.columns:
        df['VIX'] = 15.0
    
    # Merge G-Sec
    if raw.get('gsec') is not None:
        gsec = raw['gsec'][['Date', 'Close']].copy()
        gsec['GSec_Yield'] = 17 - (gsec['Close'] / 100)
        df = pd.merge(df, gsec[['Date', 'GSec_Yield']], on='Date', how='left')
    if 'GSec_Yield' not in df.columns:
        df['GSec_Yield'] = 7.5
    
    # Sort and fill
    df = df.sort_values('Date').ffill().bfill()
    
    # Calculate derived metrics
    df['Earnings_Yield'] = (1 / df['Nifty50_PE']) * 100
    df['ERP'] = df['Earnings_Yield'] - df['GSec_Yield']
    df['GSec_Adjusted_PE'] = df['Nifty50_PE'] / df['GSec_Yield']
    
    # Calculate percentiles (expanding window for historical context)
    df['PE_Percentile'] = df['Nifty50_PE'].rank(pct=True) * 100
    df['ERP_Percentile'] = df['ERP'].rank(pct=True) * 100
    df['PB_Percentile'] = df['Nifty50_PB'].rank(pct=True) * 100
    
    # Technical indicators
    if 'Nifty50' in df.columns:
        df['ATH'] = df['Nifty50'].expanding().max()
        df['Drawdown'] = ((df['Nifty50'] / df['ATH']) - 1) * 100
        df['SMA_50'] = df['Nifty50'].rolling(50).mean()
        df['SMA_200'] = df['Nifty50'].rolling(200).mean()
    
    # Merge Midcap PE (monthly)
    if raw.get('midcap_pe') is not None:
        mid = raw['midcap_pe'].copy()
        mid = mid.rename(columns={'PE': 'Midcap_PE', 'PB': 'Midcap_PB', 'DivYield': 'Midcap_DivYield'})
        mid['Date'] = pd.to_datetime(mid['Date'])
        # Create month key for merging
        df['YearMonth'] = df['Date'].dt.to_period('M')
        mid['YearMonth'] = mid['Date'].dt.to_period('M')
        mid_monthly = mid[['YearMonth', 'Midcap_PE', 'Midcap_PB', 'Midcap_DivYield']]
        df = pd.merge(df, mid_monthly, on='YearMonth', how='left')
        df = df.drop('YearMonth', axis=1)
    
    return df

# ══════════════════════════════════════════════════════════════════════════════
# INDIA-CALIBRATED SIGNAL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def india_erp_signal(erp):
    """ERP signal calibrated for Indian market (structurally negative ERP)"""
    if pd.isna(erp):
        return 'NO DATA', 0, '#64748b'
    
    # India-specific thresholds (ERP is typically -2% to -5%)
    if erp > -2.5:
        return 'VERY CHEAP', 2, '#10b981'    # Rare! Top 5%
    if erp > -3.2:
        return 'CHEAP', 1, '#34d399'          # Top 25%
    if erp > -3.7:
        return 'FAIR', 0, '#f59e0b'           # Around median
    if erp > -4.2:
        return 'EXPENSIVE', -1, '#f97316'     # Bottom 25%
    return 'VERY EXPENSIVE', -2, '#ef4444'    # Bottom 10%

def india_pe_signal(pe, pe_pct=None):
    """PE signal based on historical percentile"""
    if pd.isna(pe):
        return 'NO DATA', 0, '#64748b'
    
    # If percentile provided, use it
    if pe_pct is not None:
        if pe_pct < 20:
            return 'UNDERVALUED', 2, '#10b981'
        if pe_pct < 40:
            return 'CHEAP', 1, '#34d399'
        if pe_pct < 60:
            return 'FAIR', 0, '#f59e0b'
        if pe_pct < 80:
            return 'EXPENSIVE', -1, '#f97316'
        return 'OVERVALUED', -2, '#ef4444'
    
    # Absolute thresholds (Nifty 50 historical)
    if pe < 20:
        return 'UNDERVALUED', 2, '#10b981'
    if pe < 22:
        return 'CHEAP', 1, '#34d399'
    if pe < 25:
        return 'FAIR', 0, '#f59e0b'
    if pe < 28:
        return 'EXPENSIVE', -1, '#f97316'
    return 'OVERVALUED', -2, '#ef4444'

def india_pb_signal(pb):
    """PB ratio signal"""
    if pd.isna(pb):
        return 'NO DATA', 0, '#64748b'
    
    # Nifty 50 PB historical range: 2.5 - 4.5
    if pb < 2.8:
        return 'CHEAP', 1, '#10b981'
    if pb < 3.3:
        return 'FAIR', 0, '#f59e0b'
    if pb < 3.8:
        return 'EXPENSIVE', -1, '#f97316'
    return 'VERY EXPENSIVE', -2, '#ef4444'

def india_divyield_signal(div):
    """Dividend Yield signal (higher is better)"""
    if pd.isna(div):
        return 'NO DATA', 0, '#64748b'
    
    # Nifty 50 Div Yield historical range: 1.0% - 2.0%
    if div > 1.6:
        return 'HIGH YIELD', 1, '#10b981'
    if div > 1.3:
        return 'AVERAGE', 0, '#f59e0b'
    return 'LOW YIELD', -1, '#ef4444'

def vix_signal(vix):
    """VIX signal (same globally)"""
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

def composite_signal(erp_score, pe_score, vix_score, pb_score=0, div_score=0):
    """
    India-calibrated composite signal
    Weights: ERP 25%, PE 30%, VIX 25%, PB 10%, Div 10%
    """
    composite = (
        erp_score * 0.25 +
        pe_score * 0.30 +
        vix_score * 0.25 +
        pb_score * 0.10 +
        div_score * 0.10
    )
    
    if composite >= 1.2:
        return 'AGGRESSIVE BUY', composite, 'signal-buy'
    if composite >= 0.6:
        return 'BUY', composite, 'signal-buy'
    if composite >= 0.2:
        return 'ACCUMULATE', composite, 'signal-accumulate'
    if composite >= -0.2:
        return 'HOLD', composite, 'signal-hold'
    if composite >= -0.6:
        return 'TRIM', composite, 'signal-trim'
    if composite >= -1.0:
        return 'REDUCE', composite, 'signal-sell'
    return 'SELL', composite, 'signal-sell'

def market_regime(vix, erp_score, pe_score, drawdown=0):
    """Determine market regime"""
    vix = 15 if pd.isna(vix) else vix
    drawdown = 0 if pd.isna(drawdown) else drawdown
    
    # Ideal bottom: Cheap + Panic + Deep correction
    if erp_score >= 1 and pe_score >= 1 and vix > 25 and drawdown < -15:
        return '🎯 IDEAL BOTTOM', 'regime-bull'
    
    # Crash mode
    if vix > 30 and drawdown < -20:
        return '📉 CRASH MODE', 'regime-bear'
    
    # Bull run
    if vix < 15 and drawdown > -5:
        return '🚀 BULL RUN', 'regime-bull'
    
    # Market top warning
    if vix < 12 and erp_score <= -1 and pe_score <= -1:
        return '⚠️ MARKET TOP', 'regime-bear'
    
    # Recovery
    if -20 < drawdown < -10 and erp_score >= 0:
        return '📈 RECOVERY', 'regime-neutral'
    
    # Correction
    if -15 < drawdown < -5:
        return '📊 CORRECTION', 'regime-neutral'
    
    return '↔️ TRANSITIONAL', 'regime-neutral'

# ══════════════════════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def gauge_chart(val, title, lo, hi, thresh, colors, suffix=''):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        title={'text': title, 'font': {'size': 13, 'color': '#e2e8f0'}},
        number={'font': {'size': 24, 'color': '#e2e8f0'}, 'suffix': suffix},
        gauge={
            'axis': {'range': [lo, hi], 'tickcolor': '#64748b', 'tickfont': {'size': 9}},
            'bar': {'color': '#3b82f6', 'thickness': 0.3},
            'bgcolor': '#1f2937', 'borderwidth': 2, 'bordercolor': '#1e3a5f',
            'steps': [{'range': [thresh[i], thresh[i+1]], 'color': colors[i]} for i in range(len(thresh)-1)],
            'threshold': {'line': {'color': '#fff', 'width': 3}, 'thickness': 0.8, 'value': val}
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=180, margin=dict(l=15,r=15,t=35,b=15))
    return fig

def line_chart(df, x, ys, title, colors=None, height=350):
    colors = colors or ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
    fig = go.Figure()
    for i, y in enumerate(ys):
        if y in df.columns:
            fig.add_trace(go.Scatter(x=df[x], y=df[y], name=y.replace('_',' '), 
                                    line=dict(color=colors[i%len(colors)], width=2)))
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color='#e2e8f0'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0'), xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'),
        legend=dict(bgcolor='rgba(17,24,39,0.9)', orientation='h', y=1.12, x=0.5, xanchor='center'),
        height=height, margin=dict(l=50,r=30,t=50,b=40),
        hovermode='x unified'
    )
    return fig

def erp_chart(df):
    """ERP chart with India-calibrated zones"""
    fig = go.Figure()
    
    # Add zones (India-calibrated)
    fig.add_hrect(y0=-6, y1=-4.2, fillcolor="rgba(239,68,68,0.15)", line_width=0, 
                 annotation_text="Expensive", annotation_position="left")
    fig.add_hrect(y0=-4.2, y1=-3.2, fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hrect(y0=-3.2, y1=-1, fillcolor="rgba(16,185,129,0.15)", line_width=0,
                 annotation_text="Cheap", annotation_position="left")
    
    fig.add_trace(go.Scatter(x=df['Date'], y=df['ERP'], name='ERP',
                            line=dict(color='#06b6d4', width=2),
                            fill='tozeroy', fillcolor='rgba(6,182,212,0.2)'))
    
    # Reference lines (India-calibrated)
    fig.add_hline(y=-2.5, line_dash="dash", line_color="#10b981", line_width=1,
                 annotation_text="Very Cheap (-2.5%)")
    fig.add_hline(y=-3.7, line_dash="dot", line_color="#f59e0b", line_width=1,
                 annotation_text="Median (-3.7%)")
    fig.add_hline(y=-4.5, line_dash="dash", line_color="#ef4444", line_width=1,
                 annotation_text="Very Expensive (-4.5%)")
    
    fig.update_layout(
        title=dict(text='📈 ERP (India-Calibrated) - Earnings Yield minus G-Sec Yield', 
                  font=dict(size=15, color='#e2e8f0'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        xaxis=dict(gridcolor='#1e3a5f'), 
        yaxis=dict(gridcolor='#1e3a5f', title='ERP %', range=[-6, -1]),
        showlegend=False, height=380
    )
    return fig

def pe_pb_div_chart(df):
    """Combined PE, PB, Dividend Yield chart"""
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                       subplot_titles=('PE Ratio', 'PB Ratio', 'Dividend Yield %'))
    
    # PE
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Nifty50_PE'], name='PE',
                            line=dict(color='#3b82f6', width=2)), row=1, col=1)
    fig.add_hline(y=25, line_dash="dash", line_color="#f59e0b", row=1, col=1)
    
    # PB
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Nifty50_PB'], name='PB',
                            line=dict(color='#8b5cf6', width=2)), row=2, col=1)
    fig.add_hline(y=3.3, line_dash="dash", line_color="#f59e0b", row=2, col=1)
    
    # Div Yield
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Nifty50_DivYield'], name='Div Yield',
                            line=dict(color='#10b981', width=2)), row=3, col=1)
    fig.add_hline(y=1.3, line_dash="dash", line_color="#f59e0b", row=3, col=1)
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0'), height=450, showlegend=False,
        margin=dict(l=50,r=30,t=40,b=40)
    )
    fig.update_xaxes(gridcolor='#1e3a5f')
    fig.update_yaxes(gridcolor='#1e3a5f')
    
    return fig

def vix_chart(df):
    fig = go.Figure()
    fig.add_hrect(y0=0, y1=12, fillcolor="rgba(239,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=12, y1=20, fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hrect(y0=20, y1=50, fillcolor="rgba(16,185,129,0.1)", line_width=0)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['VIX'], line=dict(color='#8b5cf6', width=2),
                            fill='tozeroy', fillcolor='rgba(139,92,246,0.2)'))
    fig.add_hline(y=12, line_dash="dash", line_color="#ef4444")
    fig.add_hline(y=20, line_dash="dash", line_color="#f59e0b")
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981")
    fig.update_layout(
        title=dict(text='😱 India VIX - Fear & Greed', font=dict(size=15, color='#e2e8f0'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f', title='VIX'),
        showlegend=False, height=350
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown('<h1 class="main-title">🇮🇳 PRO QUANT INDIA DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">India-Calibrated Market Timing & Valuation System</p>', unsafe_allow_html=True)
    
    # Load data
    raw, status = load_data()
    df = process_data(raw)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📁 Data Status")
        for k, v in status.items():
            st.markdown(f"**{k}:** {v}")
        
        st.markdown("---")
        st.markdown("### 🎯 India ERP Calibration")
        st.markdown("""
        <div class="calibration-note">
        <strong>Why Indian ERP is Negative:</strong><br>
        • G-Sec yields: 6-8% (high)<br>
        • Earnings yield: 4-5.5%<br>
        • ERP = E/Y - GSec = -3% typically<br><br>
        <strong>Thresholds (India):</strong><br>
        • > -2.5%: Very Cheap ✅<br>
        • > -3.2%: Cheap<br>
        • > -3.7%: Fair<br>
        • > -4.2%: Expensive<br>
        • < -4.5%: V.Expensive ❌
        </div>
        """, unsafe_allow_html=True)
    
    # Check data
    if df is None:
        st.error("⚠️ Could not load data!")
        st.markdown("""
        ### Required Files:
        1. `Nifty50_PE_PB_Div_Merged.csv` ⭐ (Primary)
        2. `India_VIX_Yahoo.csv`
        3. `Nifty_10Y_Benchmark_GSec_Merged.csv`
        4. `Nifty50_Historical_Yahoo.csv`
        """)
        return
    
    # Get latest
    latest = df.iloc[-1]
    
    # Calculate signals
    erp_txt, erp_sc, erp_col = india_erp_signal(latest.get('ERP', -3.5))
    pe_txt, pe_sc, pe_col = india_pe_signal(latest.get('Nifty50_PE', 22), latest.get('PE_Percentile', 50))
    pb_txt, pb_sc, pb_col = india_pb_signal(latest.get('Nifty50_PB', 3.0))
    div_txt, div_sc, div_col = india_divyield_signal(latest.get('Nifty50_DivYield', 1.3))
    vix_txt, vix_sc, vix_col = vix_signal(latest.get('VIX', 15))
    
    sig_txt, sig_sc, sig_cls = composite_signal(erp_sc, pe_sc, vix_sc, pb_sc, div_sc)
    reg_txt, reg_cls = market_regime(latest.get('VIX', 15), erp_sc, pe_sc, latest.get('Drawdown', 0))
    
    # Sidebar metrics
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 📊 Quick Stats")
        if 'Nifty50' in latest:
            st.metric("Nifty 50", f"{latest['Nifty50']:,.0f}", f"{latest.get('Drawdown',0):.1f}% from ATH")
        st.metric("PE Ratio", f"{latest.get('Nifty50_PE', 0):.2f}", f"{latest.get('PE_Percentile',0):.0f}th Pctl")
        st.metric("ERP", f"{latest.get('ERP', 0):.2f}%", erp_txt)
        st.metric("VIX", f"{latest.get('VIX', 0):.2f}", vix_txt)
    
    # Main content
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Row 1: Key Metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        pe = latest.get('Nifty50_PE', 22)
        pct = latest.get('PE_Percentile', 50)
        dcls = 'delta-positive' if pe_sc > 0 else 'delta-negative' if pe_sc < 0 else 'delta-neutral'
        st.markdown(f'<div class="metric-card"><div class="metric-label">PE Ratio</div><div class="metric-value">{pe:.2f}</div><div class="metric-delta {dcls}">{pe_txt}</div></div>', unsafe_allow_html=True)
    
    with c2:
        pb = latest.get('Nifty50_PB', 3.0)
        dcls = 'delta-positive' if pb_sc > 0 else 'delta-negative' if pb_sc < 0 else 'delta-neutral'
        st.markdown(f'<div class="metric-card"><div class="metric-label">PB Ratio</div><div class="metric-value">{pb:.2f}</div><div class="metric-delta {dcls}">{pb_txt}</div></div>', unsafe_allow_html=True)
    
    with c3:
        div = latest.get('Nifty50_DivYield', 1.3)
        dcls = 'delta-positive' if div_sc > 0 else 'delta-negative' if div_sc < 0 else 'delta-neutral'
        st.markdown(f'<div class="metric-card"><div class="metric-label">Div Yield</div><div class="metric-value">{div:.2f}%</div><div class="metric-delta {dcls}">{div_txt}</div></div>', unsafe_allow_html=True)
    
    with c4:
        erp = latest.get('ERP', -3.5)
        dcls = 'delta-positive' if erp_sc > 0 else 'delta-negative' if erp_sc < 0 else 'delta-neutral'
        st.markdown(f'<div class="metric-card"><div class="metric-label">ERP (India)</div><div class="metric-value" style="color:{erp_col}">{erp:.2f}%</div><div class="metric-delta {dcls}">{erp_txt}</div></div>', unsafe_allow_html=True)
    
    with c5:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Signal</div><div style="text-align:center;padding:0.3rem"><div class="signal-badge {sig_cls}">{sig_txt}</div></div><div class="metric-delta delta-neutral">Score: {sig_sc:.2f}</div></div>', unsafe_allow_html=True)
    
    # Row 2: Regime + Gauges
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown(f'<div class="regime-banner {reg_cls}">{reg_txt}</div>', unsafe_allow_html=True)
        
        # Recommendation
        if sig_sc >= 0.5:
            st.markdown('<div class="info-box info-success"><strong>💡 Recommendation:</strong><br>Favorable valuations for accumulation. PE is in lower percentiles historically. Consider increasing SIPs.</div>', unsafe_allow_html=True)
        elif sig_sc <= -0.5:
            st.markdown('<div class="info-box info-danger"><strong>⚠️ Caution:</strong><br>Valuations stretched. Consider profit booking on rallies. Maintain defensive allocation.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box info-warning"><strong>📊 Note:</strong><br>Mixed signals. Valuations near historical average. Continue regular SIPs.</div>', unsafe_allow_html=True)
        
        # India context note
        st.markdown('<div class="info-box info-primary"><strong>🇮🇳 India Context:</strong><br>ERP thresholds calibrated for Indian market where G-Sec yields (6-8%) exceed earnings yields, making ERP structurally negative.</div>', unsafe_allow_html=True)
    
    with c2:
        g1, g2, g3, g4 = st.columns(4)
        with g1:
            st.plotly_chart(gauge_chart(latest.get('Nifty50_PE',22), "PE", 15, 40, 
                           [15,20,22,25,28,32,40], ['#059669','#10b981','#84cc16','#f59e0b','#f97316','#ef4444']), 
                           use_container_width=True)
        with g2:
            st.plotly_chart(gauge_chart(latest.get('Nifty50_PB',3), "PB", 2, 5,
                           [2,2.8,3.3,3.8,4.5,5], ['#10b981','#84cc16','#f59e0b','#f97316','#ef4444']),
                           use_container_width=True)
        with g3:
            st.plotly_chart(gauge_chart(latest.get('VIX',15), "VIX", 8, 40,
                           [8,12,15,20,25,40], ['#ef4444','#f97316','#f59e0b','#84cc16','#10b981']),
                           use_container_width=True)
        with g4:
            st.plotly_chart(gauge_chart(latest.get('ERP',-3.5), "ERP%", -6, -1,
                           [-6,-4.5,-4.2,-3.7,-3.2,-2.5,-1], ['#ef4444','#f97316','#f59e0b','#84cc16','#10b981','#059669'], '%'),
                           use_container_width=True)
    
    # Row 3: Charts
    st.markdown('<div class="section-header">📈 Historical Analysis</div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["📊 ERP (India-Calibrated)", "💰 PE/PB/Div", "😱 VIX Sentiment", "📈 Valuation Bands"])
    
    with t1:
        st.plotly_chart(erp_chart(df), use_container_width=True)
        st.markdown("""
        <div class="calibration-note">
        <strong>Reading the ERP Chart:</strong> In India, ERP is typically between -2% and -5%. 
        Values closer to -2% indicate cheap markets (historically top 10%), while values below -4.5% indicate expensive markets.
        </div>
        """, unsafe_allow_html=True)
    
    with t2:
        st.plotly_chart(pe_pb_div_chart(df), use_container_width=True)
    
    with t3:
        st.plotly_chart(vix_chart(df), use_container_width=True)
    
    with t4:
        # Valuation bands chart
        fig = go.Figure()
        
        pe_mean = df['Nifty50_PE'].mean()
        pe_std = df['Nifty50_PE'].std()
        
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Nifty50_PE'], name='PE',
                                line=dict(color='#3b82f6', width=2)))
        fig.add_hline(y=pe_mean, line_dash="solid", line_color="#f59e0b", 
                     annotation_text=f"Mean: {pe_mean:.1f}")
        fig.add_hline(y=pe_mean + pe_std, line_dash="dash", line_color="#ef4444",
                     annotation_text=f"+1 Std: {pe_mean+pe_std:.1f}")
        fig.add_hline(y=pe_mean - pe_std, line_dash="dash", line_color="#10b981",
                     annotation_text=f"-1 Std: {pe_mean-pe_std:.1f}")
        fig.add_hline(y=pe_mean + 2*pe_std, line_dash="dot", line_color="#ef4444")
        fig.add_hline(y=pe_mean - 2*pe_std, line_dash="dot", line_color="#10b981")
        
        fig.update_layout(
            title=dict(text='📊 PE Valuation Bands (Mean ± Std Dev)', font=dict(size=15, color='#e2e8f0'), x=0.5),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
            xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f', title='PE Ratio'),
            showlegend=False, height=380
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 4: Historical Data Table
    st.markdown('<div class="section-header">📋 Recent Data</div>', unsafe_allow_html=True)
    
    disp = df.tail(20).copy()
    disp['Date'] = disp['Date'].dt.strftime('%Y-%m-%d')
    disp['ERP_Signal'] = disp['ERP'].apply(lambda x: india_erp_signal(x)[0])
    disp['PE_Signal'] = disp['Nifty50_PE'].apply(lambda x: india_pe_signal(x)[0])
    
    cols = ['Date', 'Nifty50_PE', 'Nifty50_PB', 'Nifty50_DivYield', 'ERP', 'VIX', 'ERP_Signal', 'PE_Signal']
    cols = [c for c in cols if c in disp.columns]
    disp = disp[cols]
    
    for c in ['Nifty50_PE', 'Nifty50_PB', 'Nifty50_DivYield', 'ERP', 'VIX']:
        if c in disp.columns:
            disp[c] = disp[c].round(2)
    
    st.dataframe(disp, use_container_width=True, height=400, hide_index=True)
    
    # Footer
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align:center;color:#64748b;font-size:0.85rem">
    🇮🇳 Pro Quant India Dashboard | India-Calibrated Thresholds | Built with Streamlit<br>
    <em>ERP thresholds based on historical analysis of Indian market (2016-2026)</em>
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
