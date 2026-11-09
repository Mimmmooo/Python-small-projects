"""Interactive periodic table explorer.

Install dependencies with: pip install -r requirements.txt
"""
from __future__ import annotations

import argparse
import math
from typing import Any

try:
    import periodictable
except ImportError:
    periodictable = None


def require_periodictable() -> Any:
    if periodictable is None:
        raise RuntimeError(
            "Missing dependency 'periodictable'. Run: pip install -r requirements.txt"
        )
    return periodictable


def find_element(query: str) -> Any:
    """Find an element by atomic number, symbol, or full name."""
    table = require_periodictable()
    term = query.strip()
    if not term:
        raise ValueError("Please enter an atomic number, element name, or symbol.")
    if term.isdecimal():
        number = int(term)
        if not 1 <= number <= 118:
            raise ValueError("Atomic number must be between 1 and 118.")
        return table.elements[number]
    for element in table.elements:
        if element.number and (
            element.name.casefold() == term.casefold()
            or element.symbol.casefold() == term.casefold()
        ):
            return element
    raise ValueError(f"No element found for {query!r}.")


def format_property(value: Any, unit: str = "") -> str:
    if value is None:
        return "Not available"
    try:
        if isinstance(value, float) and not math.isfinite(value):
            return "Not available"
    except TypeError:
        pass
    return f"{value}{unit}"


def element_report(element: Any) -> str:
    return "\n".join([
        "", "=" * 42, f"  {element.name.title()} ({element.symbol})",
        "=" * 42, f"Atomic number : {element.number}",
        f"Atomic mass   : {format_property(element.mass, ' u')}",
        f"Density       : {format_property(element.density, ' g/cm³')}",
        "=" * 42,
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Look up chemical elements by number, name, or symbol."
    )
    parser.add_argument(
        "query", nargs="?", help="Atomic number, element name, or symbol"
    )
    args = parser.parse_args(argv)
    try:
        require_periodictable()
    except RuntimeError as exc:
        parser.exit(1, f"Error: {exc}\n")
    if args.query:
        try:
            print(element_report(find_element(args.query)))
            return 0
        except ValueError as exc:
            parser.exit(2, f"Error: {exc}\n")
    print("PERIODIC TABLE EXPLORER")
    print("Enter an atomic number, name, or symbol. Type 'q' to quit.\n")
    while True:
        try:
            query = input("Search element > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0
        if query.casefold() in {"q", "quit", "exit"}:
            print("Goodbye!")
            return 0
        try:
            print(element_report(find_element(query)), "\n")
        except ValueError as exc:
            print(f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
