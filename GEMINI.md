The project uses uv for package management and virtual environment management.

To activate the virtual environment, run: source .venv/bin/activate

To install new libs, run: uv add <package_name>

To add temporary libs, run: uv pip install --editable <package_name>

NOTE: before you install any lib, make sure you have activated the virtual environment. and before you activate the virtual environment, make sure the conda envs are all deactivated by running: conda deactivate. Use conda info --envs to check if there are any conda envs activated.

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