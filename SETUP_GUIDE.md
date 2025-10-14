# Setup Guide for New Computer

Based on your codebase analysis, here's what you need to install on your new computer:

## Python Environment Setup

### 1. Install Python
Make sure you have Python 3.7+ installed. You can download it from [python.org](https://python.org) or use a package manager like Homebrew on macOS:
```bash
brew install python
```

### 2. Install Required Python Libraries

Your project uses the following Python libraries:

#### Core Data Analysis Libraries:
- **pandas** - For data manipulation and analysis (used in all your data processing scripts)
- **numpy** - For numerical computations (used in fed_extract_columns.py)

#### Excel/CSV File Support:
- **openpyxl** - For reading/writing Excel files (.xlsx format)
- **xlrd** - For reading older Excel files (.xls format)

#### Built-in Libraries (no installation needed):
- **tkinter** - For GUI file dialogs (comes with Python)
- **pathlib** - For file path handling (comes with Python)
- **datetime** - For date/time operations (comes with Python)
- **os, sys, io** - System utilities (come with Python)

### 3. Installation Commands

Run these commands in your terminal:

```bash
# Install all dependencies at once
pip install -r requirements.txt

# Or install individually:
pip install pandas numpy openpyxl xlrd
```

### 4. Google Colab Specific Code

Note: Your `count_strategies.py` file contains Google Colab specific imports:
```python
from google.colab import files
```

This script is designed to run in Google Colab environment. If you want to run it locally, you'll need to modify the file upload mechanism to use tkinter file dialogs instead.

## Your Project Structure

```
emmiehou.github.io/
├── maze/
│   ├── fed_extract_columns.py      # FED device data processor
│   └── biobserve_extract_columns.py # Biobserve data extractor
├── count_strategies.py             # Strategy counting (Colab version)
├── calculatorpractice.py          # Basic Python practice
├── cs50practice.py                # CS50 practice code
└── [web files: HTML, CSS, JS]
```

## What Each Script Does

1. **fed_extract_columns.py** - Processes FED device files for maze dispenser analysis
2. **biobserve_extract_columns.py** - Extracts specific columns from Biobserve CSV/Excel data
3. **count_strategies.py** - Analyzes behavioral strategies (designed for Google Colab)
4. **calculatorpractice.py** & **cs50practice.py** - Basic Python learning exercises

## Testing Your Setup

After installation, test that everything works:

```bash
python -c "import pandas, numpy, openpyxl, xlrd; print('All libraries imported successfully!')"
```

## Additional Tools You Might Want

- **Jupyter Notebook** - For interactive data analysis: `pip install jupyter`
- **Git** - For version control (if not already installed)
- **VS Code** or your preferred code editor
- **Web browser** - For viewing your GitHub Pages site

## Running Your Scripts

Your data processing scripts use GUI file dialogs, so you can run them directly:

```bash
cd /Users/emmiehou/Documents/emmiehou.github.io/maze
python fed_extract_columns.py
python biobserve_extract_columns.py
```

The scripts will open file dialog windows for you to select input and output files.
