"""
MARKET TIMING CONFIGURATION
"""

# VALUATION THRESHOLDS
NIFTY_PE_THRESHOLDS = {
    'cheap': 18,
    'fair_low': 18,
    'fair_high': 24,
    'expensive': 24
}

# VOLATILITY THRESHOLDS
INDIA_VIX_THRESHOLDS = {
    'low': 12,
    'high': 25
}

# MACRO THRESHOLDS
DXY_THRESHOLDS = {'weak': 100, 'strong': 105}
CRUDE_OIL_THRESHOLDS = {'low': 70, 'high': 90}

# ALLOCATION MODELS
ALLOCATION_MODELS = {
    'aggressive': {'equity': '70-85%', 'gold': '5%', 'debt': '5%'},
    'moderate': {'equity': '55-70%', 'gold': '10%', 'debt': '10%'},
    'defensive': {'equity': '15-30%', 'gold': '25%', 'debt': '50%'}
}
