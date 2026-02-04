"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 PRO QUANT MARKET TIMING DASHBOARD                      ║
║                                                                              ║
║  USAGE:  streamlit run pro_quant_dashboard.py                                ║
║  REQUIREMENTS: pip install streamlit pandas numpy plotly                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Pro Quant Dashboard", page_icon="📈", layout="wide")

# Get script directory
try:
    SCRIPT_DIR = Path(__file__).parent.resolve()
except:
    SCRIPT_DIR = Path.cwd()

# ══════════════════════════════════════════════════════════════════════════════
# CSS STYLES
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

.stApp { background: linear-gradient(180deg, #0a0f1a 0%, #111827 100%); }
#MainMenu, footer, header {visibility: hidden;}

.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.5rem;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #10b981, #06b6d4, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 1rem 0;
}

.subtitle {
    font-family: 'Rajdhani', sans-serif;
    color: #64748b;
    text-align: center;
    letter-spacing: 3px;
    margin-bottom: 1.5rem;
}

.metric-card {
    background: linear-gradient(135deg, #111827, #1f2937);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
}

.metric-card::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #10b981, #3b82f6);
    margin: -1.5rem -1.5rem 1rem -1.5rem;
    border-radius: 16px 16px 0 0;
}

.metric-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0.5rem 0;
}

.metric-delta {
    font-size: 0.85rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    display: inline-block;
}

.delta-positive { background: rgba(16,185,129,0.2); color: #10b981; }
.delta-negative { background: rgba(239,68,68,0.2); color: #ef4444; }
.delta-neutral { background: rgba(245,158,11,0.2); color: #f59e0b; }

.signal-badge {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    display: inline-block;
}

.signal-buy { background: linear-gradient(135deg, #059669, #10b981); color: white; box-shadow: 0 0 20px rgba(16,185,129,0.5); }
.signal-sell { background: linear-gradient(135deg, #dc2626, #ef4444); color: white; box-shadow: 0 0 20px rgba(239,68,68,0.5); }
.signal-hold { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }
.signal-trim { background: linear-gradient(135deg, #ea580c, #f97316); color: white; }

.regime-banner {
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    padding: 1.25rem;
    border-radius: 12px;
    text-align: center;
    margin: 1rem 0;
}

.regime-bull { background: linear-gradient(135deg, #064e3b, #065f46); border: 2px solid #10b981; color: #10b981; }
.regime-bear { background: linear-gradient(135deg, #450a0a, #7f1d1d); border: 2px solid #ef4444; color: #ef4444; }
.regime-neutral { background: linear-gradient(135deg, #451a03, #78350f); border: 2px solid #f59e0b; color: #f59e0b; }

.info-box { border-radius: 10px; padding: 1rem; margin: 0.75rem 0; }
.info-success { background: linear-gradient(135deg, #064e3b, #111827); border-left: 4px solid #10b981; color: #e2e8f0; }
.info-warning { background: linear-gradient(135deg, #451a03, #111827); border-left: 4px solid #f59e0b; color: #e2e8f0; }
.info-danger { background: linear-gradient(135deg, #450a0a, #111827); border-left: 4px solid #ef4444; color: #e2e8f0; }

.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    color: #e2e8f0;
    padding: 0.75rem 1rem;
    margin: 1.5rem 0 1rem 0;
    background: linear-gradient(90deg, rgba(59,130,246,0.2), transparent);
    border-left: 4px solid #3b82f6;
    border-radius: 0 8px 8px 0;
}

.divider { height: 1px; background: linear-gradient(90deg, transparent, #3b82f6, transparent); margin: 1.5rem 0; }

[data-testid="stSidebar"] { background: linear-gradient(180deg, #111827, #0a0f1a); }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING - ROBUST FILE FINDER
# ══════════════════════════════════════════════════════════════════════════════

def find_file(possible_names):
    """Search for file in multiple locations"""
    locations = [SCRIPT_DIR, Path.cwd(), SCRIPT_DIR/"data", Path.cwd()/"data"]
    for loc in locations:
        if loc.exists():
            for name in possible_names:
                path = loc / name
                if path.exists():
                    return path
    return None

@st.cache_data(ttl=3600)
def load_data():
    """Load all market data"""
    data, status = {}, {}
    
    configs = {
        'nifty50': ['Nifty50_Historical_Yahoo.csv', 'nifty50_historical_yahoo.csv', 'Nifty50.csv'],
        'vix': ['India_VIX_Yahoo.csv', 'india_vix_yahoo.csv', 'VIX.csv'],
        'pe_data': ['Nifty_Index_Valuation_History.csv', 'PE_Data.csv'],
        'gsec': ['Nifty_10Y_Benchmark_GSec_Merged.csv', 'GSec.csv'],
        'midcap': ['NIFTY_MIDCAP_100_Historical_Yahoo.csv', 'Midcap100.csv']
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
    if not raw.get('nifty50') is not None:
        return None, None
    
    # Daily data
    df = raw['nifty50'][['Date', 'Close']].copy()
    df.columns = ['Date', 'Nifty50']
    
    # Add VIX
    if raw.get('vix') is not None:
        vix = raw['vix'].copy()
        col = 'VIX_Close' if 'VIX_Close' in vix.columns else 'Close'
        if col in vix.columns:
            vix_df = vix[['Date', col]].copy()
            vix_df.columns = ['Date', 'VIX']
            df = pd.merge(df, vix_df, on='Date', how='left')
    if 'VIX' not in df.columns:
        df['VIX'] = 15.0
    
    # Add GSec
    if raw.get('gsec') is not None:
        gsec = raw['gsec'][['Date', 'Close']].copy()
        gsec['GSec_Yield'] = 17 - (gsec['Close'] / 100)
        df = pd.merge(df, gsec[['Date', 'GSec_Yield']], on='Date', how='left')
    if 'GSec_Yield' not in df.columns:
        df['GSec_Yield'] = 7.5
    
    df = df.sort_values('Date').ffill().bfill()
    df['ATH'] = df['Nifty50'].expanding().max()
    df['Drawdown'] = ((df['Nifty50'] / df['ATH']) - 1) * 100
    
    # Monthly
    monthly = df.groupby(df['Date'].dt.to_period('M')).agg({
        'Nifty50': 'last', 'VIX': 'mean', 'GSec_Yield': 'last', 'Drawdown': 'last'
    }).reset_index()
    monthly['Date'] = monthly['Date'].dt.to_timestamp() + pd.offsets.MonthEnd(0)
    
    # Add PE
    if raw.get('pe_data') is not None:
        pe = raw['pe_data']
        for idx, col in [('Nifty 50', 'Nifty50_PE'), ('Nifty Midcap 100', 'Midcap_PE'), ('Nifty Smallcap 100', 'Smallcap_PE')]:
            sub = pe[pe['Index'] == idx][['Date', 'PE_Ratio']].copy()
            sub['Date'] = pd.to_datetime(sub['Date']) + pd.offsets.MonthEnd(0)
            sub.columns = ['Date', col]
            monthly = pd.merge(monthly, sub, on='Date', how='left')
    
    for col, val in [('Nifty50_PE', 22), ('Midcap_PE', 28), ('Smallcap_PE', 25)]:
        if col not in monthly.columns:
            monthly[col] = val
        monthly[col] = monthly[col].fillna(val)
    
    monthly['Earnings_Yield'] = (1 / monthly['Nifty50_PE']) * 100
    monthly['ERP'] = monthly['Earnings_Yield'] - monthly['GSec_Yield']
    monthly['Nifty50_PE_Pct'] = monthly['Nifty50_PE'].rank(pct=True) * 100
    monthly['Midcap_PE_Pct'] = monthly['Midcap_PE'].rank(pct=True) * 100
    monthly['Smallcap_PE_Pct'] = monthly['Smallcap_PE'].rank(pct=True) * 100
    
    return df, monthly

# ══════════════════════════════════════════════════════════════════════════════
# SIGNALS
# ══════════════════════════════════════════════════════════════════════════════

def erp_signal(erp):
    if pd.isna(erp): return 'NO DATA', 0, '#64748b'
    if erp > 3: return 'VERY CHEAP', 2, '#10b981'
    if erp > 1.5: return 'CHEAP', 1, '#34d399'
    if erp > 0: return 'FAIR', 0, '#f59e0b'
    if erp > -1.5: return 'EXPENSIVE', -1, '#f97316'
    return 'VERY EXPENSIVE', -2, '#ef4444'

def vix_signal(vix):
    if pd.isna(vix): return 'NO DATA', 0, '#64748b'
    if vix > 30: return 'EXTREME FEAR', 2, '#10b981'
    if vix > 25: return 'HIGH FEAR', 1.5, '#34d399'
    if vix > 20: return 'FEAR', 1, '#84cc16'
    if vix > 15: return 'ELEVATED', 0.5, '#f59e0b'
    if vix > 12: return 'NORMAL', 0, '#64748b'
    return 'COMPLACENCY', -1, '#ef4444'

def composite_signal(erp_s, vix_s, pe_pct):
    pe_s = 2 if pe_pct < 20 else 1 if pe_pct < 40 else 0 if pe_pct < 60 else -1 if pe_pct < 80 else -2
    comp = erp_s * 0.35 + vix_s * 0.35 + pe_s * 0.30
    if comp >= 1.5: return 'AGGRESSIVE BUY', comp, 'signal-buy'
    if comp >= 0.75: return 'BUY', comp, 'signal-buy'
    if comp >= 0.25: return 'ACCUMULATE', comp, 'signal-hold'
    if comp >= -0.25: return 'HOLD', comp, 'signal-hold'
    if comp >= -0.75: return 'TRIM', comp, 'signal-trim'
    if comp >= -1.25: return 'REDUCE', comp, 'signal-sell'
    return 'SELL', comp, 'signal-sell'

def market_regime(vix, erp_s, dd):
    vix = 15 if pd.isna(vix) else vix
    dd = 0 if pd.isna(dd) else dd
    if erp_s >= 1 and vix > 25 and dd < -15: return '🎯 IDEAL BOTTOM', 'regime-bull'
    if vix > 30 and dd < -20: return '📉 CRASH MODE', 'regime-bear'
    if vix < 15 and dd > -5: return '🚀 BULL RUN', 'regime-bull'
    if vix < 12 and erp_s <= -1: return '⚠️ MARKET TOP', 'regime-bear'
    if -20 < dd < -10: return '📈 RECOVERY', 'regime-neutral'
    return '↔️ TRANSITIONAL', 'regime-neutral'

# ══════════════════════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════════════════════

def gauge_chart(val, title, lo, hi, thresh, colors):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=val,
        title={'text': title, 'font': {'size': 14, 'color': '#e2e8f0'}},
        number={'font': {'size': 28, 'color': '#e2e8f0'}},
        gauge={
            'axis': {'range': [lo, hi], 'tickcolor': '#64748b'},
            'bar': {'color': '#3b82f6', 'thickness': 0.3},
            'bgcolor': '#1f2937', 'borderwidth': 2, 'bordercolor': '#1e3a5f',
            'steps': [{'range': [thresh[i], thresh[i+1]], 'color': colors[i]} for i in range(len(thresh)-1)],
            'threshold': {'line': {'color': '#fff', 'width': 3}, 'thickness': 0.8, 'value': val}
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20,r=20,t=40,b=20))
    return fig

def line_chart(df, x, ys, title, colors=None):
    colors = colors or ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
    fig = go.Figure()
    for i, y in enumerate(ys):
        if y in df.columns:
            fig.add_trace(go.Scatter(x=df[x], y=df[y], name=y.replace('_',' '), line=dict(color=colors[i%len(colors)], width=2)))
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#e2e8f0'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0'), xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'),
        legend=dict(bgcolor='rgba(17,24,39,0.9)', orientation='h', y=1.1, x=0.5, xanchor='center'),
        height=380, margin=dict(l=50,r=30,t=60,b=40)
    )
    return fig

def vix_chart(df):
    fig = go.Figure()
    fig.add_hrect(y0=0, y1=12, fillcolor="rgba(239,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=12, y1=20, fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hrect(y0=20, y1=50, fillcolor="rgba(16,185,129,0.1)", line_width=0)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['VIX'], line=dict(color='#8b5cf6', width=2), fill='tozeroy', fillcolor='rgba(139,92,246,0.2)'))
    fig.add_hline(y=12, line_dash="dash", line_color="#ef4444")
    fig.add_hline(y=20, line_dash="dash", line_color="#f59e0b")
    fig.update_layout(title=dict(text='📊 VIX - Fear & Greed', font=dict(size=16, color='#e2e8f0'), x=0.5),
                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
                     xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f', title='VIX'),
                     showlegend=False, height=380)
    return fig

def erp_chart(df):
    fig = go.Figure()
    fig.add_hrect(y0=-10, y1=0, fillcolor="rgba(239,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=0, y1=10, fillcolor="rgba(16,185,129,0.1)", line_width=0)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['ERP'], line=dict(color='#06b6d4', width=2), fill='tozeroy', fillcolor='rgba(6,182,212,0.2)'))
    fig.add_hline(y=0, line_color="#fff", line_width=2)
    fig.add_hline(y=1.5, line_dash="dash", line_color="#10b981")
    fig.add_hline(y=-1.5, line_dash="dash", line_color="#ef4444")
    fig.update_layout(title=dict(text='📈 Equity Risk Premium', font=dict(size=16, color='#e2e8f0'), x=0.5),
                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
                     xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f', title='ERP %'),
                     showlegend=False, height=380)
    return fig

def multicap_chart(latest):
    caps = ['Large Cap', 'Mid Cap', 'Small Cap']
    pcts = [latest.get('Nifty50_PE_Pct', 50), latest.get('Midcap_PE_Pct', 50), latest.get('Smallcap_PE_Pct', 50)]
    pes = [latest.get('Nifty50_PE', 22), latest.get('Midcap_PE', 28), latest.get('Smallcap_PE', 25)]
    colors = ['#10b981' if p < 40 else '#ef4444' if p > 60 else '#f59e0b' for p in pcts]
    fig = go.Figure(go.Bar(x=caps, y=pcts, marker_color=colors,
                          text=[f'{p:.0f}%<br>PE:{pe:.1f}' for p,pe in zip(pcts,pes)],
                          textposition='outside', textfont=dict(color='#e2e8f0')))
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981")
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444")
    fig.update_layout(title=dict(text='🏛️ Multi-Cap Valuation', font=dict(size=16, color='#e2e8f0'), x=0.5),
                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
                     xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f', title='Percentile', range=[0,100]),
                     showlegend=False, height=380)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown('<h1 class="main-title">PRO QUANT DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Market Timing & Valuation Intelligence</p>', unsafe_allow_html=True)
    
    # Load data
    raw, status = load_data()
    daily, monthly = process_data(raw)
    
    # Sidebar - file status
    with st.sidebar:
        st.markdown("## 📁 Data Status")
        for k, v in status.items():
            st.markdown(f"**{k}:** {v}")
        st.markdown("---")
        st.markdown(f"📂 Script: `{SCRIPT_DIR}`")
        st.markdown(f"📂 CWD: `{Path.cwd()}`")
        
        # List CSV files
        st.markdown("### 📄 CSV Files Found:")
        csvs = list(SCRIPT_DIR.glob("*.csv")) + list(Path.cwd().glob("*.csv"))
        csvs = list(set(csvs))
        if csvs:
            for f in csvs[:10]:
                st.text(f"• {f.name}")
        else:
            st.text("No CSV files found")
    
    # Check if data loaded
    if monthly is None:
        st.error("⚠️ Could not load data!")
        st.markdown("""
        ### Required Files (place in same folder as script):
        1. `Nifty50_Historical_Yahoo.csv`
        2. `India_VIX_Yahoo.csv`  
        3. `Nifty_Index_Valuation_History.csv`
        4. `Nifty_10Y_Benchmark_GSec_Merged.csv`
        """)
        
        if st.button("🎮 Run Demo Mode"):
            st.session_state['demo'] = True
            st.rerun()
        
        if st.session_state.get('demo'):
            np.random.seed(42)
            dates = pd.date_range('2018-01-01', '2026-01-31', freq='M')
            monthly = pd.DataFrame({
                'Date': dates,
                'Nifty50': np.cumsum(np.random.randn(len(dates))*500) + 10000 + np.arange(len(dates))*100,
                'Nifty50_PE': np.random.uniform(18, 32, len(dates)),
                'Midcap_PE': np.random.uniform(22, 40, len(dates)),
                'Smallcap_PE': np.random.uniform(20, 38, len(dates)),
                'VIX': np.random.uniform(10, 30, len(dates)),
                'GSec_Yield': np.random.uniform(6.5, 8.5, len(dates)),
                'Drawdown': np.random.uniform(-15, 0, len(dates))
            })
            monthly['Earnings_Yield'] = (1/monthly['Nifty50_PE'])*100
            monthly['ERP'] = monthly['Earnings_Yield'] - monthly['GSec_Yield']
            monthly['Nifty50_PE_Pct'] = monthly['Nifty50_PE'].rank(pct=True)*100
            monthly['Midcap_PE_Pct'] = monthly['Midcap_PE'].rank(pct=True)*100
            monthly['Smallcap_PE_Pct'] = monthly['Smallcap_PE'].rank(pct=True)*100
            st.info("🎮 Running in Demo Mode")
        else:
            return
    
    # Get latest
    latest = monthly.iloc[-1]
    
    # Calculate signals
    erp_txt, erp_sc, erp_col = erp_signal(latest.get('ERP', 0))
    vix_txt, vix_sc, vix_col = vix_signal(latest.get('VIX', 15))
    sig_txt, sig_sc, sig_cls = composite_signal(erp_sc, vix_sc, latest.get('Nifty50_PE_Pct', 50))
    reg_txt, reg_cls = market_regime(latest.get('VIX', 15), erp_sc, latest.get('Drawdown', 0))
    
    # Sidebar metrics
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 📊 Quick Stats")
        st.metric("Nifty 50", f"{latest['Nifty50']:,.0f}", f"{latest.get('Drawdown',0):.1f}% from ATH")
        st.metric("VIX", f"{latest.get('VIX',0):.2f}", vix_txt)
        st.metric("G-Sec Yield", f"{latest.get('GSec_Yield',0):.2f}%")
    
    # Main content
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Row 1: Metrics
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        pe = latest.get('Nifty50_PE', 22)
        pct = latest.get('Nifty50_PE_Pct', 50)
        dcls = 'delta-positive' if pct < 40 else 'delta-negative' if pct > 60 else 'delta-neutral'
        st.markdown(f'<div class="metric-card"><div class="metric-label">Nifty 50 PE</div><div class="metric-value">{pe:.2f}</div><div class="metric-delta {dcls}">{pct:.0f}th Percentile</div></div>', unsafe_allow_html=True)
    
    with c2:
        erp = latest.get('ERP', 0)
        dcls = 'delta-positive' if erp_sc > 0 else 'delta-negative'
        st.markdown(f'<div class="metric-card"><div class="metric-label">Equity Risk Premium</div><div class="metric-value" style="color:{erp_col}">{erp:.2f}%</div><div class="metric-delta {dcls}">{erp_txt}</div></div>', unsafe_allow_html=True)
    
    with c3:
        vix = latest.get('VIX', 15)
        dcls = 'delta-positive' if vix_sc > 0 else 'delta-negative' if vix_sc < 0 else 'delta-neutral'
        st.markdown(f'<div class="metric-card"><div class="metric-label">India VIX</div><div class="metric-value" style="color:{vix_col}">{vix:.2f}</div><div class="metric-delta {dcls}">{vix_txt}</div></div>', unsafe_allow_html=True)
    
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Final Signal</div><div style="text-align:center;padding:0.5rem"><div class="signal-badge {sig_cls}">{sig_txt}</div></div><div class="metric-delta delta-neutral">Score: {sig_sc:.2f}</div></div>', unsafe_allow_html=True)
    
    # Row 2: Regime + Gauges
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown(f'<div class="regime-banner {reg_cls}">{reg_txt}</div>', unsafe_allow_html=True)
        if sig_sc >= 0.5:
            st.markdown('<div class="info-box info-success"><strong>💡 Recommendation:</strong><br>Favorable for accumulation. Consider increasing SIPs.</div>', unsafe_allow_html=True)
        elif sig_sc <= -0.5:
            st.markdown('<div class="info-box info-danger"><strong>⚠️ Warning:</strong><br>Elevated valuations. Consider profit booking.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box info-warning"><strong>📊 Observation:</strong><br>Mixed signals. Maintain current allocation.</div>', unsafe_allow_html=True)
    
    with c2:
        g1, g2, g3 = st.columns(3)
        with g1:
            st.plotly_chart(gauge_chart(latest.get('Nifty50_PE',22), "PE", 15, 40, [15,20,25,30,35,40], ['#059669','#10b981','#f59e0b','#f97316','#ef4444']), use_container_width=True)
        with g2:
            st.plotly_chart(gauge_chart(latest.get('VIX',15), "VIX", 8, 40, [8,12,18,25,32,40], ['#ef4444','#f97316','#f59e0b','#10b981','#059669']), use_container_width=True)
        with g3:
            st.plotly_chart(gauge_chart(latest.get('ERP',-2), "ERP%", -6, 4, [-6,-3,0,1.5,3,4], ['#ef4444','#f97316','#f59e0b','#10b981','#059669']), use_container_width=True)
    
    # Row 3: Charts
    st.markdown('<div class="section-header">📈 Historical Analysis</div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["💰 Valuations", "😱 VIX", "📊 ERP", "🏛️ Multi-Cap"])
    
    with t1:
        st.plotly_chart(line_chart(monthly, 'Date', ['Nifty50_PE','Midcap_PE','Smallcap_PE'], '📊 PE Trends'), use_container_width=True)
    with t2:
        st.plotly_chart(vix_chart(monthly), use_container_width=True)
    with t3:
        st.plotly_chart(erp_chart(monthly), use_container_width=True)
    with t4:
        st.plotly_chart(multicap_chart(latest), use_container_width=True)
    
    # Row 4: Table
    st.markdown('<div class="section-header">📋 Signal History</div>', unsafe_allow_html=True)
    
    disp = monthly.tail(12).copy()
    disp['Month'] = disp['Date'].dt.strftime('%Y-%m')
    disp['ERP_Signal'] = disp['ERP'].apply(lambda x: erp_signal(x)[0])
    disp['VIX_Signal'] = disp['VIX'].apply(lambda x: vix_signal(x)[0])
    cols = ['Month', 'Nifty50', 'Nifty50_PE', 'VIX', 'ERP', 'ERP_Signal', 'VIX_Signal']
    disp = disp[[c for c in cols if c in disp.columns]]
    for c in ['Nifty50', 'Nifty50_PE', 'VIX', 'ERP']:
        if c in disp.columns:
            disp[c] = disp[c].round(2)
    
    st.dataframe(disp, use_container_width=True, height=400, hide_index=True)
    
    # Footer
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#64748b">🚀 Pro Quant Dashboard | Built with Streamlit</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
