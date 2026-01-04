"""
Download DISPATCH_UNIT_SCADA data from NEMOSIS.

This script downloads actual generation/load data (MW) for all generators in the NEM.
Data is cached to the NEMOSIS data directory for use by analysis scripts.

Note: This is a large download (~50+ GB for 2018-2025).
Consider downloading in yearly chunks if memory/disk space is limited.

Usage:
    python download_dispatch_scada.py

Output:
    Parquet files in C:\Users\matts\Documents\Aus research\Nemosis_data
    Format: PUBLIC_ARCHIVE#DISPATCH_UNIT_SCADA#FILE01#{YYYYMM}010000.parquet
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
# For large downloads, consider yearly chunks
START_DATE = '2018/01/01 00:00:00'
END_DATE = '2025/12/31 23:59:59'

TABLE_NAME = 'DISPATCH_UNIT_SCADA'

print(f"Downloading {TABLE_NAME} from {START_DATE} to {END_DATE}")
print(f"Output directory: {NEMOSIS_DATA_DIR}")
print("\n⚠ WARNING: This is a LARGE download (50+ GB)")
print("  Estimated time: 2-4 hours depending on connection speed")
print("  Disk space required: ~60 GB")
print("-" * 80)

# Prompt user confirmation
response = input("Continue with download? (y/n): ")
if response.lower() != 'y':
    print("Download cancelled.")
    exit(0)

try:
    print("\nStarting download...")
    print("Note: NEMOSIS downloads month-by-month, progress will update periodically")
    print("-" * 80)

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

except KeyboardInterrupt:
    print("\n\n✗ Download interrupted by user")
    print("  Partial data has been saved and can be resumed")
    print("  Re-run this script to continue from where it left off")
    exit(1)

except Exception as e:
    print("-" * 80)
    print(f"✗ Error downloading {TABLE_NAME}")
    print(f"  Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check internet connection")
    print("  2. Verify sufficient disk space (60+ GB required)")
    print("  3. Check AEMO website is accessible")
    print("  4. Try downloading in smaller yearly chunks:")
    print("     - Modify START_DATE and END_DATE in script")
    print("     - Download 2018, then 2019, then 2020, etc.")
    raise

print("\nNext steps:")
print("  - Run download_dispatchload.py")
print("  - Run download_generator_metadata.py")
