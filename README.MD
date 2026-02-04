# 🚀 Pro Quant Market Timing Dashboard

A comprehensive, visually stunning market analysis dashboard for Indian equity markets built with Streamlit.

![Dashboard Preview](https://via.placeholder.com/800x400/0a0f1a/3b82f6?text=Pro+Quant+Dashboard)

## ✨ Features

- **📊 Real-Time Market Signals** - ERP, VIX, PE-based buy/sell recommendations
- **🎯 Market Regime Detection** - Identifies Bull Run, Market Top, Crash, Recovery phases
- **💰 Multi-Cap Valuation** - Large, Mid, Small cap PE percentile analysis
- **📈 Interactive Charts** - Plotly-powered visualizations with dark theme
- **🎨 Stunning UI** - Futuristic dark theme with neon accents and animations

---

## 🛠️ Installation

### Step 1: Clone/Download Files

Ensure you have these files in the same folder:
```
pro_quant_dashboard/
├── pro_quant_dashboard.py      # Main dashboard app
├── requirements.txt            # Python dependencies
├── India_VIX_Yahoo.csv         # VIX data
├── Nifty50_Historical_Yahoo.csv # Nifty 50 prices
├── NIFTY_MIDCAP_100_Historical_Yahoo.csv  # Midcap data
├── Nifty_Index_Valuation_History.csv      # PE data
├── Nifty_10Y_Benchmark_GSec_Merged.csv    # G-Sec data
└── SMALL.csv                   # Smallcap NAV (optional)
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install streamlit pandas numpy plotly openpyxl
```

### Step 3: Run the Dashboard

```bash
streamlit run pro_quant_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📊 Data Requirements

| File | Description | Source |
|------|-------------|--------|
| `India_VIX_Yahoo.csv` | India VIX historical data | Yahoo Finance (^INDIAVIX) |
| `Nifty50_Historical_Yahoo.csv` | Nifty 50 OHLCV data | Yahoo Finance (^NSEI) |
| `Nifty_Index_Valuation_History.csv` | Monthly PE/PB for 55 indices | NSE Index Dashboard PDFs |
| `Nifty_10Y_Benchmark_GSec_Merged.csv` | 10Y G-Sec clean price index | NSE |

### Expected File Formats

**VIX Data:**
```csv
Date,VIX_Open,VIX_High,VIX_Low,VIX_Close
2018-01-01,14.23,15.10,13.89,14.78
```

**Nifty 50 Data:**
```csv
Date,Open,High,Low,Close,Volume
2018-01-01,10435.55,10503.60,10430.35,10478.70,123456789
```

**PE Data:**
```csv
Date,Year,Month,Index,PE_Ratio,PB_Ratio,Div_Yield
2018-01-01,2018,1,Nifty 50,26.45,3.52,1.15
```

---

## 🎯 Signal Interpretation

### ERP (Equity Risk Premium) Signals

| ERP Value | Signal | Meaning |
|-----------|--------|---------|
| > 3% | VERY CHEAP | Strong buy opportunity |
| 1.5% - 3% | CHEAP | Good entry point |
| 0% - 1.5% | FAIR | Hold positions |
| -1.5% - 0% | EXPENSIVE | Consider trimming |
| < -1.5% | VERY EXPENSIVE | Take profits |

### VIX Signals

| VIX Level | Signal | Meaning |
|-----------|--------|---------|
| > 30 | EXTREME FEAR | Contrarian buy signal |
| 25-30 | HIGH FEAR | Accumulate on dips |
| 20-25 | FEAR | Start building positions |
| 15-20 | ELEVATED | Normal caution |
| 12-15 | NORMAL | Neutral |
| < 12 | COMPLACENCY | Contrarian sell signal |

### Market Regimes

| Regime | Conditions | Recommended Action |
|--------|------------|-------------------|
| 🎯 IDEAL BOTTOM | High ERP + Panic VIX + Big Drawdown | Aggressive Buy |
| 🚀 BULL RUN | Low VIX + Near ATH | Hold, Trail Stops |
| ⚠️ MARKET TOP | Complacent VIX + Expensive ERP | Trim, Hedge |
| 📉 CRASH MODE | Panic VIX + Large Drawdown | SIP, Accumulate |
| 📈 RECOVERY | Moderate Drawdown + VIX Normalizing | Add Positions |

---

## 🎨 Customization

### Change Color Theme

Edit the CSS variables in `pro_quant_dashboard.py`:

```css
:root {
    --bg-dark: #0a0f1a;        /* Main background */
    --bg-card: #111827;        /* Card background */
    --green: #10b981;          /* Bullish color */
    --red: #ef4444;            /* Bearish color */
    --blue: #3b82f6;           /* Accent color */
}
```

### Adjust Signal Thresholds

Modify the signal functions:

```python
def get_erp_signal(erp):
    if erp > 3:    # Adjust this threshold
        return 'VERY CHEAP', 2, '#10b981'
    # ... etc
```

---

## 📈 Screenshots

### Main Dashboard
- Key metrics with animated signal badges
- Real-time market regime detection
- Interactive gauge charts

### Historical Analysis
- PE ratio trends across market caps
- VIX fear/greed visualization
- ERP time series with buy/sell zones

### Signal History
- Monthly signal tracking
- Distribution analysis
- Sector valuation heatmap

---

## 🔧 Troubleshooting

### "Could not load market data"
- Ensure all CSV files are in the same directory as the script
- Check file names match exactly (case-sensitive)
- Verify CSV format matches expected structure

### Slow Performance
- Reduce data range in the sidebar
- Close other browser tabs
- Ensure you have at least 4GB RAM

### Charts Not Rendering
- Clear browser cache
- Try a different browser (Chrome recommended)
- Update Plotly: `pip install --upgrade plotly`

---

## 📝 License

MIT License - Feel free to modify and distribute.

---

## 🙏 Credits

- Data Sources: NSE India, Yahoo Finance
- Built with: Streamlit, Plotly, Pandas
- Fonts: Orbitron, Rajdhani, JetBrains Mono

---

**⚠️ Disclaimer:** This dashboard is for educational and informational purposes only. 
It does not constitute financial advice. Always do your own research before making investment decisions.
