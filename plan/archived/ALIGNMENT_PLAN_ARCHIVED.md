# ARCHIVED - DO NOT USE

> **AI AGENTS: SKIP THIS FILE**
>
> This document is **ARCHIVED** and represents an outdated project state from an earlier planning phase.
> Do not reference this plan for current implementation decisions.
>
> For current project status and implementation guidance, see:
> - `/plan/CURRENT_PLAN.md` - Active project plan and status
> - `/CLAUDE.md` - Development instructions
>
> **Archived Date:** 2026-01-05
> **Reason:** Project has progressed significantly beyond this plan. Many gaps identified here have been addressed.

---

*Original content preserved below for historical reference only*

---

# Project Alignment Plan: Beyond the Solar Curve (ARCHIVED)

## Executive Summary

This document compares the **original project request** with the **current implementation state**, identifies key divergences and roadblocks, and provides detailed sub-plans to bring the project back on track. Each sub-plan is designed to be executed independently by agents with refreshed context.

---

## Part 1: Gap Analysis

### 1.1 Original Request vs Current State

| Requirement | Original Request | Current State | Gap Severity |
|-------------|------------------|---------------|--------------|
| **Technology Platform** | Shiny (interactive web app) | Quarto (static book) | **MAJOR** |
| **Python Execution** | Live code execution in browser | Disabled (iframe embedding) | **MAJOR** |
| **Code Visibility** | Readers can see analysis code | Code hidden, only outputs shown | **MODERATE** |
| **Section 1** | Solar price collapse + curtailment chart | Placeholder div (no real chart) | **HIGH** |
| **Section 2** | BESS Integration Thesis | **MISSING ENTIRELY** | **CRITICAL** |
| **Section 3** | 4 charts (capacity, map, diagram, revenue buckets) | Placeholder divs (no real charts) | **HIGH** |
| **Section 4** | 3 charts (revenue skew, MLF impact, MLF map) | 2 working charts, 1 missing | **MODERATE** |
| **Section 5** | Strategic Framework + PyPSA modeling | **MISSING ENTIRELY** | **CRITICAL** |
| **Decision Tree** | Interactive dtreeviz diagram | Not implemented | **HIGH** |
| **Data Source** | Real NEMOSIS data | Mostly simulated/example data | **HIGH** |
| **PyPSA Modeling** | Sizing optimization, financial model | Not implemented | **CRITICAL** |

### 1.2 Key Roadblocks Identified

1. **Jupyter/Python 3.14 Incompatibility**: System Python 3.14.2 causes Quarto Python execution to fail. Workaround: iframe embedding of pre-rendered charts.

2. **NEMOSIS Data Access**: Scripts reference Windows paths (`C:\Users\matts\...`) that don't exist in current environment. No actual cached data available.

3. **Technology Mismatch**: Original request specified Shiny for interactivity, but Quarto was implemented instead. Quarto is static-first and doesn't provide the same level of interactivity.

4. **Missing Context Files**: Reference notebooks (`.ipynb` files) and Excel files from original request are not in repository.

5. **PyPSA Integration**: No PyPSA modeling code has been written despite being core to Section 5.

---

*[Remainder of original document truncated for brevity - see git history for full content]*
