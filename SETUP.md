# 🚀 Quick Setup Guide

## Installation Steps

### 1. Install Python 3.11+
Ensure Python 3.11 or higher is installed:
```bash
python --version
```

### 2. Install uv (optional, recommended)
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or use pip
pip install uv
```

### 3. Setup Project
```bash
cd perps-regfor
make setup
```

This will:
- Install all dependencies (streamlit, pandas, scikit-learn, etc.)
- Install development tools (pytest, ruff, black)
- Setup pre-commit hooks (optional)

### 4. Run Application
```bash
make run
```

Visit: `http://localhost:8501`

### 5. Run Tests (optional)
```bash
make test
```

## Windows-Specific Notes

If `make` is not available, run commands directly:

```powershell
# Setup
pip install -e ".[dev]"

# Run
streamlit run streamlit_app.py

# Test
pytest tests/ -v

# Lint
ruff check src/ tests/ streamlit_app.py

# Format
black src/ tests/ streamlit_app.py
```

## First Run

On first run, the app will:
1. Fetch ~500 bars of data from Binance (takes ~10-30 seconds)
2. Cache data in `data/` directory as Parquet
3. Build features and train model
4. Display interactive dashboard

Subsequent runs will use cached data (refresh every 30 minutes).

## Troubleshooting

### Import Errors
If you see import errors, ensure you're in the project root and have run:
```bash
pip install -e .
```

### Network Errors
If data fetching fails:
- Check internet connection
- Binance APIs may be temporarily unavailable
- Try again after a few minutes

### Package Not Found
If specific packages fail to install:
```bash
# Install individually
pip install streamlit pandas numpy requests scikit-learn statsmodels arch plotly pyarrow pytz lightgbm pytest ruff black pre-commit
```

## Next Steps

1. ✅ Run `make run` to start the app
2. ✅ Adjust parameters in the sidebar (lookback, horizon, model)
3. ✅ Explore the price chart and regime forecasts
4. ✅ Check diagnostics table for feature values
5. ✅ Run tests with `make test` to verify everything works

Enjoy! 🎉
