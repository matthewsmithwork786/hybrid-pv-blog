# NEMOSIS Skill - Australian NEM Data Access

## Overview

NEMOSIS is a Python library for accessing historical data from the Australian National Electricity Market (NEM) operated by AEMO. This skill covers common patterns for downloading, caching, and processing NEM data.

## Key Concepts

### Data Tables

NEMOSIS provides access to various AEMO MMS tables:

| Table Name | Description | Time Resolution | Primary Use |
|------------|-------------|-----------------|-------------|
| **DISPATCHPRICE** | Regional spot prices (RRP) | 5-minute | Price analysis, revenue calculations |
| **DISPATCH_UNIT_SCADA** | Actual generation/load (MW) | 5-minute | Actual output, revenue validation |
| **DISPATCHLOAD** | Dispatch targets & availability | 5-minute | Curtailment analysis, semi-scheduled units |
| **DUDETAILSUMMARY** | Generator static metadata | Standing data | Generator registry (deprecated, use OpenElectricity) |
| **PARTICIPANT_REGISTRATION** | Participant and connection point data | Standing data | MLF values, TNI mappings |

### Timezone Handling

**Critical:** All NEMOSIS timestamps use **Australia/Brisbane** timezone (EST, UTC+10) year-round with NO daylight saving.

- Format: `"YYYY/MM/DD HH:MM:SS"`
- Example: `"2024/01/15 13:30:00"`
- Always parse with explicit format in Polars: `.str.strptime(pl.Datetime, format="%Y/%m/%d %H:%M:%S")`

### Battery Dual DUIDs

Batteries appear as **TWO separate DUIDs** in NEM data:
- One for **discharging** (dispatch_type='GENERATOR')
- One for **charging** (dispatch_type='LOAD')

**When calculating battery net revenue:**
```python
# Discharge = positive revenue
discharge_rev = discharge_scada['SCADA'] * prices['RRP'] * (5/60)

# Charge = negative revenue (paying to charge)
charge_rev = -1 * charge_scada['SCADA'] * prices['RRP'] * (5/60)

# Net revenue
net_rev = discharge_rev + charge_rev
```

## Data Download Patterns

### Basic Cache Download

```python
from nemosis import cache_compiler

data_directory = r'C:\Users\matts\Documents\Aus research\Nemosis_data'

# Download and cache data
cache_compiler(
    start_time='2024/01/01 00:00:00',
    end_time='2024/01/31 23:59:59',
    table_name='DISPATCHPRICE',
    raw_data_location=data_directory,
    fformat='parquet'  # Use parquet for efficiency
)
```

**File naming:** `PUBLIC_ARCHIVE#{TABLE}#FILE01#{YYYYMM}010000.parquet`

### Loading Cached Data with Polars

```python
import polars as pl
from pathlib import Path

# Memory optimization
import os
os.environ['POLARS_MAX_THREADS'] = str(max(1, (os.cpu_count() or 2) // 2))

# Lazy load cached files
data_dir = Path(r'C:\Users\matts\Documents\Aus research\Nemosis_data')
files = list(data_dir.glob("PUBLIC_ARCHIVE#DISPATCHPRICE#*.parquet"))

df = pl.scan_parquet(files)

# Parse datetime
df = df.with_columns(
    pl.col("SETTLEMENTDATE").str.strptime(pl.Datetime, format="%Y/%m/%d %H:%M:%S")
)

# Filter date range
df = df.filter(
    (pl.col("SETTLEMENTDATE") >= pl.lit("2024-01-01").str.strptime(pl.Datetime, format="%Y-%m-%d")) &
    (pl.col("SETTLEMENTDATE") <= pl.lit("2024-12-31").str.strptime(pl.Datetime, format="%Y-%m-%d"))
)

# Collect results
result = df.collect()
```

## Generator Metadata: OpenElectricity API

**Best Practice:** Use OpenElectricity API instead of DUDETAILSUMMARY for current generator metadata.

```python
import requests
import pandas as pd

# Fetch facilities
response = requests.get("https://api.openelectricity.org.au/v4/facilities/")
df = pd.DataFrame(response.json())

# Filter for NSW solar
nsw_solar = df[
    (df['network_region'] == 'NSW1') &
    (df['fueltech_id'] == 'solar_utility') &
    (df['status_id'].isin(['operating', 'commissioned']))
]

# Extract DUIDs
solar_duids = nsw_solar['duid'].dropna().unique().tolist()
```

**Key fueltech_id values:**
- `'solar_utility'` - Utility-scale solar
- `'wind'` - Wind farms
- `'battery_discharging'` - Battery discharging
- `'battery_charging'` - Battery charging

**Key status_id values:**
- `'operating'` or `'commissioned'` - Currently operational
- `'committed'` - Approved, under construction
- `'commissioning'` - Testing phase
- `'anticipated'` - Proposed

## Common Analysis Patterns

### Curtailment Calculation

```python
# From DISPATCHLOAD data
curtailment = (availability - totalcleared).clip(lower=0)
curtailment_pct = curtailment / availability * 100
```

**Where:**
- `AVAILABILITY` = Maximum capacity the unit could generate
- `TOTALCLEARED` = AEMO dispatch target
- Curtailment = Unused available capacity

### Energy from Power (5-min intervals)

```python
# Convert MW to MWh for 5-minute intervals
energy_mwh = power_mw * (5/60)
```

### Solar Hours Filtering

```python
# Filter for daytime hours (e.g., 10:00-16:00)
solar_hours = df.filter(
    (pl.col("SETTLEMENTDATE").dt.hour() >= 10) &
    (pl.col("SETTLEMENTDATE").dt.hour() < 16)
)
```

### Remove Leap Days

```python
# Remove Feb 29 from analysis
no_leap = df.filter(
    ~((pl.col("SETTLEMENTDATE").dt.month() == 2) &
      (pl.col("SETTLEMENTDATE").dt.day() == 29))
)
```

## Performance Best Practices

1. **Use Polars lazy evaluation** for large datasets
2. **Reduce thread count** to avoid memory issues: `os.environ['POLARS_MAX_THREADS'] = '4'`
3. **Use `.sink_parquet()`** instead of `.collect()` for very large results
4. **Cache downloads** to avoid re-downloading from AEMO
5. **Filter early** in lazy query chains (date ranges, regions, DUIDs)

## Revenue Calculations

### Basic Generator Revenue

```python
# Join SCADA to prices
revenue = (
    scada_df
    .join(price_df, on=["SETTLEMENTDATE", "REGIONID"], how="left")
    .with_columns(
        (pl.col("SCADA") * pl.col("RRP") * (5/60)).alias("revenue_mwh")
    )
)

# Aggregate
total_revenue = revenue.group_by("DUID").agg(pl.sum("revenue_mwh"))
```

### Battery Net Revenue (Dual DUIDs)

```python
# Get discharge revenue
discharge = scada_df.filter(pl.col("DUID").is_in(discharge_duids))
discharge_rev = (
    discharge
    .join(prices, on=["SETTLEMENTDATE", "REGIONID"])
    .with_columns((pl.col("SCADA") * pl.col("RRP") * (5/60)).alias("revenue"))
    .group_by("facility_name").agg(pl.sum("revenue").alias("discharge_revenue"))
)

# Get charge cost (negative)
charge = scada_df.filter(pl.col("DUID").is_in(charge_duids))
charge_cost = (
    charge
    .join(prices, on=["SETTLEMENTDATE", "REGIONID"])
    .with_columns((-1 * pl.col("SCADA") * pl.col("RRP") * (5/60)).alias("cost"))
    .group_by("facility_name").agg(pl.sum("cost").alias("charge_cost"))
)

# Net revenue
net = discharge_rev.join(charge_cost, on="facility_name")
net = net.with_columns(
    (pl.col("discharge_revenue") + pl.col("charge_cost")).alias("net_revenue")
)
```

## Marginal Loss Factors (MLFs)

MLFs adjust revenue based on transmission losses from generator to regional reference node.

**Key characteristics:**
- Static annual values (change July 1st)
- Range: 0.80-1.05 typically
- Available in: `PARTICIPANT_REGISTRATION` or dedicated loss factor tables

**Calculation from settlement data (if tables unavailable):**
```python
# Theoretical revenue at RRP
theoretical = scada * rrp

# Actual settlement (includes MLF adjustment)
# actual_settlement from TRADINGLOAD or similar

# Effective MLF
mlf = actual_settlement / theoretical
```

## Data Quality Considerations

1. **DUDETAILSUMMARY** is outdated - prefer OpenElectricity API
2. **Intervention periods** - filter `INTERVENTION == 0` for spot prices
3. **SCADA noise** - clip negative values for generation
4. **Missing data** - some generators have gaps, handle with `.fill_null()`
5. **Duplicate standing data** - deduplicate when loading static tables

## File Locations (Project-Specific)

All NEMOSIS data cached to: `C:\Users\matts\Documents\Aus research\Nemosis_data`

Helper functions located in: `scripts/utils/nemosis_helpers.py`

## References

- **NEMOSIS GitHub:** https://github.com/UNSW-CEEM/NEMOSIS
- **MMS Data Model:** https://www.mdavis.xyz/mms-guide/
- **OpenElectricity API:** https://api.openelectricity.org.au/
- **AEMO MMS Tables:** https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/market-management-system-mms-data
