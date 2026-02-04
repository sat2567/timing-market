"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        🇮🇳 PRO QUANT INDIA MULTI-CAP MARKET TIMING DASHBOARD 🇮🇳              ║
║                                                                              ║
║  India-Calibrated Valuation Analysis for Nifty 50 & Midcap 100               ║
║  Features: PE/PB/Div Analysis | ERP Signals | Multi-Cap Comparison          ║
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
    page_title="Pro Quant India Multi-Cap Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    SCRIPT_DIR = Path(__file__).parent.resolve()
except:
    SCRIPT_DIR = Path.cwd()

# ══════════════════════════════════════════════════════════════════════════════
# INDIA-CALIBRATED THRESHOLDS (Based on Historical Analysis)
# ══════════════════════════════════════════════════════════════════════════════

"""
NIFTY 50 (2016-2026):
- PE: Mean 24.8, Median 23.4, Range 17-42
- PB: Mean 3.7, Range 2.5-5.5
- DivYield: Mean 1.27%, Range 0.8-2.0%
- ERP: Mean -3.73%, Range -5.2% to -1.6%

MIDCAP 100 (2016-2026):
- PE: Mean 33.7, Median 31.0, Range 17-96
- PB: Mean 3.3, Range 1.7-5.6
- DivYield: Mean 1.09%, Range 0.6-2.1%
"""

# Nifty 50 Thresholds
N50_PE_THRESHOLDS = {'very_cheap': 20, 'cheap': 22, 'fair': 25, 'expensive': 28, 'very_expensive': 32}
N50_PB_THRESHOLDS = {'cheap': 3.0, 'fair': 3.5, 'expensive': 4.0, 'very_expensive': 4.5}
N50_DIV_THRESHOLDS = {'high': 1.5, 'avg': 1.2, 'low': 1.0}
N50_ERP_THRESHOLDS = {'very_cheap': -2.5, 'cheap': -3.2, 'fair': -3.7, 'expensive': -4.2}

# Midcap 100 Thresholds (Higher PE is normal for midcaps)
MID_PE_THRESHOLDS = {'very_cheap': 24, 'cheap': 28, 'fair': 33, 'expensive': 40, 'very_expensive': 50}
MID_PB_THRESHOLDS = {'cheap': 2.8, 'fair': 3.3, 'expensive': 4.0, 'very_expensive': 4.5}
MID_DIV_THRESHOLDS = {'high': 1.2, 'avg': 1.0, 'low': 0.8}

# ══════════════════════════════════════════════════════════════════════════════
# CSS STYLES
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
    --green: #10b981;
    --red: #ef4444;
    --yellow: #f59e0b;
    --blue: #3b82f6;
    --purple: #8b5cf6;
}

.stApp { background: linear-gradient(180deg, #0a0f1a 0%, #111827 100%); }
#MainMenu, footer, header {visibility: hidden;}

.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #ff9933, #ffffff, #138808);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 0.5rem 0;
}

.subtitle {
    font-family: 'Rajdhani', sans-serif;
    color: #64748b;
    text-align: center;
    letter-spacing: 2px;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

.index-header {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 0.5rem;
}

.nifty50-header { background: linear-gradient(135deg, #1e3a5f, #0f172a); color: #3b82f6; border: 1px solid #3b82f6; }
.midcap-header { background: linear-gradient(135deg, #3d1e5f, #1a0f2e); color: #8b5cf6; border: 1px solid #8b5cf6; }

.metric-card {
    background: linear-gradient(135deg, #111827, #1f2937);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.3s ease;
    margin-bottom: 0.5rem;
}

.metric-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 15px rgba(59,130,246,0.2);
}

.metric-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0.3rem 0;
}

.metric-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
    display: inline-block;
}

.delta-positive { background: rgba(16,185,129,0.2); color: #10b981; }
.delta-negative { background: rgba(239,68,68,0.2); color: #ef4444; }
.delta-neutral { background: rgba(245,158,11,0.2); color: #f59e0b; }

.signal-badge {
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    display: inline-block;
}

.signal-buy { background: linear-gradient(135deg, #059669, #10b981); color: white; }
.signal-sell { background: linear-gradient(135deg, #dc2626, #ef4444); color: white; }
.signal-hold { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }
.signal-trim { background: linear-gradient(135deg, #ea580c, #f97316); color: white; }
.signal-accumulate { background: linear-gradient(135deg, #0891b2, #06b6d4); color: white; }

.regime-banner {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    font-weight: 700;
    padding: 0.75rem;
    border-radius: 10px;
    text-align: center;
    margin: 0.5rem 0;
}

.regime-bull { background: linear-gradient(135deg, #064e3b, #065f46); border: 2px solid #10b981; color: #10b981; }
.regime-bear { background: linear-gradient(135deg, #450a0a, #7f1d1d); border: 2px solid #ef4444; color: #ef4444; }
.regime-neutral { background: linear-gradient(135deg, #451a03, #78350f); border: 2px solid #f59e0b; color: #f59e0b; }

.comparison-card {
    background: linear-gradient(135deg, #1e1e2e, #2d2d3d);
    border: 1px solid #3d3d5c;
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
}

.info-box { border-radius: 8px; padding: 0.75rem; margin: 0.5rem 0; font-size: 0.85rem; }
.info-success { background: linear-gradient(135deg, #064e3b, #111827); border-left: 3px solid #10b981; color: #e2e8f0; }
.info-warning { background: linear-gradient(135deg, #451a03, #111827); border-left: 3px solid #f59e0b; color: #e2e8f0; }
.info-danger { background: linear-gradient(135deg, #450a0a, #111827); border-left: 3px solid #ef4444; color: #e2e8f0; }
.info-primary { background: linear-gradient(135deg, #1e3a5f, #111827); border-left: 3px solid #3b82f6; color: #e2e8f0; }

.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    color: #e2e8f0;
    padding: 0.5rem 0.75rem;
    margin: 1rem 0 0.5rem 0;
    background: linear-gradient(90deg, rgba(59,130,246,0.2), transparent);
    border-left: 3px solid #3b82f6;
    border-radius: 0 6px 6px 0;
}

.divider { height: 1px; background: linear-gradient(90deg, transparent, #ff9933, #138808, transparent); margin: 1rem 0; }

.calibration-note {
    font-size: 0.75rem;
    color: #64748b;
    background: rgba(30, 58, 95, 0.3);
    padding: 0.5rem;
    border-radius: 6px;
    border-left: 2px solid #ff9933;
}

[data-testid="stSidebar"] { background: linear-gradient(180deg, #111827, #0a0f1a); }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.stTabs [data-baseweb="tab-list"] { background: #111827; padding: 4px; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { font-family: 'Rajdhani', sans-serif; font-weight: 600; color: #64748b; font-size: 0.9rem; }
.stTabs [aria-selected="true"] { background: #1e3a5f; color: #3b82f6 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

def find_file(names):
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
    data, status = {}, {}
    
    configs = {
        'nifty50_pe': ['Nifty50_PE_PB_Div_Merged.csv'],
        'midcap_pe': ['NiftyMidcap100_PE_PB_Div_Merged.csv'],
        'nifty50': ['Nifty50_Historical_Yahoo.csv'],
        'vix': ['India_VIX_Yahoo.csv'],
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
    """Process both Nifty 50 and Midcap 100 data"""
    
    result = {'nifty50': None, 'midcap': None}
    
    # Process Nifty 50
    if raw.get('nifty50_pe') is not None:
        df = raw['nifty50_pe'].copy()
        df = df.rename(columns={'PE': 'PE', 'PB': 'PB', 'DivYield': 'DivYield'})
        
        # Merge prices
        if raw.get('nifty50') is not None:
            prices = raw['nifty50'][['Date', 'Close']].copy()
            prices.columns = ['Date', 'Price']
            df = pd.merge(df, prices, on='Date', how='left')
        
        # Merge VIX
        if raw.get('vix') is not None:
            vix = raw['vix'].copy()
            col = 'VIX_Close' if 'VIX_Close' in vix.columns else 'Close'
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
        
        df = df.sort_values('Date').ffill().bfill()
        
        # Calculate metrics
        df['Earnings_Yield'] = (1 / df['PE']) * 100
        df['ERP'] = df['Earnings_Yield'] - df['GSec_Yield']
        df['PE_Percentile'] = df['PE'].rank(pct=True) * 100
        df['PB_Percentile'] = df['PB'].rank(pct=True) * 100
        df['ERP_Percentile'] = df['ERP'].rank(pct=True) * 100
        
        if 'Price' in df.columns:
            df['ATH'] = df['Price'].expanding().max()
            df['Drawdown'] = ((df['Price'] / df['ATH']) - 1) * 100
        
        result['nifty50'] = df
    
    # Process Midcap 100
    if raw.get('midcap_pe') is not None:
        df = raw['midcap_pe'].copy()
        df = df.rename(columns={'PE': 'PE', 'PB': 'PB', 'DivYield': 'DivYield'})
        df = df.sort_values('Date')
        
        # Calculate percentiles
        df['PE_Percentile'] = df['PE'].rank(pct=True) * 100
        df['PB_Percentile'] = df['PB'].rank(pct=True) * 100
        
        # Calculate ERP for Midcap (use same G-Sec yield)
        df['Earnings_Yield'] = (1 / df['PE']) * 100
        if raw.get('gsec') is not None:
            gsec = raw['gsec'].copy()
            gsec['GSec_Yield'] = 17 - (gsec['Close'] / 100)
            gsec['YearMonth'] = gsec['Date'].dt.to_period('M')
            df['YearMonth'] = df['Date'].dt.to_period('M')
            gsec_monthly = gsec.groupby('YearMonth')['GSec_Yield'].last().reset_index()
            df = pd.merge(df, gsec_monthly, on='YearMonth', how='left')
            df = df.drop('YearMonth', axis=1)
        if 'GSec_Yield' not in df.columns:
            df['GSec_Yield'] = 7.5
        df['GSec_Yield'] = df['GSec_Yield'].ffill().bfill()
        df['ERP'] = df['Earnings_Yield'] - df['GSec_Yield']
        df['ERP_Percentile'] = df['ERP'].rank(pct=True) * 100
        
        result['midcap'] = df
    
    return result

# ══════════════════════════════════════════════════════════════════════════════
# SIGNAL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def nifty50_pe_signal(pe, pe_pct=None):
    if pd.isna(pe): return 'NO DATA', 0, '#64748b'
    if pe_pct is not None:
        if pe_pct < 20: return 'UNDERVALUED', 2, '#10b981'
        if pe_pct < 40: return 'CHEAP', 1, '#34d399'
        if pe_pct < 60: return 'FAIR', 0, '#f59e0b'
        if pe_pct < 80: return 'EXPENSIVE', -1, '#f97316'
        return 'OVERVALUED', -2, '#ef4444'
    if pe < 20: return 'UNDERVALUED', 2, '#10b981'
    if pe < 22: return 'CHEAP', 1, '#34d399'
    if pe < 25: return 'FAIR', 0, '#f59e0b'
    if pe < 28: return 'EXPENSIVE', -1, '#f97316'
    return 'OVERVALUED', -2, '#ef4444'

def midcap_pe_signal(pe, pe_pct=None):
    """Midcap has higher PE norms"""
    if pd.isna(pe): return 'NO DATA', 0, '#64748b'
    if pe_pct is not None:
        if pe_pct < 20: return 'UNDERVALUED', 2, '#10b981'
        if pe_pct < 40: return 'CHEAP', 1, '#34d399'
        if pe_pct < 60: return 'FAIR', 0, '#f59e0b'
        if pe_pct < 80: return 'EXPENSIVE', -1, '#f97316'
        return 'OVERVALUED', -2, '#ef4444'
    if pe < 24: return 'UNDERVALUED', 2, '#10b981'
    if pe < 28: return 'CHEAP', 1, '#34d399'
    if pe < 33: return 'FAIR', 0, '#f59e0b'
    if pe < 40: return 'EXPENSIVE', -1, '#f97316'
    return 'OVERVALUED', -2, '#ef4444'

def pb_signal(pb, is_midcap=False):
    if pd.isna(pb): return 'NO DATA', 0, '#64748b'
    thresh = MID_PB_THRESHOLDS if is_midcap else N50_PB_THRESHOLDS
    if pb < thresh['cheap']: return 'CHEAP', 1, '#10b981'
    if pb < thresh['fair']: return 'FAIR', 0, '#f59e0b'
    if pb < thresh['expensive']: return 'EXPENSIVE', -1, '#f97316'
    return 'VERY EXPENSIVE', -2, '#ef4444'

def div_signal(div, is_midcap=False):
    if pd.isna(div): return 'NO DATA', 0, '#64748b'
    thresh = MID_DIV_THRESHOLDS if is_midcap else N50_DIV_THRESHOLDS
    if div > thresh['high']: return 'HIGH', 1, '#10b981'
    if div > thresh['avg']: return 'AVERAGE', 0, '#f59e0b'
    return 'LOW', -1, '#ef4444'

def india_erp_signal(erp):
    """India-calibrated ERP (structurally negative)"""
    if pd.isna(erp): return 'NO DATA', 0, '#64748b'
    if erp > -2.5: return 'VERY CHEAP', 2, '#10b981'
    if erp > -3.2: return 'CHEAP', 1, '#34d399'
    if erp > -3.7: return 'FAIR', 0, '#f59e0b'
    if erp > -4.2: return 'EXPENSIVE', -1, '#f97316'
    return 'VERY EXPENSIVE', -2, '#ef4444'

def vix_signal(vix):
    if pd.isna(vix): return 'NO DATA', 0, '#64748b'
    if vix > 30: return 'EXTREME FEAR', 2, '#10b981'
    if vix > 25: return 'HIGH FEAR', 1.5, '#34d399'
    if vix > 20: return 'FEAR', 1, '#84cc16'
    if vix > 15: return 'ELEVATED', 0.5, '#f59e0b'
    if vix > 12: return 'NORMAL', 0, '#64748b'
    return 'COMPLACENCY', -1, '#ef4444'

def composite_signal(pe_score, pb_score, div_score, vix_score=0, erp_score=0):
    """Composite signal: PE 35%, PB 20%, Div 15%, VIX 15%, ERP 15%"""
    comp = pe_score * 0.35 + pb_score * 0.20 + div_score * 0.15 + vix_score * 0.15 + erp_score * 0.15
    if comp >= 1.0: return 'STRONG BUY', comp, 'signal-buy'
    if comp >= 0.5: return 'BUY', comp, 'signal-buy'
    if comp >= 0.1: return 'ACCUMULATE', comp, 'signal-accumulate'
    if comp >= -0.3: return 'HOLD', comp, 'signal-hold'
    if comp >= -0.7: return 'TRIM', comp, 'signal-trim'
    return 'REDUCE', comp, 'signal-sell'

# ══════════════════════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def gauge_chart(val, title, lo, hi, thresh, colors, suffix=''):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=val,
        title={'text': title, 'font': {'size': 12, 'color': '#e2e8f0'}},
        number={'font': {'size': 22, 'color': '#e2e8f0'}, 'suffix': suffix},
        gauge={
            'axis': {'range': [lo, hi], 'tickcolor': '#64748b', 'tickfont': {'size': 8}},
            'bar': {'color': '#3b82f6', 'thickness': 0.3},
            'bgcolor': '#1f2937', 'borderwidth': 2, 'bordercolor': '#1e3a5f',
            'steps': [{'range': [thresh[i], thresh[i+1]], 'color': colors[i]} for i in range(len(thresh)-1)],
            'threshold': {'line': {'color': '#fff', 'width': 2}, 'thickness': 0.75, 'value': val}
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=160, margin=dict(l=10,r=10,t=30,b=10))
    return fig

def comparison_bar_chart(n50_val, mid_val, n50_pct, mid_pct, title):
    """Side-by-side comparison chart"""
    fig = go.Figure()
    
    colors = ['#3b82f6', '#8b5cf6']
    
    fig.add_trace(go.Bar(
        name='Nifty 50', x=['Current', 'Percentile'],
        y=[n50_val, n50_pct], marker_color=colors[0],
        text=[f'{n50_val:.1f}', f'{n50_pct:.0f}%'], textposition='outside'
    ))
    fig.add_trace(go.Bar(
        name='Midcap 100', x=['Current', 'Percentile'],
        y=[mid_val, mid_pct], marker_color=colors[1],
        text=[f'{mid_val:.1f}', f'{mid_pct:.0f}%'], textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#e2e8f0'), x=0.5),
        barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0', size=10),
        xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'),
        legend=dict(orientation='h', y=1.15, x=0.5, xanchor='center'),
        height=280, margin=dict(l=40,r=20,t=60,b=30)
    )
    return fig

def dual_line_chart(df1, df2, x, y, title, label1='Nifty 50', label2='Midcap 100'):
    """Dual line chart for comparison"""
    fig = go.Figure()
    
    if df1 is not None and y in df1.columns:
        fig.add_trace(go.Scatter(x=df1[x], y=df1[y], name=label1,
                                line=dict(color='#3b82f6', width=2)))
    if df2 is not None and y in df2.columns:
        fig.add_trace(go.Scatter(x=df2[x], y=df2[y], name=label2,
                                line=dict(color='#8b5cf6', width=2)))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#e2e8f0'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0'), xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'),
        legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center'),
        height=320, margin=dict(l=50,r=30,t=50,b=40), hovermode='x unified'
    )
    return fig

def pe_pb_div_subplot(df, title_prefix, color):
    """PE, PB, Div subplot"""
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                       subplot_titles=(f'{title_prefix} PE', f'{title_prefix} PB', f'{title_prefix} Div Yield'))
    
    fig.add_trace(go.Scatter(x=df['Date'], y=df['PE'], line=dict(color=color, width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['PB'], line=dict(color=color, width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['DivYield'], line=dict(color=color, width=2)), row=3, col=1)
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0'), height=400, showlegend=False,
        margin=dict(l=50,r=30,t=30,b=30)
    )
    fig.update_xaxes(gridcolor='#1e3a5f')
    fig.update_yaxes(gridcolor='#1e3a5f')
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown('<h1 class="main-title">🇮🇳 PRO QUANT INDIA MULTI-CAP DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">India-Calibrated Valuation: Nifty 50 & Midcap 100</p>', unsafe_allow_html=True)
    
    # Load data
    raw, status = load_data()
    data = process_data(raw)
    
    n50_df = data.get('nifty50')
    mid_df = data.get('midcap')
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📁 Data Status")
        for k, v in status.items():
            st.markdown(f"**{k}:** {v}")
        
        st.markdown("---")
        st.markdown("### 🎯 India Calibration")
        st.markdown("""
        <div class="calibration-note">
        <strong>Nifty 50:</strong><br>
        PE: Mean 24.8, Range 17-42<br>
        PB: Mean 3.7, Range 2.5-5.5<br><br>
        <strong>Midcap 100:</strong><br>
        PE: Mean 33.7, Range 17-96<br>
        PB: Mean 3.3, Range 1.7-5.6<br><br>
        <em>Midcaps trade at PE premium</em>
        </div>
        """, unsafe_allow_html=True)
    
    if n50_df is None and mid_df is None:
        st.error("⚠️ No data loaded!")
        st.markdown("""
        ### Required Files:
        - `Nifty50_PE_PB_Div_Merged.csv`
        - `NiftyMidcap100_PE_PB_Div_Merged.csv`
        """)
        return
    
    # Get latest values
    n50_latest = n50_df.iloc[-1] if n50_df is not None else {}
    mid_latest = mid_df.iloc[-1] if mid_df is not None else {}
    
    # Calculate signals
    if n50_df is not None:
        n50_pe_txt, n50_pe_sc, n50_pe_col = nifty50_pe_signal(n50_latest.get('PE'), n50_latest.get('PE_Percentile'))
        n50_pb_txt, n50_pb_sc, n50_pb_col = pb_signal(n50_latest.get('PB'))
        n50_div_txt, n50_div_sc, n50_div_col = div_signal(n50_latest.get('DivYield'))
        n50_erp_txt, n50_erp_sc, n50_erp_col = india_erp_signal(n50_latest.get('ERP'))
        vix_txt, vix_sc, vix_col = vix_signal(n50_latest.get('VIX', 15))
        n50_sig_txt, n50_sig_sc, n50_sig_cls = composite_signal(n50_pe_sc, n50_pb_sc, n50_div_sc, vix_sc, n50_erp_sc)
    
    if mid_df is not None:
        mid_pe_txt, mid_pe_sc, mid_pe_col = midcap_pe_signal(mid_latest.get('PE'), mid_latest.get('PE_Percentile'))
        mid_pb_txt, mid_pb_sc, mid_pb_col = pb_signal(mid_latest.get('PB'), is_midcap=True)
        mid_div_txt, mid_div_sc, mid_div_col = div_signal(mid_latest.get('DivYield'), is_midcap=True)
        mid_erp_txt, mid_erp_sc, mid_erp_col = india_erp_signal(mid_latest.get('ERP'))
        mid_sig_txt, mid_sig_sc, mid_sig_cls = composite_signal(mid_pe_sc, mid_pb_sc, mid_div_sc, 0, mid_erp_sc)
    
    # Sidebar metrics
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 📊 Current Values")
        if n50_df is not None:
            st.metric("Nifty 50 PE", f"{n50_latest.get('PE', 0):.2f}", f"{n50_latest.get('PE_Percentile', 0):.0f}th pctl")
        if mid_df is not None:
            st.metric("Midcap PE", f"{mid_latest.get('PE', 0):.2f}", f"{mid_latest.get('PE_Percentile', 0):.0f}th pctl")
        if n50_df is not None:
            st.metric("India VIX", f"{n50_latest.get('VIX', 0):.2f}", vix_txt)
    
    # Main content
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ══════════════════════════════════════════════════════════════════════════
    # ROW 1: Side-by-side Index Cards
    # ══════════════════════════════════════════════════════════════════════════
    
    col1, col2 = st.columns(2)
    
    # NIFTY 50 CARD
    with col1:
        st.markdown('<div class="index-header nifty50-header">📊 NIFTY 50</div>', unsafe_allow_html=True)
        
        if n50_df is not None:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                dcls = 'delta-positive' if n50_pe_sc > 0 else 'delta-negative' if n50_pe_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">PE Ratio</div><div class="metric-value">{n50_latest.get("PE", 0):.1f}</div><div class="metric-delta {dcls}">{n50_pe_txt}</div></div>', unsafe_allow_html=True)
            with c2:
                dcls = 'delta-positive' if n50_pb_sc > 0 else 'delta-negative' if n50_pb_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">PB Ratio</div><div class="metric-value">{n50_latest.get("PB", 0):.2f}</div><div class="metric-delta {dcls}">{n50_pb_txt}</div></div>', unsafe_allow_html=True)
            with c3:
                dcls = 'delta-positive' if n50_div_sc > 0 else 'delta-negative' if n50_div_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">Div Yield</div><div class="metric-value">{n50_latest.get("DivYield", 0):.2f}%</div><div class="metric-delta {dcls}">{n50_div_txt}</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Signal</div><div style="padding:0.3rem"><div class="signal-badge {n50_sig_cls}">{n50_sig_txt}</div></div></div>', unsafe_allow_html=True)
            
            # Percentile row
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">PE Pctl</div><div class="metric-value" style="font-size:1.2rem">{n50_latest.get("PE_Percentile", 0):.0f}%</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">PB Pctl</div><div class="metric-value" style="font-size:1.2rem">{n50_latest.get("PB_Percentile", 0):.0f}%</div></div>', unsafe_allow_html=True)
            with c3:
                dcls = 'delta-positive' if n50_erp_sc > 0 else 'delta-negative' if n50_erp_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">ERP</div><div class="metric-value" style="font-size:1.2rem;color:{n50_erp_col}">{n50_latest.get("ERP", 0):.2f}%</div><div class="metric-delta {dcls}">{n50_erp_txt}</div></div>', unsafe_allow_html=True)
            with c4:
                dcls = 'delta-positive' if vix_sc > 0 else 'delta-negative' if vix_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">VIX</div><div class="metric-value" style="font-size:1.2rem;color:{vix_col}">{n50_latest.get("VIX", 0):.1f}</div><div class="metric-delta {dcls}">{vix_txt}</div></div>', unsafe_allow_html=True)
        else:
            st.warning("Nifty 50 data not available")
    
    # MIDCAP 100 CARD
    with col2:
        st.markdown('<div class="index-header midcap-header">📈 MIDCAP 100</div>', unsafe_allow_html=True)
        
        if mid_df is not None:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                dcls = 'delta-positive' if mid_pe_sc > 0 else 'delta-negative' if mid_pe_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">PE Ratio</div><div class="metric-value">{mid_latest.get("PE", 0):.1f}</div><div class="metric-delta {dcls}">{mid_pe_txt}</div></div>', unsafe_allow_html=True)
            with c2:
                dcls = 'delta-positive' if mid_pb_sc > 0 else 'delta-negative' if mid_pb_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">PB Ratio</div><div class="metric-value">{mid_latest.get("PB", 0):.2f}</div><div class="metric-delta {dcls}">{mid_pb_txt}</div></div>', unsafe_allow_html=True)
            with c3:
                dcls = 'delta-positive' if mid_div_sc > 0 else 'delta-negative' if mid_div_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">Div Yield</div><div class="metric-value">{mid_latest.get("DivYield", 0):.2f}%</div><div class="metric-delta {dcls}">{mid_div_txt}</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="metric-card"><div class="metric-label">Signal</div><div style="padding:0.3rem"><div class="signal-badge {mid_sig_cls}">{mid_sig_txt}</div></div></div>', unsafe_allow_html=True)
            
            # Percentile row
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="metric-label">PE Pctl</div><div class="metric-value" style="font-size:1.2rem">{mid_latest.get("PE_Percentile", 0):.0f}%</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="metric-label">PB Pctl</div><div class="metric-value" style="font-size:1.2rem">{mid_latest.get("PB_Percentile", 0):.0f}%</div></div>', unsafe_allow_html=True)
            with c3:
                dcls = 'delta-positive' if mid_erp_sc > 0 else 'delta-negative' if mid_erp_sc < 0 else 'delta-neutral'
                st.markdown(f'<div class="metric-card"><div class="metric-label">ERP</div><div class="metric-value" style="font-size:1.2rem;color:{mid_erp_col}">{mid_latest.get("ERP", 0):.2f}%</div><div class="metric-delta {dcls}">{mid_erp_txt}</div></div>', unsafe_allow_html=True)
            with c4:
                # Premium calculation
                if n50_df is not None:
                    premium = mid_latest.get('PE', 0) - n50_latest.get('PE', 0)
                    st.markdown(f'<div class="metric-card"><div class="metric-label">PE Premium</div><div class="metric-value" style="font-size:1.2rem">{premium:+.1f}</div><div class="metric-delta delta-neutral">vs N50</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="metric-card"><div class="metric-label">Data</div><div class="metric-value" style="font-size:1.2rem">--</div></div>', unsafe_allow_html=True)
        else:
            st.warning("Midcap 100 data not available")
    
    # ══════════════════════════════════════════════════════════════════════════
    # ROW 2: Comparison Charts
    # ══════════════════════════════════════════════════════════════════════════
    
    st.markdown('<div class="section-header">📊 Multi-Cap Comparison</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if n50_df is not None and mid_df is not None:
            fig = comparison_bar_chart(
                n50_latest.get('PE', 0), mid_latest.get('PE', 0),
                n50_latest.get('PE_Percentile', 0), mid_latest.get('PE_Percentile', 0),
                '📊 PE Comparison'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if n50_df is not None and mid_df is not None:
            fig = comparison_bar_chart(
                n50_latest.get('PB', 0), mid_latest.get('PB', 0),
                n50_latest.get('PB_Percentile', 0), mid_latest.get('PB_Percentile', 0),
                '📊 PB Comparison'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        if n50_df is not None and mid_df is not None:
            # Div Yield comparison
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Nifty 50', x=['Div Yield'], y=[n50_latest.get('DivYield', 0)],
                                marker_color='#3b82f6', text=[f"{n50_latest.get('DivYield', 0):.2f}%"], textposition='outside'))
            fig.add_trace(go.Bar(name='Midcap 100', x=['Div Yield'], y=[mid_latest.get('DivYield', 0)],
                                marker_color='#8b5cf6', text=[f"{mid_latest.get('DivYield', 0):.2f}%"], textposition='outside'))
            fig.update_layout(
                title=dict(text='📊 Dividend Yield', font=dict(size=14, color='#e2e8f0'), x=0.5),
                barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
                font=dict(color='#e2e8f0'), yaxis=dict(gridcolor='#1e3a5f'),
                legend=dict(orientation='h', y=1.15, x=0.5, xanchor='center'),
                height=280, margin=dict(l=40,r=20,t=60,b=30)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ══════════════════════════════════════════════════════════════════════════
    # ROW 3: Historical Charts
    # ══════════════════════════════════════════════════════════════════════════
    
    st.markdown('<div class="section-header">📈 Historical Analysis</div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["📊 PE Trends", "📊 PB Trends", "💰 Div Yield", "📈 ERP (India)"])
    
    with t1:
        fig = dual_line_chart(n50_df, mid_df, 'Date', 'PE', '📊 PE Ratio: Nifty 50 vs Midcap 100')
        st.plotly_chart(fig, use_container_width=True)
    
    with t2:
        fig = dual_line_chart(n50_df, mid_df, 'Date', 'PB', '📊 PB Ratio: Nifty 50 vs Midcap 100')
        st.plotly_chart(fig, use_container_width=True)
    
    with t3:
        fig = dual_line_chart(n50_df, mid_df, 'Date', 'DivYield', '💰 Dividend Yield: Nifty 50 vs Midcap 100')
        st.plotly_chart(fig, use_container_width=True)
    
    with t4:
        fig = dual_line_chart(n50_df, mid_df, 'Date', 'ERP', '📈 ERP (India-Calibrated): Nifty 50 vs Midcap 100')
        fig.add_hline(y=-2.5, line_dash="dash", line_color="#10b981", annotation_text="Very Cheap")
        fig.add_hline(y=-3.7, line_dash="dot", line_color="#f59e0b", annotation_text="Median")
        fig.add_hline(y=-4.5, line_dash="dash", line_color="#ef4444", annotation_text="V.Expensive")
        st.plotly_chart(fig, use_container_width=True)
    
    # ══════════════════════════════════════════════════════════════════════════
    # ROW 4: Recommendations
    # ══════════════════════════════════════════════════════════════════════════
    
    st.markdown('<div class="section-header">💡 Recommendations</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if n50_df is not None:
            if n50_sig_sc >= 0.5:
                st.markdown(f'<div class="info-box info-success"><strong>NIFTY 50: {n50_sig_txt}</strong><br>PE at {n50_latest.get("PE_Percentile",0):.0f}th percentile. Favorable for Large Cap allocation. Consider index funds/ETFs.</div>', unsafe_allow_html=True)
            elif n50_sig_sc <= -0.3:
                st.markdown(f'<div class="info-box info-danger"><strong>NIFTY 50: {n50_sig_txt}</strong><br>Valuations stretched. Consider profit booking on large cap positions.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="info-box info-warning"><strong>NIFTY 50: {n50_sig_txt}</strong><br>Valuations at fair levels. Continue regular SIPs in large cap funds.</div>', unsafe_allow_html=True)
    
    with col2:
        if mid_df is not None:
            if mid_sig_sc >= 0.5:
                st.markdown(f'<div class="info-box info-success"><strong>MIDCAP 100: {mid_sig_txt}</strong><br>PE at {mid_latest.get("PE_Percentile",0):.0f}th percentile. Good entry for midcap funds. Higher growth potential.</div>', unsafe_allow_html=True)
            elif mid_sig_sc <= -0.3:
                st.markdown(f'<div class="info-box info-danger"><strong>MIDCAP 100: {mid_sig_txt}</strong><br>Midcap valuations rich. Be selective, avoid aggressive midcap allocation.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="info-box info-warning"><strong>MIDCAP 100: {mid_sig_txt}</strong><br>Midcaps at fair value. Maintain existing allocation through SIPs.</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align:center;color:#64748b;font-size:0.8rem">
    🇮🇳 Pro Quant India Multi-Cap Dashboard | India-Calibrated Thresholds<br>
    <em>PE/PB/Div thresholds based on historical analysis (2016-2026)</em>
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
