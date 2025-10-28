# 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT APPLICATION                                │
│                         (streamlit_app.py)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ User Input (symbol, lookback, horizon)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA LOADING & CACHING                               │
│                    (30-min TTL, Parquet persistence)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
        ┌───────────────────────┐         ┌───────────────────────┐
        │   Cache Hit (Parquet) │         │   Cache Miss (Fetch)  │
        │   Load from data/     │         │   Binance Public APIs │
        └───────────────────────┘         └───────────────────────┘
                    │                                   │
                    │                                   │
                    │     ┌──────────────────────────┬──┴──────────┬──────────────┐
                    │     │                          │             │              │
                    │     ▼                          ▼             ▼              ▼
                    │  Funding                    Open          Perp          Spot
                    │  Rate API                Interest        Klines       Klines
                    │     │                          │             │              │
                    │     └──────────────────────────┴─────────────┴──────────────┘
                    │                                   │
                    │                                   ▼
                    │                          ┌─────────────────┐
                    │                          │  align_hourly() │
                    │                          │  merge, sort,   │
                    │                          │  ffill, dropna  │
                    │                          └─────────────────┘
                    │                                   │
                    └───────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FEATURE ENGINEERING                                  │
│                      (features/engine.py)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Funding: EMA(8), EMA(24), slope                                          │
│  • Open Interest: % change (clipped)                                        │
│  • Basis: perp_close - spot_close                                           │
│  • Volatility: realized_vol(24h), jump_3sigma                               │
│  • Time: hour_sin/cos, dow_sin/cos                                          │
│  • Price: EMA(12), EMA(48) for trend                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LABEL CREATION                                       │
│                      (features/engine.py)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Logic:                                                                      │
│  • Calculate future return (horizon bars ahead)                             │
│  • Trend filter: EMA(12) vs EMA(48)                                         │
│  • Volatility gate: rv24 > median?                                          │
│  • Bull: positive future return + uptrend + high vol                        │
│  • Bear: negative future return + downtrend + high vol                      │
│  • Chop: everything else (low vol or mixed signals)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TRAIN/TEST SPLIT (80/20)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
        ┌───────────────────────┐         ┌───────────────────────┐
        │   REGIME CLASSIFIER   │         │ POINT & VOL FORECAST  │
        │  (models/regime.py)   │         │ (models/point_vol.py) │
        ├───────────────────────┤         ├───────────────────────┤
        │ • StandardScaler      │         │ • ARIMA(1,0,1) for μ  │
        │ • LogisticRegression  │         │ • GARCH(1,1) for σ    │
        │   or LightGBM         │         │                       │
        │ • Predict proba       │         │ • Fallback to naive   │
        └───────────────────────┘         └───────────────────────┘
                    │                                   │
                    ▼                                   ▼
        ┌───────────────────────┐         ┌───────────────────────┐
        │  Next Bar Probabilities│         │   μ_hat, σ_hat       │
        │  P(bull), P(bear),    │         │                       │
        │  P(chop)              │         │                       │
        └───────────────────────┘         └───────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EVALUATION & METRICS                                 │
│                       (eval/metrics.py)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Regime:                             Point/Vol:                              │
│  • Brier score per class            • sMAPE (mean forecast)                 │
│  • Confusion matrix                 • QLIKE (volatility forecast)           │
│  • Accuracy                         • RMSE                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT UI DISPLAY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PRICE CHART WITH REGIME RIBBON                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                                                              │   │   │
│  │  │  🟢🟢🟢 Bull   🔴🔴🔴 Bear   ⚪⚪⚪ Chop                      │   │   │
│  │  │                                                              │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │  FUNDING RATE SUBPLOT                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│  │  NEXT BAR FORECAST           │  │  μ & σ FORECAST              │        │
│  │  ┌────────────────────────┐  │  │  ┌────────────────────────┐  │        │
│  │  │ Bull:  35%            │  │  │  │ μ:  0.0012 (0.12%)    │  │        │
│  │  │ Bear:  25%            │  │  │  │ σ:  0.0145 (1.45%)    │  │        │
│  │  │ Chop:  40%            │  │  │  └────────────────────────┘  │        │
│  │  └────────────────────────┘  │  └──────────────────────────────┘        │
│  │  [Bar Chart]                 │                                           │
│  └──────────────────────────────┘                                           │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  DIAGNOSTICS TABLE (Last 10 Bars)                                   │   │
│  │  timestamp | price | funding | oi_chg | basis | rv24 | regime       │   │
│  │  ...                                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MODEL EVALUATION (Test Set)                                        │   │
│  │  Accuracy: 62%    Avg Brier: 0.32    Test Samples: 100              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Sequence

```
1. User opens Streamlit → Sidebar inputs
2. load_and_process_data() → Check cache
3. If cache miss → fetch_funding_rate(), fetch_open_interest(), etc.
4. align_hourly() → Merge all sources
5. Save to Parquet cache
6. build_features() → Engineer 12 features
7. create_regime_labels() → Label with bull/bear/chop
8. Split 80/20 train/test
9. train_regime_classifier() → Fit model
10. predict_regime_proba() → Get probabilities
11. forecast_next_bar() → ARIMA + GARCH
12. Display in Streamlit UI
```

---

## Module Dependencies

```
streamlit_app.py
    ├─ config.py
    ├─ utils/cache.py
    ├─ data/binance.py
    │   └─ requests (HTTP)
    ├─ features/engine.py
    │   └─ numpy, pandas
    ├─ models/regime.py
    │   └─ sklearn
    ├─ models/point_vol.py
    │   ├─ statsmodels (ARIMA)
    │   └─ arch (GARCH)
    └─ eval/metrics.py
        └─ sklearn

tests/
    ├─ test_fetch_align.py → data/binance.py
    ├─ test_features.py → features/engine.py
    └─ test_labels_and_metrics.py → features/engine.py, eval/metrics.py
```

---

## HTTP Retry Strategy

```
Request
   │
   ▼
Try 1 ───[Success]───► Return data
   │
   ▼ [Fail: 429, 500, 502, 503, 504]
Wait 1 second
   │
   ▼
Try 2 ───[Success]───► Return data
   │
   ▼ [Fail]
Wait 2 seconds (exponential backoff)
   │
   ▼
Try 3 ───[Success]───► Return data
   │
   ▼ [Fail]
Wait 4 seconds
   │
   ▼
Try 4 ───[Success]───► Return data
   │
   ▼ [Fail]
Raise Exception with clear error message
```

---

## Caching Strategy

```
Data Request
   │
   ▼
Check Streamlit cache (30 min TTL)
   │
   ├─[Hit]──► Return cached DataFrame
   │
   └─[Miss]
      │
      ▼
   Check Parquet file in data/
      │
      ├─[Exists + Fresh]──► Load Parquet → Return
      │
      └─[Missing or Stale]
         │
         ▼
      Fetch from Binance APIs
         │
         ▼
      Align data
         │
         ▼
      Save to Parquet
         │
         ▼
      Return DataFrame
```

---

## Feature Engineering Pipeline

```
Raw Data (aligned)
   │
   ├─► log_return = log(close/close_lag1)
   │
   ├─► funding_ema8 = EMA(fundingRate, 8)
   ├─► funding_ema24 = EMA(fundingRate, 24)
   ├─► funding_slope = ema8 - ema24
   │
   ├─► oi_pct_chg = openInterest.pct_change().clip(-0.2, 0.2)
   │
   ├─► basis_proxy = perp_close - spot_close
   │
   ├─► rv24 = rolling_std(log_return, 24)
   │
   ├─► jump_3sigma = |log_return| > 3 * rolling_std(log_return, 24)
   │
   ├─► price_ema12 = EMA(perp_close, 12)
   ├─► price_ema48 = EMA(perp_close, 48)
   │
   ├─► hour_sin, hour_cos = cyclic_encode(hour, 24)
   └─► dow_sin, dow_cos = cyclic_encode(day_of_week, 7)
   │
   ▼
Feature Matrix (12 columns)
```

---

## Regime Label Logic

```
For each row:
   │
   ├─► future_return = log_return[t+horizon]
   │
   ├─► uptrend = (price_ema12 > price_ema48)
   │
   ├─► high_vol = (rv24 > median(rv24))
   │
   ▼
Assign regime:
   │
   ├─► IF future_return > 0 AND uptrend AND high_vol
   │      → regime = "bull"
   │
   ├─► ELSE IF future_return < 0 AND NOT uptrend AND high_vol
   │      → regime = "bear"
   │
   └─► ELSE
          → regime = "chop"
```

---

## Model Training Flow

```
Feature Matrix + Labels
   │
   ▼
Split 80/20
   │
   ├─► Train Set (80%)
   │      │
   │      ├─► StandardScaler.fit_transform()
   │      │
   │      └─► LogisticRegression.fit() or LGBMClassifier.fit()
   │
   └─► Test Set (20%)
          │
          └─► StandardScaler.transform()
```

---

## Prediction Flow

```
Last Row Features
   │
   ▼
StandardScaler.transform()
   │
   ▼
Model.predict_proba()
   │
   ▼
[P(bear), P(bull), P(chop)]
   │
   ▼
Display in UI (bar chart + table)
```

---

This architecture provides:
- ✅ **Modularity**: Each component is independent
- ✅ **Testability**: Each module can be tested in isolation
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Extensibility**: Easy to add features or models
- ✅ **Performance**: Smart caching at multiple levels
- ✅ **Resilience**: Retry logic and error handling throughout
