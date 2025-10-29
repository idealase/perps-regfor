# UI Mockup: Insights & Decision Pathways

## Page Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ⚠️ Research Demo: This is a research demonstration. Not financial advice │
└─────────────────────────────────────────────────────────────────────────┘

🔮 Crypto Regime Forecaster
Short-term regime forecasting using public Binance Futures APIs

┌──────────────────────────────────────────────────────────────────────────┐
│  [Price Chart with Regime Ribbon]     │  🔮 Next Bar Forecast           │
│                                        │                                  │
│  [Colored background showing           │  Regime Probabilities:           │
│   bull/bear/chop regimes]              │  ┌─────────────────────┐        │
│                                        │  │ Regime | Probability │        │
│  [Blue price line]                     │  │ bear   | 20.5%       │        │
│  [Purple funding rate subplot]         │  │ bull   | 70.3%       │        │
│                                        │  │ chop   | 9.2%        │        │
│                                        │  └─────────────────────┘        │
│                                        │                                  │
│                                        │  [Bar Chart]                     │
│                                        │  bull ████████████████           │
│                                        │  bear ████                       │
│                                        │  chop ██                         │
│                                        │                                  │
│                                        │  Point & Volatility Forecast:    │
│                                        │  μ (mean return): 1.50%          │
│                                        │  σ (volatility): 3.20%           │
└──────────────────────────────────────────────────────────────────────────┘

─────────────────────────────────────────────────────────────────────────────

💡 Insights & Decision Pathways

### Confidence Score: 🟢 82/100

┌─▼─ 🎯 Regime Interpretation ──────────────────────────────────────────┐
│                                                                        │
│  🟢 **Bullish Regime** - Market showing upward momentum with high     │
│  volatility                                                            │
│                                                                        │
│  **Market Conditions:** Strong uptrend with fast EMA > slow EMA,      │
│  positive funding rates suggest long bias, high volatility creates    │
│  opportunities                                                         │
│                                                                        │
│  **Risk Level:** Moderate                                              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

┌─▼─ 📋 Trading Suggestions ────────────────────────────────────────────┐
│                                                                        │
│  **Suggested Actions:**                                                │
│  - ✅ Consider long positions in alignment with trend                  │
│  - 🎯 Expected return: 1.50% with volatility 3.20%                    │
│  - ⏰ Use tight stop losses due to high volatility                     │
│  - 📊 Monitor funding rate - high rates may signal over-leverage       │
│                                                                        │
│  ──────────────────────────────────────────────────────                │
│                                                                        │
│  **Position Sizing:** **Moderate to Large** (60-80% of normal         │
│  position)                                                             │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

┌─▶─ 🔍 What's Driving This Forecast? ──────────────────────────────────┐
│                                                                        │
│  **Key Market Drivers (by percentile):**                              │
│  ┌──────────────────────────┬─────────────┐                          │
│  │ Feature                  │ Percentile  │                          │
│  ├──────────────────────────┼─────────────┤                          │
│  │ Funding Rate             │ 92nd        │                          │
│  │ Open Interest Change     │ 88th        │                          │
│  │ Realized Volatility      │ 75th        │                          │
│  │ Basis (Perp-Spot)        │ 68th        │                          │
│  └──────────────────────────┴─────────────┘                          │
│                                                                        │
│  **Supporting Signals:**                                               │
│  ✅ 📈 High positive funding rate (0.1234%) indicates long bias        │
│  ✅ 🔥 Large OI increase (7.5%) - strong new positioning               │
│  ✅ ⚡ High volatility (3.2%) - regime clarity increases                │
│  ✅ 💰 Positive basis - perp premium suggests bullish sentiment        │
│                                                                        │
│  **Contradicting Signals:**                                            │
│  (none)                                                                │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

┌─▶─ 📊 Historical Model Performance ───────────────────────────────────┐
│                                                                        │
│  **Accuracy by Regime:**                                               │
│  ┌──────────┬──────────┐                                              │
│  │ Regime   │ Accuracy │                                              │
│  ├──────────┼──────────┤                                              │
│  │ bear     │ 65.2%    │                                              │
│  │ bull     │ 72.8%    │                                              │
│  │ chop     │ 58.3%    │                                              │
│  └──────────┴──────────┘                                              │
│                                                                        │
│  **Regime Distribution (Historical):**                                 │
│  ┌──────────┬───────┬────────────┐                                    │
│  │ Regime   │ Count │ Percentage │                                    │
│  ├──────────┼───────┼────────────┤                                    │
│  │ bull     │ 145   │ 36.2%      │                                    │
│  │ chop     │ 168   │ 42.0%      │                                    │
│  │ bear     │ 87    │ 21.8%      │                                    │
│  └──────────┴───────┴────────────┘                                    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘

🔍 Diagnostics: Last 10 Bars
[Existing diagnostics table unchanged]

📊 Model Evaluation (Test Set)
[Existing metrics unchanged]

─────────────────────────────────────────────────────────────────────────────
Data source: Binance Public APIs | Display timezone: Australia/Perth
Built with ❤️ using Streamlit
```

## Color Coding

### Confidence Score
- 🟢 Green (70-100): High confidence
- 🟠 Orange (40-69): Moderate confidence  
- 🔴 Red (0-39): Low confidence

### Regime Indicators
- 🟢 Bull: Green background ribbon on chart
- 🔴 Bear: Red background ribbon on chart
- ⚪ Chop: Gray background ribbon on chart

## Interaction

### Expanded by Default
- 🎯 Regime Interpretation
- 📋 Trading Suggestions

### Collapsed by Default
- 🔍 What's Driving This Forecast?
- 📊 Historical Model Performance

### Warning Alerts
If conditions warrant, warnings appear above the expanders:

```
⚠️ HIGH VOLATILITY ALERT: Expected volatility 8.50% - use wider stops
```

## Alternative Scenarios

### Low Confidence Choppy Market

```
### Confidence Score: 🔴 35/100

⚠️ LOW CONFIDENCE: Model uncertainty is high - avoid large positions
🤔 MIXED SIGNALS: No clear regime dominance - wait for confirmation

┌─▼─ 🎯 Regime Interpretation ──────────────────────────────────────────┐
│  ⚪ **Choppy Regime** - Market consolidating with low directional     │
│  conviction                                                            │
│  **Market Conditions:** Low volatility environment, unclear trend...   │
│  **Risk Level:** Moderate                                              │
└────────────────────────────────────────────────────────────────────────┘

┌─▼─ 📋 Trading Suggestions ────────────────────────────────────────────┐
│  **Suggested Actions:**                                                │
│  - 🚫 **No clear directional edge** - avoid new positions              │
│  - 📊 Expected return: 0.10% with low volatility 1.50%                │
│  - 💰 Consider taking profits on existing positions                    │
│  - ⏸️ Wait for better setup with clearer regime                        │
│  - 🎯 Range-bound strategies may work (mean reversion)                 │
│                                                                        │
│  **Position Sizing:** **Minimal** (0-20% of normal position) or       │
│  stay flat                                                             │
└────────────────────────────────────────────────────────────────────────┘
```

### High Confidence Bear Market

```
### Confidence Score: 🟠 68/100

⚡ HIGH VOLATILITY ALERT: Expected volatility 5.20% - use wider stops

┌─▼─ 🎯 Regime Interpretation ──────────────────────────────────────────┐
│  🔴 **Bearish Regime** - Market showing downward pressure with high   │
│  volatility                                                            │
│  **Market Conditions:** Downtrend with fast EMA < slow EMA...          │
│  **Risk Level:** High                                                  │
└────────────────────────────────────────────────────────────────────────┘

┌─▼─ 📋 Trading Suggestions ────────────────────────────────────────────┐
│  **Suggested Actions:**                                                │
│  - 🔻 Consider short positions or exit longs                           │
│  - 🎯 Expected return: -2.30% with volatility 5.20%                   │
│  - 🛡️ Use wider stops due to short squeeze risk                        │
│  - ⚡ Monitor for capitulation signals or reversal patterns             │
│                                                                        │
│  **Position Sizing:** **Moderate** (40-60% of normal position)        │
└────────────────────────────────────────────────────────────────────────┘
```

## Responsive Design

The UI adapts to different screen sizes:
- Desktop: Side-by-side chart and forecast
- Mobile: Stacked layout with full-width sections
- All expanders remain functional
- Tables adjust to container width
