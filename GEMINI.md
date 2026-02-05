# uv Project Workflow (Standard)

## Setup / Update deps

```bash
uv sync
```

Creates/updates `uv.lock` and the project venv (usually `./.venv`).

## Run commands (recommended: no activation)

```bash
uv run <command>
# e.g.
uv run pytest
uv run python -m your_module
```

`uv run` will automatically lock + sync as needed.

## Optional: activate the venv (only if you want)

```bash
source .venv/bin/activate
```

Activation is only necessary if you want to run commands without `uv run`.

## Add a dependency to the project (updates `pyproject.toml` + lock)

```bash
uv add <package>
```

## One-off / ad-hoc install (does NOT become a project dependency)

```bash
uv pip install <package>
```

## Note on conda

Avoid mixing an active conda env with a uv project venv; prefer using the project’s `./.venv` via `uv run` / `uv sync`.

---

# Project Status (Updated: 2026-02-02)

## Overview

This project focuses on processing and visualizing crisis emotion label data derived from Excel source files.

## Workflow & Scripts

### 1. Data Processing (`process_data.py`)

Converts raw Excel files into JSON format and merges them based on a unique ID.

- **Input**:
  - `data/choices数据.xlsx`: Annotator choices data.
  - `data/labels数据汇总.xlsx`: Label summaries.
- **Output**:
  - `output/choices数据.json`
  - `output/labels数据汇总.json`
  - `output/merged_by_id.json` (Aggregated data keyed by ID)
- **Command**:
  ```bash
  python process_data.py
  ```

### 2. Visualization (`visualize_choices.py`)

Generates statistical plots based on `output/choices数据.json` to analyze label distribution, annotator tendencies, and crisis levels.

- **Input**: `output/choices数据.json`
- **Output**: Images stored in `plots/` directory.
  - `plot1_overall.png`: Overall normalized distribution of choices.
  - `plot2_by_annotator.png`: Choice distribution breakdown by Annotator (`completed_by`).
  - `plot3_by_crisis.png`: Choice distribution breakdown by Crisis Level (`crisis_level`).
  - `plot4_interaction.png`: Detailed interaction plot (Annotator × Crisis Level).
- **Command**:
  ```bash
  python visualize_choices.py
  ```

## Key Files

- `inspect_excel.py`: Utility script to quickly inspect header structure of Excel files in `data/`.
- `test.py`: Scratchpad script for quick data validations.
- `.gitignore`: Configured to ignore `plots/` and system files.
