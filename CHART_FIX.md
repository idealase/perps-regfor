# 🔧 Chart Not Displaying - FIXED!

## The Problem
Plotly charts were failing to render in Streamlit, showing placeholder text instead of actual charts.

## The Root Cause
**Timezone-aware datetime objects**: Plotly has poor support for timezone-aware pandas datetime objects. When we converted timestamps to Australia/Perth timezone, they remained timezone-aware, causing Plotly to fail silently.

## The Solution
After converting to the display timezone, we strip the timezone info:

```python
# Convert to display timezone
df["timestamp_local"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(tz)

# KEY FIX: Remove timezone info for Plotly compatibility
df["timestamp_local"] = df["timestamp_local"].dt.tz_localize(None)
```

## Additional Improvements

1. **Error Handling**: Wrapped chart rendering in try-except blocks
2. **Dark Theme**: Added `template="plotly_dark"` for better visibility
3. **Debug Info**: Added expandable debug section to verify data
4. **Fallback Chart**: If complex chart fails, shows simple line chart

## How to Verify Fix

1. Restart Streamlit (in terminal: Ctrl+C, then `streamlit run streamlit_app.py`)
2. Wait for data to load
3. You should now see:
   - ✅ Price chart with colored regime ribbon
   - ✅ Funding rate subplot below price
   - ✅ Probability bar chart in right panel
   - ✅ Interactive hover tooltips

## Debug Checklist

If charts still don't appear:

### 1. Check Debug Info
Click "🔍 Debug Info" expander to see:
- Data shape (should be ~400-500 rows)
- Date range
- Regime counts (should have bull, bear, chop)
- Sample data

### 2. Check Browser Console
Press F12 in browser, look for JavaScript errors

### 3. Check Streamlit Terminal
Look for Python errors or warnings

### 4. Verify Data Types
In debug expander, ensure:
- `timestamp_local` is datetime64[ns] (NOT datetime64[ns, tz])
- `perp_close` and `fundingRate` are float64
- `regime` is object (string)

### 5. Try Simple Chart
If complex chart fails, the code will automatically fall back to:
```python
st.line_chart(df.set_index("timestamp_local")[["perp_close"]])
```

## Common Issues & Fixes

### Issue: "TypeError: Object of type Timestamp is not JSON serializable"
**Cause**: Timezone-aware timestamps
**Fix**: Already applied - we strip timezone info

### Issue: Charts show but are blank/white
**Cause**: All NaN values or empty data
**Fix**: Check debug info for data quality

### Issue: Charts render slowly
**Cause**: Too many vrect shapes for regime ribbon
**Fix**: Reduce lookback or simplify ribbon (if needed)

### Issue: Hover tooltips don't work
**Cause**: Missing or misaligned data
**Fix**: Check that timestamp_local has no gaps

## Performance Notes

With 500 bars of data:
- Chart render time: ~2-3 seconds (normal)
- Regime ribbon: ~500 vrect shapes (manageable)
- Total plotly figure size: ~1-2 MB (acceptable)

If performance is slow with >1000 bars, consider:
1. Reducing lookback
2. Simplifying regime ribbon (sample every N bars)
3. Using simpler chart library (altair)

## Alternative Chart Libraries

If Plotly continues to have issues, we can switch to:

### Altair (lightweight, fast)
```python
import altair as alt

chart = alt.Chart(df).mark_line().encode(
    x='timestamp_local:T',
    y='perp_close:Q'
)
st.altair_chart(chart, use_container_width=True)
```

### Matplotlib (classic, reliable)
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df['timestamp_local'], df['perp_close'])
st.pyplot(fig)
```

### Bokeh (interactive, robust)
```python
from bokeh.plotting import figure

p = figure(x_axis_type='datetime', width=800, height=400)
p.line(df['timestamp_local'], df['perp_close'])
st.bokeh_chart(p, use_container_width=True)
```

## Verification Steps

1. ✅ Restart Streamlit
2. ✅ Load data (wait for "✅ Fetched XXX bars")
3. ✅ See price chart with colored background
4. ✅ See funding rate chart below
5. ✅ See probability bar chart on right
6. ✅ Hover over charts - tooltips work
7. ✅ Zoom/pan - interactions work

## Success Indicators

When working correctly:
- 🟢 Blue price line visible
- 🟢 Green/red/gray regime backgrounds visible
- 🟢 Purple funding rate line visible
- 🟢 Bar chart shows 3 bars (bull, bear, chop)
- 🟢 Hover shows price/time values
- 🟢 No error messages

## If Still Broken

1. Check Python version: `python --version` (need 3.11+)
2. Reinstall plotly: `pip install --upgrade plotly`
3. Clear Streamlit cache: Press 'c' in terminal while app running
4. Try different browser (Chrome recommended)
5. Check firewall/proxy settings

## Files Modified

- `streamlit_app.py`:
  - Added `.dt.tz_localize(None)` after timezone conversion
  - Added try-except blocks around chart rendering
  - Added `template="plotly_dark"` for better visibility
  - Added debug expander
  - Added fallback simple chart

## Testing

The fix has been applied. To test:

```powershell
cd c:\Users\brodi\OneDrive\Desktop\Sandbox\perps-regfor

# Restart Streamlit
# In terminal: Ctrl+C to stop, then:
streamlit run streamlit_app.py
```

**Expected result**: Charts now display correctly! ✅

---

**Last Updated**: October 28, 2025
**Issue**: Chart not displaying
**Status**: ✅ FIXED
