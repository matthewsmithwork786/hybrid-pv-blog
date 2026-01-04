"""
Download DISPATCHPRICE data from NEMOSIS.

This script downloads regional price data (RRP) for the NEM from 2018-2025.
Data is cached to the NEMOSIS data directory for use by analysis scripts.

Usage:
    python download_dispatchprice.py

Output:
    Parquet files in C:\Users\matts\Documents\Aus research\Nemosis_data
    Format: PUBLIC_ARCHIVE#DISPATCHPRICE#FILE01#{YYYYMM}010000.parquet
"""

import os
from pathlib import Path
from nemosis import cache_compiler
from datetime import datetime

# NEMOSIS data directory
NEMOSIS_DATA_DIR = Path(r"C:\Users\matts\Documents\Aus research\Nemosis_data")

# Ensure directory exists
NEMOSIS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Set Polars thread count to avoid memory issues
os.environ['POLARS_MAX_THREADS'] = str(max(1, (os.cpu_count() or 2) // 2))

# Date range for download
START_DATE = '2018/01/01 00:00:00'
END_DATE = '2025/12/31 23:59:59'

TABLE_NAME = 'DISPATCHPRICE'

print(f"Downloading {TABLE_NAME} from {START_DATE} to {END_DATE}")
print(f"Output directory: {NEMOSIS_DATA_DIR}")
print("-" * 80)

try:
    cache_compiler(
        start_time=START_DATE,
        end_time=END_DATE,
        table_name=TABLE_NAME,
        raw_data_location=str(NEMOSIS_DATA_DIR),
        fformat='parquet'
    )

    print("-" * 80)
    print(f"✓ Successfully downloaded {TABLE_NAME}")
    print(f"  Files saved to: {NEMOSIS_DATA_DIR}")

    # List downloaded files
    files = list(NEMOSIS_DATA_DIR.glob(f"PUBLIC_ARCHIVE#{TABLE_NAME}#*.parquet"))
    print(f"  Total files: {len(files)}")

    if files:
        # Show file size summary
        total_size = sum(f.stat().st_size for f in files) / (1024**3)  # GB
        print(f"  Total size: {total_size:.2f} GB")
        print(f"  First file: {files[0].name}")
        print(f"  Last file: {files[-1].name}")

except Exception as e:
    print("-" * 80)
    print(f"✗ Error downloading {TABLE_NAME}")
    print(f"  Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check internet connection")
    print("  2. Verify AEMO website is accessible")
    print("  3. Check disk space availability")
    print("  4. Try reducing date range if memory issues occur")
    raise

print("\nNext steps:")
print("  - Run download_dispatch_scada.py")
print("  - Run download_dispatchload.py")
print("  - Run download_generator_metadata.py")
