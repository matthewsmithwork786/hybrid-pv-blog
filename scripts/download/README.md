# Data Download Scripts

This folder contains scripts to download and cache all required NEM data for the Beyond the Solar Curve analysis.

## Overview

All data is downloaded from AEMO via the NEMOSIS library and cached locally to avoid repeated API calls. Generator metadata is fetched from the OpenElectricity API for current, accurate facility information.

**Cache location:** `C:\Users\matts\Documents\Aus research\Nemosis_data`

## Prerequisites

Ensure you have activated the hybridpv environment:

```bash
mamba activate hybridpv
```

## Download Scripts

Run these scripts **in order** to download all required data:

### 1. download_dispatchprice.py

Downloads regional wholesale prices (RRP) for all NEM regions (2018-2025).

```bash
python download_dispatchprice.py
```

- **Table:** DISPATCHPRICE
- **Size:** ~5-8 GB
- **Time:** 30-60 minutes
- **Use:** Price analysis, revenue calculations

### 2. download_dispatch_scada.py

Downloads actual generation/load data for all generators (2018-2025).

```bash
python download_dispatch_scada.py
```

- **Table:** DISPATCH_UNIT_SCADA
- **Size:** ~50-60 GB ⚠️ LARGE
- **Time:** 2-4 hours
- **Use:** Actual output, revenue validation, battery operations
- **Note:** Downloads month-by-month, can be interrupted and resumed

### 3. download_dispatchload.py

Downloads dispatch targets and availability for semi-scheduled units (2018-2025).

```bash
python download_dispatchload.py
```

- **Table:** DISPATCHLOAD
- **Size:** ~10-15 GB
- **Time:** 1-2 hours
- **Use:** Curtailment analysis for solar/wind

### 4. download_generator_metadata.py

Downloads current generator metadata from OpenElectricity API.

```bash
python download_generator_metadata.py
```

- **Source:** OpenElectricity API
- **Size:** ~5 MB
- **Time:** <1 minute
- **Use:** Facility names, coordinates, capacity, fuel type, status

## Total Requirements

- **Disk space:** ~70-80 GB
- **Download time:** 4-6 hours (depending on internet speed)
- **Internet:** Stable connection required

## Data Files

After running all scripts, your data directory will contain:

```
C:\Users\matts\Documents\Aus research\Nemosis_data\
├── PUBLIC_ARCHIVE#DISPATCHPRICE#FILE01#201801010000.parquet
├── PUBLIC_ARCHIVE#DISPATCHPRICE#FILE01#201802010000.parquet
├── ...
├── PUBLIC_ARCHIVE#DISPATCH_UNIT_SCADA#FILE01#201801010000.parquet
├── PUBLIC_ARCHIVE#DISPATCH_UNIT_SCADA#FILE01#201802010000.parquet
├── ...
├── PUBLIC_ARCHIVE#DISPATCHLOAD#FILE01#201801010000.parquet
├── PUBLIC_ARCHIVE#DISPATCHLOAD#FILE01#201802010000.parquet
├── ...
└── openelectricity_facilities.csv
```

## Troubleshooting

### Download interrupted

NEMOSIS downloads month-by-month. If interrupted:
- Re-run the script
- It will resume from where it left off (already-downloaded months are skipped)

### Memory issues

If you encounter memory errors:

1. **Reduce thread count** (already set in scripts):
   ```python
   os.environ['POLARS_MAX_THREADS'] = '2'
   ```

2. **Download in smaller chunks** - Edit date ranges in scripts:
   ```python
   # Instead of 2018-2025, do:
   START_DATE = '2018/01/01 00:00:00'
   END_DATE = '2018/12/31 23:59:59'  # One year at a time
   ```

3. **Close other applications** to free up RAM

### Disk space issues

- Check available space: Each table requires 5-60 GB
- Consider external drive if needed
- Update `NEMOSIS_DATA_DIR` in scripts to point to external location

### Connection timeouts

- AEMO servers can be slow during peak times
- Try running during off-peak hours (evenings/weekends)
- Scripts will retry failed downloads automatically

### API errors

If OpenElectricity API fails:
- Check: https://api.openelectricity.org.au/v4/facilities/
- Verify internet connection
- API may have temporary outages - try again later

## Manual Download Alternative

If automated downloads fail, you can manually download from AEMO:

1. Visit: https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/market-management-system-mms-data
2. Navigate to "Data Archive"
3. Select tables: DISPATCHPRICE, DISPATCH_UNIT_SCADA, DISPATCHLOAD
4. Download monthly ZIP files
5. Extract parquet files to `NEMOSIS_DATA_DIR`

## Data Update Schedule

For ongoing analysis, update data periodically:

- **Monthly:** Run all scripts to get latest month
- **Annual:** Full refresh at start of each year
- **Ad-hoc:** After major market events

## Next Steps

After downloads complete, you can:

1. **Verify data:** Check file counts and sizes
2. **Run analyses:** Execute scripts in `scripts/section1/`, `scripts/section3/`, etc.
3. **Generate report:** Use `quarto render` to build full report

## Support

For issues with:
- **NEMOSIS library:** https://github.com/UNSW-CEEM/NEMOSIS/issues
- **OpenElectricity API:** https://github.com/opennem/openelectricity
- **This project:** Check main README.md or create issue
