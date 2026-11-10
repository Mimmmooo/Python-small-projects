# Python Small Projects 🐍

Two beginner-friendly Python applications with command-line tools, a desktop GUI, input validation, and automated tests.

## Projects

### 🔬 Periodic Table Explorer
Look up any of the 118 elements using its **atomic number**, **chemical symbol**, or **name**. See the element's name, symbol, atomic number, atomic mass, and density (when available).

### 🏠 Household Rent & Expense Calculator
Add **rent**, **food**, and **electricity** costs, then split the total between housemates. Supports decimal amounts, prevents invalid inputs and division by zero, and distributes leftover cents so the shares add up to the exact total.

## Desktop app (GUI)\n\nLaunch both projects in one window with tabs, form fields, buttons, and readable results:\n\n```bash\npython desktop_app.py\n```\n\nThe GUI uses Python's standard **Tkinter** library, so no additional pip package is required for the interface. On some Linux distributions, install the OS package `python3-tk` if Tkinter is missing. A graphical desktop session is required. CLI tools still work independently.\n\n## Quick start

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
python rent_calculator.py --rent 6500 --food 2250.50 --electricity 499.50 --people 3 --json
```

The currency is intentionally unspecified, so you can enter amounts in BDT or another currency as long as all amounts use the same currency. Use a dot for decimal values and no thousands separators.

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
| `desktop_app.py` | Tkinter desktop interface for both projects |\n| `periodic_table.py` | Chemical element search and information |
| `rent_calculator.py` | Shared expense calculation |
| `requirements.txt` | External Python dependency |
| `tests/test_projects.py` | Automated tests |
| `.github/workflows/tests.yml` | Continuous integration |

Built as approachable Python learning projects. Contributions and suggestions are welcome.
