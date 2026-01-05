"""
Download missing NEMOSIS data for 2018-2024 analysis

This script downloads the missing DISPATCHPRICE and DISPATCHLOAD data
needed for the solar price curtailment analysis.

Usage:
    python download_missing_data.py
"""

from nemosis import cache_compiler
from pathlib import Path
from datetime import datetime
import time

# Data directory
NEMOSIS_DATA_DIR = Path(r"C:\Users\matts\Documents\Aus research\Nemosis_data")

# Ensure directory exists
NEMOSIS_DATA_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("Downloading Missing NEMOSIS Data (2018-2024)")
print("=" * 80)

# Download configuration
data_ranges = [
    # Year 2018-2023 DISPATCHPRICE (missing early years)
    {"table": "DISPATCHPRICE", "start": "2018/01/01 00:00:00", "end": "2023/12/31 23:59:59", "format": "parquet"},
    # Year 2018-2023 DISPATCHLOAD (missing early years)  
    {"table": "DISPATCHLOAD", "start": "2018/01/01 00:00:00", "end": "2023/12/31 23:59:59", "format": "feather"},
]

print(f"\nDownload plan:")
print(f"  - Data directory: {NEMOSIS_DATA_DIR}")
print(f"  - Tables to download: {len(data_ranges)}")
print(f"  - Estimated time: 10-15 minutes per table year range")
print(f"  - Total files: {len(data_ranges)}")

print("\n" + "=" * 80)
print("Starting downloads...")
print("=" * 80)

success_count = 0
failed_downloads = []

for i, config in enumerate(data_ranges, 1):
    table_name = config["table"]
    start_time = config["start"]
    end_time = config["end"]
    file_format = config["format"]
    
    print(f"\n[{i}/{len(data_ranges)}] Downloading {table_name}: {start_time} to {end_time}")
    print(f"  Format: {file_format}")
    
    try:
        start = time.time()
        
        cache_compiler(
            start_time=start_time,
            end_time=end_time,
            table_name=table_name,
            raw_data_location=str(NEMOSIS_DATA_DIR),
            fformat=file_format
        )
        
        elapsed = time.time() - start
        print(f"  [OK] Completed in {elapsed:.1f} seconds")
        success_count += 1
        
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        failed_downloads.append({
            "table": table_name,
            "range": f"{start_time} to {end_time}",
            "error": str(e)
        })

print("\n" + "=" * 80)
print("DOWNLOAD SUMMARY")
print("=" * 80)

print(f"\nSuccessful downloads: {success_count}/{len(data_ranges)}")
print(f"Failed downloads: {len(failed_downloads)}")

if failed_downloads:
    print("\nFailed downloads:")
    for failure in failed_downloads:
        print(f"  - {failure['table']} ({failure['range']}): {failure['error']}")
else:
    print("\n[OK] All downloads completed successfully!")

print(f"\nData location: {NEMOSIS_DATA_DIR}")
print("\nYou can now run analysis scripts:")
print("  python scripts/section1/s1_solar_price_curtailment.py")

print("\n" + "=" * 80)
print("Download process complete!")
print("=" * 80)