"""
NEMOSIS helper functions for Beyond the Solar Curve report.
Provides wrapper functions for common NEMOSIS data operations.
"""

import os
from pathlib import Path
import polars as pl
import pandas as pd
from datetime import datetime
from nemosis import cache_compiler
import requests

# Set Polars thread count to avoid memory issues
os.environ['POLARS_MAX_THREADS'] = str(max(1, (os.cpu_count() or 2) // 2))

# NEMOSIS data directory
NEMOSIS_DATA_DIR = Path(r"C:\Users\matts\Documents\Aus research\Nemosis_data")

# OpenElectricity API
OPENELECTRICITY_API_URL = "https://api.openelectricity.org.au/v4/facilities/"

# Timezone for NEMOSIS data
NEMOSIS_TIMEZONE = "Australia/Brisbane"  # EST, no DST
DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"


def load_cached_dispatchprice(start_date, end_date, region=None):
    """
    Load cached DISPATCHPRICE data from NEMOSIS.

    Parameters:
    -----------
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    region : str, optional
        Filter for specific region (e.g., 'NSW1')

    Returns:
    --------
    pl.DataFrame : Polars DataFrame with price data
    """
    # Convert dates to NEMOSIS format
    start_dt = f"{start_date} 00:00:00"
    end_dt = f"{end_date} 23:59:59"

    # Load cached data using Polars lazy scan
    data_files = list(NEMOSIS_DATA_DIR.glob("PUBLIC_ARCHIVE#DISPATCHPRICE#*.parquet"))

    if not data_files:
        raise FileNotFoundError(
            f"No DISPATCHPRICE cache files found in {NEMOSIS_DATA_DIR}. "
            "Run download scripts first."
        )

    # Lazy load all parquet files
    df = pl.scan_parquet(data_files)

    # Parse datetime
    df = df.with_columns(
        pl.col("SETTLEMENTDATE").str.strptime(pl.Datetime, format=DATETIME_FORMAT)
    )

    # Filter date range
    df = df.filter(
        (pl.col("SETTLEMENTDATE") >= pl.lit(start_date).str.strptime(pl.Datetime, format="%Y-%m-%d")) &
        (pl.col("SETTLEMENTDATE") <= pl.lit(end_date).str.strptime(pl.Datetime, format="%Y-%m-%d"))
    )

    # Filter region if specified
    if region:
        df = df.filter(pl.col("REGIONID") == region)

    return df.collect()


def load_cached_dispatch_scada(start_date, end_date, duids=None):
    """
    Load cached DISPATCH_UNIT_SCADA data from NEMOSIS.

    Parameters:
    -----------
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    duids : list, optional
        Filter for specific DUIDs

    Returns:
    --------
    pl.DataFrame : Polars DataFrame with SCADA data
    """
    data_files = list(NEMOSIS_DATA_DIR.glob("PUBLIC_ARCHIVE#DISPATCH_UNIT_SCADA#*.parquet"))

    if not data_files:
        raise FileNotFoundError(
            f"No DISPATCH_UNIT_SCADA cache files found in {NEMOSIS_DATA_DIR}. "
            "Run download scripts first."
        )

    # Lazy load
    df = pl.scan_parquet(data_files)

    # Parse datetime
    df = df.with_columns(
        pl.col("SETTLEMENTDATE").str.strptime(pl.Datetime, format=DATETIME_FORMAT)
    )

    # Filter date range
    df = df.filter(
        (pl.col("SETTLEMENTDATE") >= pl.lit(start_date).str.strptime(pl.Datetime, format="%Y-%m-%d")) &
        (pl.col("SETTLEMENTDATE") <= pl.lit(end_date).str.strptime(pl.Datetime, format="%Y-%m-%d"))
    )

    # Filter DUIDs if specified
    if duids:
        df = df.filter(pl.col("DUID").is_in(duids))

    return df.collect()


def load_cached_dispatchload(start_date, end_date, duids=None):
    """
    Load cached DISPATCHLOAD data from NEMOSIS.

    Parameters:
    -----------
    start_date : str
        Start date in format 'YYYY-MM-DD'
    end_date : str
        End date in format 'YYYY-MM-DD'
    duids : list, optional
        Filter for specific DUIDs

    Returns:
    --------
    pl.DataFrame : Polars DataFrame with dispatch load data
    """
    data_files = list(NEMOSIS_DATA_DIR.glob("PUBLIC_ARCHIVE#DISPATCHLOAD#*.parquet"))

    if not data_files:
        raise FileNotFoundError(
            f"No DISPATCHLOAD cache files found in {NEMOSIS_DATA_DIR}. "
            "Run download scripts first."
        )

    # Lazy load
    df = pl.scan_parquet(data_files)

    # Parse datetime
    df = df.with_columns(
        pl.col("SETTLEMENTDATE").str.strptime(pl.Datetime, format=DATETIME_FORMAT)
    )

    # Filter date range
    df = df.filter(
        (pl.col("SETTLEMENTDATE") >= pl.lit(start_date).str.strptime(pl.Datetime, format="%Y-%m-%d")) &
        (pl.col("SETTLEMENTDATE") <= pl.lit(end_date).str.strptime(pl.Datetime, format="%Y-%m-%d"))
    )

    # Filter DUIDs if specified
    if duids:
        df = df.filter(pl.col("DUID").is_in(duids))

    return df.collect()


def get_openelectricity_facilities(fueltech_id=None, region=None, status_id=None):
    """
    Fetch generator metadata from OpenElectricity API.

    Parameters:
    -----------
    fueltech_id : str or list, optional
        Filter by fuel technology (e.g., 'solar_utility', 'battery_discharging')
    region : str, optional
        Filter by network region (e.g., 'NSW1')
    status_id : str or list, optional
        Filter by status (e.g., 'operating', 'committed')

    Returns:
    --------
    pd.DataFrame : DataFrame with facility metadata
    """
    # Fetch data from API
    response = requests.get(OPENELECTRICITY_API_URL)
    response.raise_for_status()

    # Convert to DataFrame
    df = pd.DataFrame(response.json())

    # Apply filters
    if fueltech_id:
        if isinstance(fueltech_id, str):
            fueltech_id = [fueltech_id]
        df = df[df['fueltech_id'].isin(fueltech_id)]

    if region:
        df = df[df['network_region'] == region]

    if status_id:
        if isinstance(status_id, str):
            status_id = [status_id]
        df = df[df['status_id'].isin(status_id)]

    return df


def get_solar_duids(region='NSW1'):
    """
    Get list of solar DUIDs for a region using OpenElectricity API.

    Parameters:
    -----------
    region : str
        Network region (default 'NSW1')

    Returns:
    --------
    list : List of DUIDs
    """
    df = get_openelectricity_facilities(
        fueltech_id='solar_utility',
        region=region,
        status_id=['operating', 'commissioned']
    )
    return df['duid'].dropna().unique().tolist()


def get_battery_duids(region='NSW1', include_charging=True):
    """
    Get list of battery DUIDs for a region.

    Parameters:
    -----------
    region : str
        Network region (default 'NSW1')
    include_charging : bool
        Include charging DUIDs (default True)

    Returns:
    --------
    dict : Dictionary with 'discharging' and optionally 'charging' DUID lists
    """
    fueltech = ['battery_discharging']
    if include_charging:
        fueltech.append('battery_charging')

    df = get_openelectricity_facilities(
        fueltech_id=fueltech,
        region=region,
        status_id=['operating', 'commissioned']
    )

    result = {}
    if 'battery_discharging' in df['fueltech_id'].values:
        result['discharging'] = df[df['fueltech_id'] == 'battery_discharging']['duid'].dropna().unique().tolist()

    if include_charging and 'battery_charging' in df['fueltech_id'].values:
        result['charging'] = df[df['fueltech_id'] == 'battery_charging']['duid'].dropna().unique().tolist()

    return result


def calculate_curtailment(dispatchload_df):
    """
    Calculate curtailment from DISPATCHLOAD data.

    Curtailment = max(0, AVAILABILITY - TOTALCLEARED)

    Parameters:
    -----------
    dispatchload_df : pl.DataFrame
        DISPATCHLOAD data with AVAILABILITY and TOTALCLEARED columns

    Returns:
    --------
    pl.DataFrame : DataFrame with added curtailment columns
    """
    return dispatchload_df.with_columns([
        (pl.col("AVAILABILITY") - pl.col("TOTALCLEARED")).clip(lower_bound=0).alias("curtailment_MW"),
        ((pl.col("AVAILABILITY") - pl.col("TOTALCLEARED")).clip(lower_bound=0) / pl.col("AVAILABILITY") * 100)
        .fill_null(0)
        .alias("curtailment_pct")
    ])


def calculate_energy_from_power(power_mw, interval_minutes=5):
    """
    Calculate energy (MWh) from power (MW) for a given interval.

    For 5-minute intervals, uses average power method:
    Energy = Power × (5/60) hours

    Parameters:
    -----------
    power_mw : float or pl.Expr
        Power in MW
    interval_minutes : int
        Interval length in minutes (default 5)

    Returns:
    --------
    float or pl.Expr : Energy in MWh
    """
    hours = interval_minutes / 60
    return power_mw * hours


def filter_solar_hours(df, start_hour=10, end_hour=16):
    """
    Filter DataFrame for solar hours (daytime).

    Parameters:
    -----------
    df : pl.DataFrame
        DataFrame with SETTLEMENTDATE column
    start_hour : int
        Start hour (inclusive, default 10)
    end_hour : int
        End hour (exclusive, default 16)

    Returns:
    --------
    pl.DataFrame : Filtered DataFrame
    """
    return df.filter(
        (pl.col("SETTLEMENTDATE").dt.hour() >= start_hour) &
        (pl.col("SETTLEMENTDATE").dt.hour() < end_hour)
    )


def remove_leap_days(df, date_column="SETTLEMENTDATE"):
    """
    Remove leap day (Feb 29) from DataFrame.

    Parameters:
    -----------
    df : pl.DataFrame
        DataFrame with date column
    date_column : str
        Name of date column (default "SETTLEMENTDATE")

    Returns:
    --------
    pl.DataFrame : DataFrame without leap days
    """
    return df.filter(
        ~((pl.col(date_column).dt.month() == 2) & (pl.col(date_column).dt.day() == 29))
    )
