import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from market_timing_fetcher import MarketTimingDataFetcher

# Config
st.set_page_config(page_title="Market Timing Alpha", page_icon="📈", layout="wide")

# Styling
st.markdown("""<style>.metric-card {background-color: #f0f2f6; border-radius: 10px; padding: 15px;}</style>""", unsafe_allow_html=True)

# Data Loading
@st.cache_data(ttl=3600)
def load_data():
    return MarketTimingDataFetcher().fetch_all_data()

try:
    with st.spinner('Analyzing Markets...'):
        data = load_data()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# Helpers
signals = data.get('signals', {})
indian = data.get('indian_market', {})
global_m = data.get('global_market', {})

# --- UI ---
st.title("📈 Market Timing Dashboard")
st.caption(f"Last Updated: {data['metadata']['fetch_timestamp'][:16].replace('T', ' ')}")
st.markdown("---")

# Metrics
k1, k2, k3, k4 = st.columns(4)
k1.metric("🇮🇳 Nifty PE", f"{indian['nifty_valuation'].get('nifty_pe')}", indian['nifty_valuation'].get('pe_zone'))
k2.metric("📉 India VIX", f"{indian['india_vix'].get('india_vix')}", indian['india_vix'].get('vix_signal'))
k3.metric("💵 DXY", f"{global_m.get('dollar_index', {}).get('dxy', 'N/A')}")
k4.metric("🥇 Gold ($)", f"{global_m.get('gold', {}).get('gold_usd', 'N/A')}")

st.markdown("---")

# Gauge & Recommendation
col1, col2 = st.columns([1, 2])
with col1:
    score = signals.get('composite_score', 50)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "Composite Score"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "#ff4b4b"},
                {'range': [30, 70], 'color': "#ffa421"},
                {'range': [70, 100], 'color': "#00c853"}
            ]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(f"Recommendation: {signals.get('recommendation')}")
    st.info(f"**Suggested Equity Allocation:** {signals.get('suggested_equity_allocation')}")
    
    # Nifty Trend Status
    nifty = indian.get('nifty_50', {})
    if nifty.get('above_200dma'):
        st.success(f"✅ Nifty ({nifty.get('price')}) is trading ABOVE 200 DMA ({nifty.get('dma_200')})")
    else:
        st.error(f"❌ Nifty ({nifty.get('price')}) is trading BELOW 200 DMA ({nifty.get('dma_200')})")

# Tabs
t1, t2 = st.tabs(["🇮🇳 Indian Details", "🌍 Global Macros"])
with t1:
    st.write("### Valuation & Volatility")
    st.json(indian)
with t2:
    st.write("### Global Indicators")
    st.json(global_m)
