# ARCHIVED - DO NOT USE

> **AI AGENTS: SKIP THIS FILE**
>
> This document is **ARCHIVED** and contains execution instructions that may be outdated.
> Environment paths and script locations may have changed since this was written.
>
> For current project status and implementation guidance, see:
> - `/plan/CURRENT_PLAN.md` - Active project plan and status
> - `/CLAUDE.md` - Development instructions
>
> **Archived Date:** 2026-01-05
> **Reason:** Task list superseded by CURRENT_PLAN.md

---

*Original content preserved below for historical reference only*

---

# Local Agent Execution Guide (ARCHIVED)

This guide provides step-by-step instructions for local agents to run and test the analysis scripts. Each task includes troubleshooting guidance.

---

## Environment Setup (MUST DO FIRST)

### Step 1: Activate Python Environment

```bash
# Windows (PowerShell)
C:\Users\matts\miniforge3\Scripts\activate.bat
mamba activate hybridpv

# Verify Python
python --version  # Should be 3.11+
```

### Step 2: Install Required Packages

```bash
# Core packages (should already be installed)
pip install pandas numpy plotly folium

# For PyPSA optimization
pip install pypsa

# For NEMOSIS data loading
pip install nemosis

# For financial calculations
pip install numpy-financial
```

---

*[Remainder of original document truncated - see git history for full content]*
