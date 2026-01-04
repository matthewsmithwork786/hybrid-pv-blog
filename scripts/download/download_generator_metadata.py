"""
Download generator metadata from OpenElectricity API.

This script fetches current generator metadata including coordinates, capacity,
fuel type, and status. This is used instead of DUDETAILSUMMARY which is often
outdated.

Usage:
    python download_generator_metadata.py

Output:
    CSV file: C:\Users\matts\Documents\Aus research\Nemosis_data\openelectricity_facilities.csv
"""

import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# NEMOSIS data directory
NEMOSIS_DATA_DIR = Path(r"C:\Users\matts\Documents\Aus research\Nemosis_data")

# Ensure directory exists
NEMOSIS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# OpenElectricity API URL
API_URL = "https://api.openelectricity.org.au/v4/facilities/"

# Output file
OUTPUT_FILE = NEMOSIS_DATA_DIR / "openelectricity_facilities.csv"

print("Downloading generator metadata from OpenElectricity API")
print(f"API URL: {API_URL}")
print(f"Output file: {OUTPUT_FILE}")
print("-" * 80)

try:
    # Fetch data from API
    print("Fetching data from API...")
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    # Parse JSON
    data = response.json()
    print(f"✓ Received {len(data)} facility records")

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Display summary statistics
    print("\nData summary:")
    print(f"  Total facilities: {len(df)}")
    print(f"  Unique DUIDs: {df['duid'].nunique()}")

    # Group by fuel type
    if 'fueltech_id' in df.columns:
        print("\nFacilities by fuel type:")
        fuel_counts = df['fueltech_id'].value_counts()
        for fuel, count in fuel_counts.head(10).items():
            print(f"  {fuel}: {count}")

    # Group by region
    if 'network_region' in df.columns:
        print("\nFacilities by region:")
        region_counts = df['network_region'].value_counts()
        for region, count in region_counts.items():
            print(f"  {region}: {count}")

    # Group by status
    if 'status_id' in df.columns:
        print("\nFacilities by status:")
        status_counts = df['status_id'].value_counts()
        for status, count in status_counts.items():
            print(f"  {status}: {count}")

    # Save to CSV
    print(f"\nSaving to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)

    file_size = OUTPUT_FILE.stat().st_size / (1024**2)  # MB
    print(f"✓ Successfully saved metadata")
    print(f"  File size: {file_size:.2f} MB")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")

    # Show column names
    print(f"\nAvailable columns:")
    for i, col in enumerate(df.columns, 1):
        if i % 4 == 0:
            print(f"  {col}")
        else:
            print(f"  {col}", end="")
    print()

except requests.exceptions.RequestException as e:
    print("-" * 80)
    print(f"✗ Error fetching data from API")
    print(f"  Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check internet connection")
    print("  2. Verify OpenElectricity API is accessible:")
    print(f"     {API_URL}")
    print("  3. Check if API endpoint has changed")
    raise

except Exception as e:
    print("-" * 80)
    print(f"✗ Error processing data")
    print(f"  Error: {e}")
    raise

print("\n" + "=" * 80)
print("ALL DOWNLOADS COMPLETE")
print("=" * 80)
print("\nData files location: " + str(NEMOSIS_DATA_DIR))
print("\nYou can now run analysis scripts:")
print("  - scripts/section1/s1_solar_price_curtailment.py")
print("  - scripts/section3/s3_bess_capacity_growth.py")
print("  - scripts/section4/s4_revenue_skew.py")
print("  - etc.")
print("\nFor more information, see scripts/download/README.md")
