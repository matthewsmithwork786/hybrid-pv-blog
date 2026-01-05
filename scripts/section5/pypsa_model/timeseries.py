"""
Time Series Data Loading
========================

Handles loading and generation of price and solar capacity factor data.

Data Sources:
- NEMOSIS: Historical dispatch prices
- Synthetic: Generated data matching documented patterns

LOCAL AGENT NOTES:
------------------
- Real data requires NEMOSIS with cached data
- Synthetic data is used if NEMOSIS unavailable
- Solar CF follows typical NSW daily profile
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import sys

# Try to import NEMOSIS
try:
    from nemosis import dynamic_data_compiler
    NEMOSIS_AVAILABLE = True
except ImportError:
    NEMOSIS_AVAILABLE = False


def load_price_data(
    year: int = 2025,
    region: str = "NSW1",
    cache_path: Optional[str] = None
) -> pd.Series:
    """
    Load wholesale price data for a year.

    Parameters:
    -----------
    year : int
        Year to load
    region : str
        NEM region (NSW1, QLD1, VIC1, SA1, TAS1)
    cache_path : str, optional
        Path to NEMOSIS cache

    Returns:
    --------
    pd.Series
        Hourly prices indexed by datetime
    """
    if NEMOSIS_AVAILABLE and cache_path:
        try:
            return _load_nemosis_prices(year, region, cache_path)
        except Exception as e:
            print(f"NEMOSIS load failed: {e}")
            print("Using synthetic price data...")

    return _generate_synthetic_prices(year)


def _load_nemosis_prices(
    year: int,
    region: str,
    cache_path: str
) -> pd.Series:
    """Load prices from NEMOSIS cache."""
    start = f"{year}/01/01 00:00:00"
    end = f"{year}/12/31 23:55:00"

    data = dynamic_data_compiler(
        start_time=start,
        end_time=end,
        table_name="DISPATCHPRICE",
        raw_data_location=cache_path,
        select_columns=["SETTLEMENTDATE", "REGIONID", "RRP"],
        filter_cols=["REGIONID"],
        filter_values=([region],)
    )

    data["SETTLEMENTDATE"] = pd.to_datetime(data["SETTLEMENTDATE"])

    # Resample to hourly
    hourly = data.set_index("SETTLEMENTDATE")["RRP"].resample("H").mean()

    return hourly


def _generate_synthetic_prices(year: int) -> pd.Series:
    """
    Generate synthetic prices matching NSW patterns.

    Patterns:
    - Low prices (sometimes negative) during midday solar peak
    - High prices during morning and evening peaks
    - Moderate overnight prices
    - Seasonal variation (higher in summer)
    - Random extreme events
    """
    np.random.seed(42 + year)

    # Create hourly index
    start = pd.Timestamp(f"{year}-01-01 00:00:00")
    end = pd.Timestamp(f"{year}-12-31 23:00:00")
    index = pd.date_range(start, end, freq="H")

    # Base price pattern by hour
    hourly_pattern = {
        0: 45, 1: 40, 2: 38, 3: 35, 4: 38, 5: 55,
        6: 80, 7: 95, 8: 85, 9: 60, 10: 40, 11: 25,
        12: 15, 13: 10, 14: 15, 15: 30, 16: 55, 17: 100,
        18: 130, 19: 110, 20: 85, 21: 70, 22: 60, 23: 50
    }

    prices = []
    for dt in index:
        base = hourly_pattern[dt.hour]

        # Seasonal adjustment (higher in summer)
        month = dt.month
        if month in [1, 2, 12]:  # Summer
            seasonal = 1.3
        elif month in [6, 7, 8]:  # Winter
            seasonal = 1.1
        else:
            seasonal = 1.0

        # Weekend adjustment (lower demand)
        if dt.dayofweek >= 5:
            weekend = 0.8
        else:
            weekend = 1.0

        # Random noise
        noise = np.random.normal(0, 15)

        price = base * seasonal * weekend + noise

        # Add extreme events (5% chance)
        if np.random.random() < 0.05:
            if dt.hour in [17, 18, 19]:  # Evening peak
                price = np.random.uniform(500, 3000)
            elif dt.hour in [11, 12, 13, 14]:  # Solar peak
                price = np.random.uniform(-100, -20)

        prices.append(max(-1000, min(15000, price)))  # Cap prices

    return pd.Series(prices, index=index, name="price")


def load_solar_capacity_factors(
    year: int = 2025,
    region: str = "NSW1",
    cache_path: Optional[str] = None
) -> pd.Series:
    """
    Load or generate solar capacity factors.

    Parameters:
    -----------
    year : int
        Year to load
    region : str
        NEM region
    cache_path : str, optional
        Path to cached solar data

    Returns:
    --------
    pd.Series
        Hourly capacity factors (0-1) indexed by datetime
    """
    # Try to load from cache
    if cache_path:
        cf_file = Path(cache_path) / f"solar_cf_{region}_{year}.feather"
        if cf_file.exists():
            data = pd.read_feather(cf_file)
            return data.set_index("timestamp")["capacity_factor"]

    # Generate synthetic
    return _generate_synthetic_solar_cf(year)


def _generate_synthetic_solar_cf(year: int) -> pd.Series:
    """
    Generate synthetic solar capacity factors for NSW.

    Patterns:
    - Zero overnight
    - Bell curve during day, peak at noon
    - Seasonal variation (higher in summer)
    - Weather variation (clouds)
    """
    np.random.seed(123 + year)

    start = pd.Timestamp(f"{year}-01-01 00:00:00")
    end = pd.Timestamp(f"{year}-12-31 23:00:00")
    index = pd.date_range(start, end, freq="H")

    capacity_factors = []

    for dt in index:
        hour = dt.hour

        # Zero at night
        if hour < 6 or hour > 19:
            cf = 0.0
        else:
            # Bell curve peaking at noon
            peak_hour = 12
            spread = 3.5
            base_cf = np.exp(-0.5 * ((hour - peak_hour) / spread) ** 2)

            # Seasonal adjustment
            # Longer days and higher sun in summer
            month = dt.month
            if month in [1, 2, 11, 12]:  # Summer
                seasonal = 1.15
            elif month in [5, 6, 7, 8]:  # Winter
                seasonal = 0.75
            else:
                seasonal = 0.95

            # Weather variation (cloudy days)
            if np.random.random() < 0.2:  # 20% cloudy
                weather = np.random.uniform(0.3, 0.7)
            else:
                weather = np.random.uniform(0.85, 1.0)

            cf = base_cf * seasonal * weather

        # Ensure 0-1 range
        cf = max(0, min(1, cf))
        capacity_factors.append(cf)

    return pd.Series(capacity_factors, index=index, name="capacity_factor")


def get_snapshots(year: int = 2025, freq: str = "H") -> pd.DatetimeIndex:
    """
    Get time snapshots for optimization.

    Parameters:
    -----------
    year : int
        Year for analysis
    freq : str
        Frequency ("H" for hourly, "4H" for 4-hourly for faster runs)

    Returns:
    --------
    pd.DatetimeIndex
        Timestamps for optimization
    """
    start = pd.Timestamp(f"{year}-01-01 00:00:00")
    end = pd.Timestamp(f"{year}-12-31 23:00:00")

    # Remove Feb 29 for leap years (consistent year length)
    snapshots = pd.date_range(start, end, freq=freq)
    snapshots = snapshots[~((snapshots.month == 2) & (snapshots.day == 29))]

    return snapshots


def load_all_timeseries(
    year: int = 2025,
    region: str = "NSW1",
    cache_path: Optional[str] = None
) -> Tuple[pd.DatetimeIndex, pd.Series, pd.Series]:
    """
    Load all required time series data.

    Parameters:
    -----------
    year : int
        Analysis year
    region : str
        NEM region
    cache_path : str, optional
        Path to data cache

    Returns:
    --------
    tuple
        (snapshots, prices, solar_cf)
    """
    print(f"Loading time series data for {region} {year}...")

    snapshots = get_snapshots(year)
    print(f"  Snapshots: {len(snapshots)} hours")

    prices = load_price_data(year, region, cache_path)
    prices = prices.reindex(snapshots).fillna(prices.mean())
    print(f"  Price range: ${prices.min():.0f} to ${prices.max():.0f}/MWh")

    solar_cf = load_solar_capacity_factors(year, region, cache_path)
    solar_cf = solar_cf.reindex(snapshots).fillna(0)
    print(f"  Solar CF range: {solar_cf.min():.2f} to {solar_cf.max():.2f}")

    return snapshots, prices, solar_cf
