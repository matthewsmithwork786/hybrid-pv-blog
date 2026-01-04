"""
Centralized path management for Beyond the Solar Curve report.
All file paths used across the project are defined here.
"""

from pathlib import Path

# Base directories
PROJECT_ROOT = Path(r"C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Git\Hybrid_PV_Blog")
CONTEXT_ROOT = Path(r"C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context")
NEMOSIS_DATA_ROOT = Path(r"C:\Users\matts\Documents\Aus research\Nemosis_data")
PYPSA_ROOT = Path(r"C:\Users\matts\Documents\Aus research\Gen modelling\PyPSA")

# Project subdirectories
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SECTIONS_DIR = PROJECT_ROOT / "sections"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = DATA_DIR / "outputs"
CACHE_DIR = DATA_DIR / "cache"
ASSETS_DIR = PROJECT_ROOT / "assets"
SKILLS_DIR = PROJECT_ROOT / "skills"

# Output directories by section
SECTION1_OUTPUT = OUTPUTS_DIR / "section1"
SECTION3_OUTPUT = OUTPUTS_DIR / "section3"
SECTION4_OUTPUT = OUTPUTS_DIR / "section4"
SECTION5_OUTPUT = OUTPUTS_DIR / "section5"

# Context files
CONTEXT_NEMOSIS_SKILL = CONTEXT_ROOT / "NEMOSIS_skillv2.docx"
CONTEXT_COMBINED_FILES = CONTEXT_ROOT / "combined_files.txt"
CONTEXT_NEM_GEN_INFO = CONTEXT_ROOT / "NEM Generation Information Oct 2025.xlsx"
CONTEXT_MLF_PROMPT = CONTEXT_ROOT / "NEMOSIS prompt_Curtailment and MLFs.md"

# Context notebooks
CONTEXT_NB_GEN_CURT = CONTEXT_ROOT / "Hybridpv_Gen curt NSW.ipynb"
CONTEXT_NB_GEN_MAP = CONTEXT_ROOT / "Hybridpv_NSWGeneratorMap.ipynb"
CONTEXT_NB_PRICE_SKEW = CONTEXT_ROOT / "hyridpv_pricerevskew.ipynb"

# Context images
CONTEXT_IMG_BESS_GROWTH = CONTEXT_ROOT / "NEM BESS plants MWh by year.png"
CONTEXT_IMG_MODO_DIAGRAM = CONTEXT_ROOT / "Modo BESS Colocated options diagram.png"
CONTEXT_IMG_MODO_MLF = CONTEXT_ROOT / "Modo BESS revenue MLF constraints.jpg"
CONTEXT_IMG_NEM_MAP_MLF = CONTEXT_ROOT / "NEM map MLFs.png"

# PyPSA files
PYPSA_FUNCTIONS = PYPSA_ROOT / "PyPSA_functions.py"
PYPSA_CONFIG = PYPSA_ROOT / "PyPSA_config.py"
PYPSA_INPUTS = PYPSA_ROOT / "inputs" / "config" / "PyPSA_inputs_Aus.xlsm"
PYPSA_CUF_DATA = PYPSA_ROOT / "inputs" / "Chosen plant CUFs_18-24_60min.feather"
PYPSA_PRICE_DATA = PYPSA_ROOT / "inputs" / "NSW QLD price data_2018-24_60min.feather"

# NEMOSIS data tables (cached)
NEMOSIS_DISPATCHPRICE = "DISPATCHPRICE"
NEMOSIS_DISPATCH_SCADA = "DISPATCH_UNIT_SCADA"
NEMOSIS_DISPATCHLOAD = "DISPATCHLOAD"
NEMOSIS_DUDETAILSUMMARY = "DUDETAILSUMMARY"
NEMOSIS_PARTICIPANT_REG = "PARTICIPANT_REGISTRATION"

# OpenElectricity API
OPENELECTRICITY_API_URL = "https://api.openelectricity.org.au/v4/facilities/"


def ensure_output_dirs():
    """Create all output directories if they don't exist."""
    for dir_path in [SECTION1_OUTPUT, SECTION3_OUTPUT, SECTION4_OUTPUT, SECTION5_OUTPUT, CACHE_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_output_path(section, filename):
    """
    Get full output path for a given section and filename.

    Parameters:
    -----------
    section : str
        Section name ('section1', 'section3', 'section4', 'section5')
    filename : str
        Output filename

    Returns:
    --------
    Path : Full path to output file
    """
    section_map = {
        'section1': SECTION1_OUTPUT,
        'section3': SECTION3_OUTPUT,
        'section4': SECTION4_OUTPUT,
        'section5': SECTION5_OUTPUT
    }
    output_dir = section_map.get(section, OUTPUTS_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / filename


def get_nemosis_cache_path(table_name, date_str=None):
    """
    Get expected path for NEMOSIS cached data.

    Parameters:
    -----------
    table_name : str
        NEMOSIS table name (e.g., 'DISPATCHPRICE')
    date_str : str, optional
        Date string in format YYYYMM (e.g., '202401')
        If None, returns the base directory

    Returns:
    --------
    Path : Path to cached data file or directory
    """
    if date_str:
        filename = f"PUBLIC_ARCHIVE#{table_name}#FILE01#{date_str}010000.parquet"
        return NEMOSIS_DATA_ROOT / filename
    else:
        return NEMOSIS_DATA_ROOT
