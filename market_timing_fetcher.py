import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
import market_timing_config as Config
from datetime import datetime

class MarketTimingDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def fetch_all_data(self):
        data = {
            'metadata': {'fetch_timestamp': datetime.now().isoformat()},
            'indian_market': {},
            'global_market': {},
            'signals': {}
        }

        # --- 1. Fetch Indian Data ---
        # Nifty PE (Scrape with fallback)
        pe, pe_zone = 22.5, "FAIR" # Default fallback
        try:
            url = 'https://www.nifty-pe-ratio.com/'
            response = self.session.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Try to find PE in common containers
            div = soup.find('div', {'id': 'current-pe'}) # Example ID
            if not div:
                # Look for text pattern if ID fails
                for tag in soup.find_all(['td', 'span']):
                    if 'PE' in tag.text and len(tag.text) < 10:
                        try:
                            val = float(tag.find_next().text)
                            if 10 < val < 50:
                                pe = val
                                break
                        except: pass
        except:
            print("Using fallback PE")
        
        # Determine Zone
        if pe < Config.NIFTY_PE_THRESHOLDS['cheap']: pe_zone = "CHEAP"
        elif pe > Config.NIFTY_PE_THRESHOLDS['expensive']: pe_zone = "EXPENSIVE"
        
        data['indian_market']['nifty_valuation'] = {'nifty_pe': pe, 'pe_zone': pe_zone}

        # Nifty Price & VIX (Yahoo Finance)
        try:
            nifty = yf.Ticker("^NSEI")
            hist = nifty.history(period="1y")
            price = round(hist['Close'].iloc[-1], 2)
            dma200 = round(hist['Close'].tail(200).mean(), 2)
            
            vix = yf.Ticker("^INDIAVIX")
            vix_val = round(vix.history(period="5d")['Close'].iloc[-1], 2)
            
            vix_sig = "NORMAL"
            if vix_val < Config.INDIA_VIX_THRESHOLDS['low']: vix_sig = "COMPLACENT"
            elif vix_val > Config.INDIA_VIX_THRESHOLDS['high']: vix_sig = "FEAR"

            data['indian_market']['nifty_50'] = {
                'price': price, 
                'dma_200': dma200, 
                'above_200dma': price > dma200,
                'returns': {'1Y': round(((price - hist['Close'].iloc[0])/hist['Close'].iloc[0])*100, 2)}
            }
            data['indian_market']['india_vix'] = {'india_vix': vix_val, 'vix_signal': vix_sig}
        except:
            data['indian_market']['nifty_50'] = {'price': 0, 'dma_200': 0, 'above_200dma': False}
            data['indian_market']['india_vix'] = {'india_vix': 0, 'vix_signal': "N/A"}

        # --- 2. Fetch Global Data ---
        tickers = {
            'dxy': 'DX-Y.NYB',
            'crude': 'BZ=F',
            'gold': 'GC=F',
            'us_vix': '^VIX',
            'usdinr': 'INR=X'
        }
        
        for key, sym in tickers.items():
            try:
                t = yf.Ticker(sym)
                val = round(t.history(period="5d")['Close'].iloc[-1], 2)
                
                # Structure specific keys
                if key == 'dxy': data['global_market']['dollar_index'] = {'dxy': val}
                elif key == 'crude': data['global_market']['crude_oil'] = {'brent_crude': val}
                elif key == 'gold': data['global_market']['gold'] = {'gold_usd': val}
                elif key == 'us_vix': data['global_market']['us_vix'] = {'us_vix': val}
                elif key == 'usdinr': data['global_market']['usdinr'] = {'usdinr': val}
            except:
                pass

        # --- 3. Calculate Signals ---
        score = 50
        # Valuation Logic
        if pe < 18: score += 20
        elif pe > 24: score -= 20
        
        # Trend Logic
        if data['indian_market']['nifty_50'].get('above_200dma'): score += 15
        else: score -= 15
        
        # VIX Logic
        ivix = data['indian_market']['india_vix'].get('india_vix', 15)
        if ivix > 24: score += 15 # Fear is opportunity
        
        score = max(0, min(100, score))
        
        rec = "NEUTRAL"
        alloc = Config.ALLOCATION_MODELS['moderate']['equity']
        if score > 70: 
            rec = "AGGRESSIVE BUY"
            alloc = Config.ALLOCATION_MODELS['aggressive']['equity']
        elif score < 30: 
            rec = "DEFENSIVE"
            alloc = Config.ALLOCATION_MODELS['defensive']['equity']
            
        data['signals'] = {
            'composite_score': score,
            'recommendation': rec,
            'suggested_equity_allocation': alloc,
            'component_scores': {
                'valuation': {'valuation_score': 50}, # Simplified for brevity
                'trend': {'trend_score': 50},
                'volatility': {'volatility_score': 50},
                'macro': {'macro_score': 50}
            }
        }
        
        return data
