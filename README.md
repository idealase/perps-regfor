# 🔮 Perps Regime Forecaster

Short-term crypto regime forecasting using **public Binance Futures APIs**. This Streamlit application forecasts bull/bear/chop regimes, mean returns (μ), and volatility (σ) for crypto perpetual futures.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## ⚠️ Disclaimer

**This is a research demonstration. Not financial advice.** 

All data is sourced from public Binance APIs. No authentication, secrets, or paid services required.

---

## ✨ Features

- **Data Sources**: Funding rates, open interest, perpetual & spot klines (all public endpoints)
- **Feature Engineering**: 
  - Funding rate EMAs and slope
  - Open interest % change
  - Basis proxy (perp - spot)
  - Realized volatility (24h)
  - Jump detection (3-sigma events)
  - Cyclic time encodings (hour, day-of-week)
  
- **Models**:
  - Regime classifier: Logistic Regression (baseline) or LightGBM
  - Point forecast (μ): ARIMA(1,0,1)
  - Volatility forecast (σ): GARCH(1,1)
  
- **Evaluation Metrics**:
  - Regime: Brier score, confusion matrix, accuracy
  - μ: sMAPE, RMSE
  - σ: QLIKE
  
- **Interactive UI**: 
  - Price chart with regime ribbon
  - Next-bar probability forecasts
  - Configurable lookback, horizon, and model selection
  - All times displayed in `Australia/Perth` timezone

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- `uv` (recommended) or `pip`

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd perps-regfor

# Setup environment and install dependencies
make setup

# (Optional) Install pre-commit hooks
pre-commit install
```

### Run the Application

```bash
make run
```

The Streamlit app will launch at `http://localhost:8501`

### Run Tests

```bash
make test
```

### Lint and Format

```bash
# Lint code
make lint

# Format code
make format
```

---

## 📁 Project Structure

```
perps-regfor/
├── .gitignore              # Ignore patterns
├── .pre-commit-config.yaml # Pre-commit hooks (ruff + black)
├── LICENSE                 # MIT License
├── Makefile               # Automation targets
├── README.md              # This file
├── pyproject.toml         # Python project config
├── streamlit_app.py       # Main Streamlit application
├── .streamlit/
│   └── config.toml        # Streamlit theme config
├── .vscode/
│   ├── launch.json        # VS Code debugger config
│   ├── settings.json      # VS Code editor settings
│   └── tasks.json         # VS Code tasks
├── src/perps_forecaster/
│   ├── __init__.py
│   ├── config.py          # Configuration dataclass
│   ├── data/
│   │   ├── __init__.py
│   │   └── binance.py     # Binance API fetchers + alignment
│   ├── features/
│   │   ├── __init__.py
│   │   └── engine.py      # Feature engineering + label creation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── regime.py      # Regime classifier
│   │   └── point_vol.py   # ARIMA/GARCH forecasters
│   ├── eval/
│   │   ├── __init__.py
│   │   └── metrics.py     # sMAPE, QLIKE, RMSE
│   └── utils/
│       ├── __init__.py
│       └── cache.py       # Parquet cache utilities
├── tests/
│   ├── test_fetch_align.py        # Data fetching tests
│   ├── test_features.py           # Feature engineering tests
│   └── test_labels_and_metrics.py # Label and metric tests
└── data/                  # Cached Parquet files (gitignored)
```

---

## 🔧 Configuration

Default configuration is in `src/perps_forecaster/config.py`:

```python
@dataclass
class Config:
    symbol: str = "BTCUSDT"
    interval: str = "1h"
    display_tz: str = "Australia/Perth"
    cache_dir: Path = Path("data")
    max_rows: int = 2000
    default_lookback: int = 500
    default_horizon: int = 1
    ...
```

Adjust these defaults or use the Streamlit sidebar to configure at runtime.

---

## 🌐 Data Sources (Binance Public APIs)

All endpoints are **public** and require no authentication:

1. **Funding Rate**: `GET https://fapi.binance.com/fapi/v1/fundingRate`
2. **Open Interest**: `GET https://fapi.binance.com/futures/data/openInterestHist`
3. **Perpetual Klines**: `GET https://fapi.binance.com/fapi/v1/continuousKlines`
4. **Spot Klines**: `GET https://api.binance.com/api/v3/klines`

The HTTP client implements:
- **Timeout**: 30 seconds
- **Retries**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Error handling**: Clear error messages on network/HTTP failures

---

## 🧪 Testing

Tests use **live data** from Binance public APIs (no mocking for smoke tests):

```bash
pytest tests/ -v
```

Test coverage:
- `test_fetch_align.py`: Fetch endpoints, alignment, schema validation
- `test_features.py`: Feature engineering on synthetic data
- `test_labels_and_metrics.py`: Label creation and metric calculations

---

## 📊 Architecture

### Data Pipeline
1. **Fetch**: Pull data from 4 Binance endpoints
2. **Align**: Merge on hourly timestamps, sort, forward-fill, drop NaN
3. **Cache**: Save aligned data as Parquet (30-min TTL in Streamlit)
4. **Features**: Engineer 12+ features (funding, OI, basis, volatility, time)
5. **Labels**: Create regime labels using trend + volatility filters

### Modeling Pipeline
1. **Split**: 80/20 train/test
2. **Train**: Fit classifier (Logistic or LightGBM) with StandardScaler
3. **Predict**: Generate probabilities for test set + next bar
4. **Forecast**: ARIMA(1,0,1) for μ, GARCH(1,1) for σ
5. **Evaluate**: Brier, accuracy, confusion matrix, sMAPE, QLIKE

### UI Flow
1. Sidebar: User selects symbol, lookback, horizon, model
2. Load data (cached or fresh fetch)
3. Display price chart with regime ribbon
4. Show next-bar forecast probabilities
5. Display μ/σ forecasts and diagnostics table

---

## 🛠️ Development

### Using `uv` (recommended)

```bash
# Install with uv
uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/ -v

# Run Streamlit
uv run streamlit run streamlit_app.py
```

### Using standard `pip`

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run Streamlit
streamlit run streamlit_app.py
```

### VS Code Integration

The project includes:
- **Tasks**: Run/test/lint via `Ctrl+Shift+B` (Windows) or `Cmd+Shift+B` (Mac)
- **Debugger**: Launch Streamlit with breakpoints (`F5`)
- **Settings**: Auto-format on save with black + ruff

---

## 📦 Dependencies

### Core
- `streamlit` - Web UI framework
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `requests` - HTTP client
- `plotly` - Interactive charts
- `pyarrow` - Parquet I/O
- `pytz` - Timezone handling

### Machine Learning
- `scikit-learn` - Logistic regression, preprocessing
- `lightgbm` - Gradient boosting (optional)
- `statsmodels` - ARIMA
- `arch` - GARCH

### Development
- `pytest` - Testing framework
- `ruff` - Fast linter
- `black` - Code formatter
- `pre-commit` - Git hooks

---

## 🎯 Design Decisions

1. **Public APIs only**: No authentication, no secrets, no rate limits (within reason)
2. **Caching**: Parquet files in `data/` reduce API calls during development
3. **Resilient HTTP**: Retries with exponential backoff for network reliability
4. **Timezone consistency**: All times displayed in `Australia/Perth`
5. **Modular architecture**: Separate packages for data, features, models, eval
6. **Test with live data**: Ensures API compatibility (no brittle mocks)
7. **Streamlit caching**: 30-min TTL balances freshness and performance

---

## 🚨 Known Limitations

- **Hourly data only** (v1): Higher frequency intervals not yet supported
- **Single symbol**: Multi-symbol analysis not implemented
- **No backtesting engine**: Regime forecasts are not walk-forward tested
- **Model simplicity**: Baseline models (Logistic, ARIMA, GARCH) - room for improvement
- **Rate limits**: Heavy usage may trigger Binance rate limits (add delays if needed)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Ensure all tests pass and code is formatted:

```bash
make format
make test
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Brodie

---

## 🙏 Acknowledgments

- **Binance**: For providing free public APIs
- **Streamlit**: For the amazing web framework
- **Python community**: For excellent data science libraries

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Happy forecasting! 📈🔮**
