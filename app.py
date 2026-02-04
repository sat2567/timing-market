"""
🇮🇳 PRO QUANT INDIA COMPLETE MARKET DASHBOARD
Multi-Cap Valuation + ERP + VIX + Technical Analysis
India-Calibrated • April 2021 Analysis Period

USAGE: streamlit run pro_quant_dashboard.py
REQUIREMENTS: pip install streamlit pandas numpy plotly yfinance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Pro Quant India", page_icon="🇮🇳", layout="wide", initial_sidebar_state="collapsed")

try:
    SCRIPT_DIR = Path(__file__).parent.resolve()
except:
    SCRIPT_DIR = Path.cwd()

ANALYSIS_START = '2021-04-01'

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&family=JetBrains+Mono&display=swap');
.stApp { background: linear-gradient(180deg, #0a0f1a 0%, #111827 100%); }
#MainMenu, footer, header {visibility: hidden;}
.main-title { font-family: 'Orbitron', monospace; font-size: 1.6rem; font-weight: 700; text-align: center; background: linear-gradient(90deg, #ff9933, #fff, #138808); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { color: #64748b; text-align: center; font-size: 0.75rem; margin-bottom: 0.5rem; }
.card { background: linear-gradient(135deg, #111827, #1f2937); border: 1px solid #1e3a5f; border-radius: 8px; padding: 0.6rem; margin: 0.2rem 0; }
.idx-header { font-family: 'Orbitron', monospace; font-size: 0.85rem; font-weight: 700; padding: 0.3rem 0.6rem; border-radius: 5px; text-align: center; margin-bottom: 0.4rem; }
.n50-hdr { background: #1e3a5f; color: #3b82f6; border: 1px solid #3b82f6; }
.mid-hdr { background: #3d1e5f; color: #8b5cf6; border: 1px solid #8b5cf6; }
.sml-hdr { background: #1e5f3d; color: #10b981; border: 1px solid #10b981; }
.metric-row { display: flex; justify-content: space-between; padding: 0.2rem 0; border-bottom: 1px solid #1e3a5f; font-size: 0.75rem; }
.metric-lbl { color: #64748b; }
.metric-val { font-family: 'JetBrains Mono', monospace; color: #e2e8f0; font-weight: 600; }
.pctl { font-size: 0.65rem; padding: 0.1rem 0.3rem; border-radius: 8px; }
.pctl-g { background: rgba(16,185,129,0.2); color: #10b981; }
.pctl-y { background: rgba(245,158,11,0.2); color: #f59e0b; }
.pctl-r { background: rgba(239,68,68,0.2); color: #ef4444; }
.signal { font-family: 'Orbitron', monospace; font-size: 0.7rem; font-weight: 700; padding: 0.3rem 0.6rem; border-radius: 5px; text-align: center; }
.sig-buy { background: linear-gradient(135deg, #059669, #10b981); color: white; }
.sig-hold { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }
.sig-trim { background: linear-gradient(135deg, #dc2626, #ef4444); color: white; }
.section { font-family: 'Orbitron', monospace; font-size: 0.85rem; color: #e2e8f0; padding: 0.4rem 0.6rem; margin: 0.6rem 0 0.4rem 0; background: linear-gradient(90deg, rgba(255,153,51,0.2), transparent); border-left: 3px solid #ff9933; border-radius: 0 5px 5px 0; }
.divider { height: 1px; background: linear-gradient(90deg, transparent, #ff9933, #138808, transparent); margin: 0.6rem 0; }
.info { border-radius: 5px; padding: 0.5rem; margin: 0.3rem 0; font-size: 0.75rem; }
.info-g { background: rgba(16,185,129,0.15); border-left: 3px solid #10b981; color: #e2e8f0; }
.info-y { background: rgba(245,158,11,0.15); border-left: 3px solid #f59e0b; color: #e2e8f0; }
.info-r { background: rgba(239,68,68,0.15); border-left: 3px solid #ef4444; color: #e2e8f0; }
[data-testid="stSidebar"] { background: #111827; }
.stTabs [data-baseweb="tab-list"] { background: #111827; padding: 3px; border-radius: 5px; }
.stTabs [data-baseweb="tab"] { font-size: 0.75rem; color: #64748b; }
.stTabs [aria-selected="true"] { background: #1e3a5f; color: #3b82f6 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

def find_file(names):
    for loc in [SCRIPT_DIR, Path.cwd(), SCRIPT_DIR/"data", Path.cwd()/"data"]:
        if loc.exists():
            for n in names:
                if (loc / n).exists(): return loc / n
    return None

@st.cache_data(ttl=3600)
def load_data():
    data = {}
    
    # Load PE/PB/Div data
    for key, names in [('n50', ['Nifty50_PE_PB_Div_Merged.csv']), 
                       ('mid', ['NiftyMidcap100_PE_PB_Div_Merged.csv']),
                       ('small', ['NiftySmallcap250_PE_PB_Div_Merged.csv'])]:
        path = find_file(names)
        if path:
            df = pd.read_csv(path)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df[df['Date'] >= ANALYSIS_START].copy()
            df = df.rename(columns={'PE': 'PE', 'PB': 'PB', 'DivYield': 'DivYield'})
            data[key] = df
    
    # Load G-Sec
    path = find_file(['Nifty_10Y_Benchmark_GSec_Merged.csv'])
    if path:
        gsec = pd.read_csv(path)
        gsec['Date'] = pd.to_datetime(gsec['Date'])
        gsec['GSec_Yield'] = 17 - (gsec['Close'] / 100)
        gsec = gsec[gsec['Date'] >= ANALYSIS_START][['Date', 'GSec_Yield']]
        data['gsec'] = gsec
    
    # Load VIX
    path = find_file(['India_VIX_Yahoo.csv'])
    if path:
        vix = pd.read_csv(path)
        vix['Date'] = pd.to_datetime(vix['Date'])
        vix = vix.rename(columns={'VIX_Close': 'VIX'})
        vix = vix[vix['Date'] >= ANALYSIS_START][['Date', 'VIX']]
        data['vix'] = vix
    
    return data

def process_data(data):
    processed = {}
    
    for key in ['n50', 'mid', 'small']:
        if key not in data: continue
        df = data[key].copy()
        
        # Merge G-Sec
        if 'gsec' in data:
            if key == 'mid':  # Monthly data
                gsec = data['gsec'].copy()
                gsec['YM'] = gsec['Date'].dt.to_period('M')
                gsec = gsec.groupby('YM')['GSec_Yield'].mean().reset_index()
                df['YM'] = df['Date'].dt.to_period('M')
                df = pd.merge(df, gsec, on='YM', how='left').drop('YM', axis=1)
            else:
                df = pd.merge(df, data['gsec'], on='Date', how='left')
        
        # Merge VIX (for N50 only)
        if key == 'n50' and 'vix' in data:
            df = pd.merge(df, data['vix'], on='Date', how='left')
        
        df = df.sort_values('Date').ffill().bfill()
        
        # Calculate ERP
        df['E_Yield'] = (1 / df['PE']) * 100
        df['ERP'] = df['E_Yield'] - df.get('GSec_Yield', 7.5)
        
        # Percentiles
        df['PE_Pctl'] = df['PE'].rank(pct=True) * 100
        df['PB_Pctl'] = df['PB'].rank(pct=True) * 100
        df['ERP_Pctl'] = df['ERP'].rank(pct=True) * 100
        
        processed[key] = df
    
    return processed

# ══════════════════════════════════════════════════════════════════════════════
# SIGNAL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def erp_signal(erp):
    if pd.isna(erp): return 'N/A', 0, 'pctl-y'
    if erp > -2.5: return 'V.CHEAP', 2, 'pctl-g'
    if erp > -3.2: return 'CHEAP', 1, 'pctl-g'
    if erp > -3.7: return 'FAIR', 0, 'pctl-y'
    if erp > -4.5: return 'EXPENSIVE', -1, 'pctl-r'
    return 'V.EXPENSIVE', -2, 'pctl-r'

def pctl_signal(pctl, inverted=False):
    if pd.isna(pctl): return 'N/A', 0, 'pctl-y'
    if inverted: pctl = 100 - pctl
    if pctl < 25: return 'CHEAP', 1, 'pctl-g'
    if pctl < 50: return 'FAIR-', 0.5, 'pctl-g'
    if pctl < 75: return 'FAIR+', -0.5, 'pctl-y'
    return 'EXPENSIVE', -1, 'pctl-r'

def composite_signal(pe_pctl, pb_pctl, erp_pctl):
    # Higher score = better value
    score = (100 - pe_pctl) * 0.40 + (100 - pb_pctl) * 0.30 + erp_pctl * 0.30
    if score >= 60: return 'BUY', score, 'sig-buy'
    if score >= 45: return 'ACCUMULATE', score, 'sig-buy'
    if score >= 35: return 'HOLD', score, 'sig-hold'
    return 'TRIM', score, 'sig-trim'

def vix_signal(vix):
    if pd.isna(vix): return 'N/A', 0, 'pctl-y'
    if vix > 30: return 'PANIC', 2, 'pctl-g'
    if vix > 25: return 'FEAR', 1.5, 'pctl-g'
    if vix > 20: return 'ELEVATED', 1, 'pctl-y'
    if vix > 15: return 'NORMAL', 0, 'pctl-y'
    if vix > 12: return 'CALM', -0.5, 'pctl-y'
    return 'COMPLACENT', -1, 'pctl-r'

# ══════════════════════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def comparison_chart(data, metric, title):
    fig = go.Figure()
    colors = {'n50': '#3b82f6', 'mid': '#8b5cf6', 'small': '#10b981'}
    names = {'n50': 'Nifty 50', 'mid': 'Midcap 100', 'small': 'Smallcap 250'}
    
    for key in ['n50', 'mid', 'small']:
        if key in data and metric in data[key].columns:
            df = data[key].dropna(subset=[metric])
            fig.add_trace(go.Scatter(x=df['Date'], y=df[metric], name=names[key], line=dict(color=colors[key], width=2)))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=12, color='#e2e8f0'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0', size=9),
        xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'),
        legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center', font=dict(size=9)),
        height=280, margin=dict(l=40, r=20, t=40, b=30), hovermode='x unified'
    )
    return fig

def erp_chart(data):
    fig = go.Figure()
    colors = {'n50': '#3b82f6', 'mid': '#8b5cf6', 'small': '#10b981'}
    names = {'n50': 'Nifty 50', 'mid': 'Midcap 100', 'small': 'Smallcap 250'}
    
    # Add zones
    fig.add_hrect(y0=-6, y1=-4.5, fillcolor="rgba(239,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=-4.5, y1=-3.7, fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hrect(y0=-3.7, y1=-2.5, fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hrect(y0=-2.5, y1=0, fillcolor="rgba(16,185,129,0.1)", line_width=0)
    
    for key in ['n50', 'mid', 'small']:
        if key in data and 'ERP' in data[key].columns:
            df = data[key].dropna(subset=['ERP'])
            fig.add_trace(go.Scatter(x=df['Date'], y=df['ERP'], name=names[key], line=dict(color=colors[key], width=2)))
    
    fig.add_hline(y=-2.5, line_dash="dash", line_color="#10b981", line_width=1)
    fig.add_hline(y=-3.7, line_dash="dot", line_color="#f59e0b", line_width=1)
    fig.add_hline(y=-4.5, line_dash="dash", line_color="#ef4444", line_width=1)
    
    fig.update_layout(
        title=dict(text='📈 ERP (India-Calibrated)', font=dict(size=12, color='#e2e8f0'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0', size=9),
        xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f', title='ERP %', range=[-6, 0]),
        legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center', font=dict(size=9)),
        height=300, margin=dict(l=50, r=20, t=40, b=30)
    )
    return fig

def pctl_bars(n50_val, mid_val, small_val, title):
    fig = go.Figure()
    indices = ['Smallcap', 'Midcap', 'Nifty 50']
    values = [small_val, mid_val, n50_val]
    colors = ['#10b981' if v <= 40 else '#ef4444' if v >= 60 else '#f59e0b' for v in values]
    
    fig.add_trace(go.Bar(y=indices, x=values, orientation='h', marker_color=colors,
                         text=[f'{v:.0f}%' for v in values], textposition='outside', textfont=dict(size=10)))
    fig.add_vline(x=30, line_dash="dash", line_color="#10b981", line_width=1)
    fig.add_vline(x=70, line_dash="dash", line_color="#ef4444", line_width=1)
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=11, color='#e2e8f0'), x=0.5),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.8)',
        font=dict(color='#e2e8f0', size=9),
        xaxis=dict(gridcolor='#1e3a5f', range=[0, 100]), yaxis=dict(gridcolor='#1e3a5f'),
        height=180, margin=dict(l=70, r=40, t=35, b=25), showlegend=False
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown('<h1 class="main-title">🇮🇳 INDIA MULTI-CAP VALUATION DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Nifty 50 • Midcap 100 • Smallcap 250 | ERP • PE • PB • VIX | April 2021 Analysis</p>', unsafe_allow_html=True)
    
    # Load data
    raw_data = load_data()
    data = process_data(raw_data)
    
    if not data:
        st.error("No data found!")
        return
    
    # Get latest values
    latest = {k: v.dropna(subset=['PE']).iloc[-1] for k, v in data.items()}
    
    # Calculate signals
    signals = {}
    for key in latest:
        l = latest[key]
        pe_sig, pe_sc, pe_cls = pctl_signal(l['PE_Pctl'])
        pb_sig, pb_sc, pb_cls = pctl_signal(l['PB_Pctl'])
        erp_sig_txt, erp_sc, erp_cls = erp_signal(l.get('ERP', -3.7))
        comp_txt, comp_sc, comp_cls = composite_signal(l['PE_Pctl'], l['PB_Pctl'], l.get('ERP_Pctl', 50))
        signals[key] = {'pe': (pe_sig, pe_cls), 'pb': (pb_sig, pb_cls), 'erp': (erp_sig_txt, erp_cls), 
                       'comp': (comp_txt, comp_sc, comp_cls)}
    
    # VIX signal (from N50)
    vix_val = latest.get('n50', {}).get('VIX', 15) if 'n50' in latest else 15
    vix_txt, vix_sc, vix_cls = vix_signal(vix_val)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # ══════════════════════════════════════════════════════════════════════════
    # ROW 1: Three Index Cards
    # ══════════════════════════════════════════════════════════════════════════
    
    c1, c2, c3 = st.columns(3)
    
    for col, key, hdr_cls, name in [(c1, 'n50', 'n50-hdr', 'NIFTY 50'), 
                                     (c2, 'mid', 'mid-hdr', 'MIDCAP 100'),
                                     (c3, 'small', 'sml-hdr', 'SMALLCAP 250')]:
        with col:
            if key in latest:
                l = latest[key]
                s = signals[key]
                
                st.markdown(f'<div class="idx-header {hdr_cls}">{name}</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                
                st.markdown(f'''
                <div class="metric-row"><span class="metric-lbl">PE</span>
                <span><span class="metric-val">{l["PE"]:.1f}</span> <span class="pctl {s["pe"][1]}">{l["PE_Pctl"]:.0f}%</span></span></div>
                <div class="metric-row"><span class="metric-lbl">PB</span>
                <span><span class="metric-val">{l["PB"]:.2f}</span> <span class="pctl {s["pb"][1]}">{l["PB_Pctl"]:.0f}%</span></span></div>
                <div class="metric-row"><span class="metric-lbl">Div%</span>
                <span class="metric-val">{l["DivYield"]:.2f}%</span></div>
                <div class="metric-row"><span class="metric-lbl">ERP</span>
                <span><span class="metric-val">{l.get("ERP", 0):.2f}%</span> <span class="pctl {s["erp"][1]}">{s["erp"][0]}</span></span></div>
                <div style="margin-top:0.4rem;text-align:center"><div class="signal {s["comp"][2]}">{s["comp"][0]} ({s["comp"][1]:.0f})</div></div>
                ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # ══════════════════════════════════════════════════════════════════════════
    # ROW 2: VIX + Percentile Bars
    # ══════════════════════════════════════════════════════════════════════════
    
    st.markdown('<div class="section">📊 Percentile Comparison (Lower = Cheaper)</div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    
    with c1:
        # VIX Card
        st.markdown(f'''
        <div class="card" style="text-align:center">
            <div style="color:#64748b;font-size:0.7rem">INDIA VIX</div>
            <div style="font-family:'Orbitron';font-size:1.4rem;color:#e2e8f0">{vix_val:.1f}</div>
            <div class="pctl {vix_cls}" style="display:inline-block">{vix_txt}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with c2:
        if all(k in latest for k in ['n50', 'mid', 'small']):
            fig = pctl_bars(latest['n50']['PE_Pctl'], latest['mid']['PE_Pctl'], latest['small']['PE_Pctl'], 'PE Percentile')
            st.plotly_chart(fig, use_container_width=True)
    
    with c3:
        if all(k in latest for k in ['n50', 'mid', 'small']):
            fig = pctl_bars(latest['n50']['PB_Pctl'], latest['mid']['PB_Pctl'], latest['small']['PB_Pctl'], 'PB Percentile')
            st.plotly_chart(fig, use_container_width=True)
    
    with c4:
        if all(k in latest for k in ['n50', 'mid', 'small']):
            fig = pctl_bars(latest['n50'].get('ERP_Pctl', 50), latest['mid'].get('ERP_Pctl', 50), 
                           latest['small'].get('ERP_Pctl', 50), 'ERP Percentile (Higher=Better)')
            st.plotly_chart(fig, use_container_width=True)
    
    # ══════════════════════════════════════════════════════════════════════════
    # ROW 3: Recommendation
    # ══════════════════════════════════════════════════════════════════════════
    
    # Find best value
    comp_scores = {k: signals[k]['comp'][1] for k in signals}
    best = max(comp_scores, key=comp_scores.get)
    names = {'n50': 'Nifty 50', 'mid': 'Midcap 100', 'small': 'Smallcap 250'}
    ranked = sorted(comp_scores.items(), key=lambda x: x[1], reverse=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'''
        <div class="info info-g">
            <strong>🏆 Best Value: {names[best]}</strong> (Score: {comp_scores[best]:.0f})<br>
            Consider overweighting this segment.
        </div>
        ''', unsafe_allow_html=True)
    
    with c2:
        st.markdown(f'''
        <div class="info info-y">
            <strong>📊 Ranking:</strong> 1. {names[ranked[0][0]]} ({ranked[0][1]:.0f}) • 
            2. {names[ranked[1][0]]} ({ranked[1][1]:.0f}) • 3. {names[ranked[2][0]]} ({ranked[2][1]:.0f})
        </div>
        ''', unsafe_allow_html=True)
    
    # ══════════════════════════════════════════════════════════════════════════
    # ROW 4: Charts
    # ══════════════════════════════════════════════════════════════════════════
    
    st.markdown('<div class="section">📈 Historical Analysis (April 2021 - Present)</div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["ERP", "PE", "PB", "Div Yield"])
    
    with t1:
        st.plotly_chart(erp_chart(data), use_container_width=True)
        st.markdown('''
        <div class="info info-y" style="font-size:0.7rem">
            <strong>India ERP is structurally negative:</strong> G-Sec yields (6-8%) exceed earnings yields (3-5%).
            Thresholds: > -2.5% Very Cheap | -3.7% Fair | < -4.5% Very Expensive
        </div>
        ''', unsafe_allow_html=True)
    
    with t2:
        st.plotly_chart(comparison_chart(data, 'PE', '📊 PE Ratio'), use_container_width=True)
    
    with t3:
        st.plotly_chart(comparison_chart(data, 'PB', '📊 PB Ratio'), use_container_width=True)
    
    with t4:
        st.plotly_chart(comparison_chart(data, 'DivYield', '💰 Dividend Yield %'), use_container_width=True)
    
    # Footer
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('''
    <p style="text-align:center;color:#64748b;font-size:0.7rem">
    🇮🇳 Pro Quant India Dashboard | Composite = (100-PE_Pctl)×40% + (100-PB_Pctl)×30% + ERP_Pctl×30%
    </p>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
