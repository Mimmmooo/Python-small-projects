# Python Small Projects 🐍

Two beginner-friendly Python applications with command-line tools, a desktop GUI, input validation, and automated tests.

## Projects

### 🔬 Periodic Table Explorer
Look up any of the 118 elements using its **atomic number**, **chemical symbol**, or **name**. See the element's name, symbol, atomic number, atomic mass, and density (when available).

### 🏠 Household Rent & Expense Calculator
Add **rent**, **food**, and **electricity** costs, then split the total between housemates. Supports exact two-decimal arithmetic, optional participant names, currency labels, named JSON output, strict input validation, and remainder-cent distribution so every share adds up to the exact total.

## Desktop app (GUI)

Launch both projects in a dark-themed, resizable desktop window. The Element Explorer includes searchable element lookup plus an interactive 2D periodic table with all 118 elements, standard positions, color-coded element families, hover labels, and click-to-inspect details. The Expense Splitter supports custom participant names and unequal contributions, calculates fair shares and net balances, and suggests who should repay whom. Leave the payment list blank for a normal equal split. It also supports reset, copies summaries to the clipboard, saves the latest 100 calculations locally in a History tab (with restore, clear, combined-total and average summaries, and full-history CSV export), shows a color-coded expense chart, and exports the expense breakdown and shares to CSV:

```bash
python desktop_app.py
```

The GUI uses Python's standard **Tkinter** library, so no additional pip package is required for the interface. On some Linux distributions, install the OS package `python3-tk` if Tkinter is missing. A graphical desktop session is required. CLI tools still work independently.

## Windows executable

Use the **Build Windows desktop app** workflow under GitHub Actions and select **Run workflow**. After it finishes successfully, download the `PythonLab-Windows` artifact and extract `PythonLab.exe`. The workflow also runs when a GitHub Release is published. Windows builds must be produced on Windows; no executable is committed to the repository.

## Quick start

Python 3.10 or newer is recommended.

```bash
git clone https://github.com/Mimmmooo/Python-small-projects.git
cd Python-small-projects
python -m pip install -r requirements.txt
```

### Periodic table

```bash
python periodic_table.py
python periodic_table.py 8
python periodic_table.py Fe
python periodic_table.py oxygen
python periodic_table.py Fe --json
```

Interactive mode accepts multiple searches until you type `q`, `quit`, or `exit`.

### Expense calculator

```bash
python rent_calculator.py
python rent_calculator.py --rent 6500 --food 2250.50 --electricity 499.50 --people 3
python rent_calculator.py --rent 6500 --food 2250.50 --electricity 499.50 --people 3 --currency BDT
python rent_calculator.py --rent 6500 --food 2250.50 --electricity 499.50 --people 3 --names "Ayon,Mim,Rafi" --currency BDT --json
```

Currency is optional and informational. Use `--currency BDT` (or another label) to show it in the report. Use `--names "Ayon,Mim,Rafi"` to label each person's share in the supplied order. Names must be unique, non-empty, and match the participant count. Enter amounts with a dot for decimals and no thousands separators. Amounts are limited to 999,999,999,999.99 and two decimal places.

## Example

For rent = 6500, food = 2250.50, electricity = 499.50, and 3 people:

```text
Total expenses   : 9,250.00
Number of people : 3
Person 1 pays    : 3,083.34
Person 2 pays    : 3,083.33
Person 3 pays    : 3,083.33
```

Both programs support `--json` for scripts and automation. The calculator represents money as strings in JSON to preserve exact cents; the periodic table reports missing scientific properties as `null`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions also runs the test suite on Python 3.10, 3.12 and 3.13 for pushes and pull requests.

## Project files

| File | Purpose |
| --- | --- |
| `desktop_app.py` | Tkinter desktop interface for both projects |
| `expense_history.py` | Local JSON history storage |
| `expense_settlement.py` | Fair shares and repayment calculations for unequal contributions |
| `periodic_table.py` | Chemical element search and information |
| `periodic_layout.py` | Periodic-table positions, element families and colors |
| `rent_calculator.py` | Shared expense calculation |
| `requirements.txt` | External Python dependency |
| `tests/test_projects.py` | Automated tests |
| `.github/workflows/tests.yml` | Continuous integration |
| `.github/workflows/windows-build.yml` | Windows executable build |

Built as approachable Python learning projects. Contributions and suggestions are welcome.
