# Python Small Projects 🐍

Two beginner-friendly Python command-line applications, upgraded with input validation, useful output, and tests.

## Projects

### 🔬 Periodic Table Explorer
Look up any of the 118 elements using its **atomic number**, **chemical symbol**, or **name**. See the element's name, symbol, atomic number, atomic mass, and density (when available).

### 🏠 Household Rent & Expense Calculator
Add **rent**, **food**, and **electricity** costs, then split the total between housemates. Supports decimal amounts, prevents invalid inputs and division by zero, and distributes leftover cents so the shares add up to the exact total.

## Quick start

Python 3.10 or newer is recommended.

```bash
git clone https://github.com/Mimmmooo/Python-small-projects.git
cd Python-small-projects
python -m pip install -r requirements.txt
```

> If you're reviewing the pull request before merging, switch to the `enhancement/interactive-projects` branch.

### Periodic table

```bash
python periodic_table.py
python periodic_table.py 8
python periodic_table.py Fe
python periodic_table.py oxygen
```

Interactive mode accepts multiple searches until you type `q`, `quit`, or `exit`.

### Expense calculator

```bash
python rent_calculator.py
python rent_calculator.py --rent 6500 --food 2250.50 --electricity 499.50 --people 3
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

## Run tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions also runs the test suite on Python 3.10, 3.12 and 3.13 for pushes and pull requests.

## Project files

| File | Purpose |
| --- | --- |
| `periodic_table.py` | Chemical element search and information |
| `rent_calculator.py` | Shared expense calculation |
| `requirements.txt` | External Python dependency |
| `tests/test_projects.py` | Automated tests |
| `.github/workflows/tests.yml` | Continuous integration |

Built as approachable Python learning projects. Contributions and suggestions are welcome.
