"""Split shared household expenses with exact two-decimal arithmetic."""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation, localcontext

CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("999999999999.99")


def _validate_amount(amount: Decimal, label: str = "Amount") -> Decimal:
    """Validate and normalize a finite, non-negative currency amount."""
    if not isinstance(amount, Decimal):
        raise ValueError(f"{label} must be a decimal amount.")
    if not amount.is_finite():
        raise ValueError(f"{label} must be a finite number.")
    if amount < 0:
        raise ValueError(f"{label} cannot be negative.")
    if amount > MAX_AMOUNT:
        raise ValueError(f"{label} cannot exceed {MAX_AMOUNT:,.2f}.")
    try:
        with localcontext() as context:
            context.prec = 32
            normalized = amount.quantize(CENT)
    except InvalidOperation:
        raise ValueError(f"{label} is too large or has an unsupported precision.") from None
    if amount != normalized:
        raise ValueError(f"{label} must have no more than two decimal places.")
    return normalized


def parse_amount(value: str) -> Decimal:
    """Parse a finite, non-negative amount with at most two decimal places."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Enter an amount (for example, 1250 or 1250.50).")
    try:
        amount = Decimal(value.strip())
    except InvalidOperation:
        raise ValueError("Enter a valid amount (for example, 1250 or 1250.50).") from None
    return _validate_amount(amount)


def _validate_people(people: int) -> int:
    if isinstance(people, bool) or not isinstance(people, int) or people < 1:
        raise ValueError("Number of people must be a whole number greater than zero.")
    if people > 10000:
        raise ValueError("Number of people cannot exceed 10,000.")
    return people


def _validate_names(names: list[str] | None, people: int) -> list[str]:
    if names is None:
        return [f"Person {index}" for index in range(1, people + 1)]
    if len(names) != people:
        raise ValueError(f"Provide exactly {people} participant names.")
    cleaned = [name.strip() for name in names]
    if any(not name for name in cleaned):
        raise ValueError("Participant names cannot be empty.")
    if any(len(name) > 60 for name in cleaned):
        raise ValueError("Participant names cannot exceed 60 characters.")
    if len({name.casefold() for name in cleaned}) != len(cleaned):
        raise ValueError("Participant names must be unique.")
    return cleaned


def split_expenses(
    rent: Decimal, food: Decimal, electricity: Decimal, people: int
) -> list[Decimal]:
    """Distribute every cent, assigning remainder cents in participant order."""
    people = _validate_people(people)
    rent = _validate_amount(rent, "Rent")
    food = _validate_amount(food, "Food")
    electricity = _validate_amount(electricity, "Electricity")
    total_cents = sum(int(amount * 100) for amount in (rent, food, electricity))
    base, remainder = divmod(total_cents, people)
    return [
        Decimal(base + (1 if index < remainder else 0)) / 100
        for index in range(people)
    ]


def expense_data(
    rent: Decimal,
    food: Decimal,
    electricity: Decimal,
    people: int,
    participant_names: list[str] | None = None,
) -> dict:
    """Return a JSON-friendly breakdown with exact currency strings."""
    shares = split_expenses(rent, food, electricity, people)
    names = _validate_names(participant_names, people)
    total = sum((_validate_amount(value) for value in (rent, food, electricity)), Decimal("0.00"))
    return {
        "rent": f"{rent:.2f}",
        "food": f"{food:.2f}",
        "electricity": f"{electricity:.2f}",
        "total": f"{total:.2f}",
        "people": people,
        "shares": [f"{share:.2f}" for share in shares],
        "participants": [
            {"name": name, "share": f"{share:.2f}"}
            for name, share in zip(names, shares)
        ],
    }


def expense_report(
    rent: Decimal,
    food: Decimal,
    electricity: Decimal,
    people: int,
    participant_names: list[str] | None = None,
    currency: str = "",
) -> str:
    shares = split_expenses(rent, food, electricity, people)
    names = _validate_names(participant_names, people)
    rent, food, electricity = (
        _validate_amount(value, label)
        for value, label in (
            (rent, "Rent"), (food, "Food"), (electricity, "Electricity")
        )
    )
    total = rent + food + electricity
    unit = f" {currency.strip()}" if currency and currency.strip() else ""
    lines = [
        "", "=" * 48, "HOUSEHOLD EXPENSE BREAKDOWN", "=" * 48,
        f"Rent             : {rent:,.2f}{unit}",
        f"Food             : {food:,.2f}{unit}",
        f"Electricity      : {electricity:,.2f}{unit}",
        "-" * 48,
        f"Total expenses   : {total:,.2f}{unit}",
        f"Number of people : {people}",
        "-" * 48,
    ]
    if len(set(shares)) == 1:
        lines.append(f"Each person pays : {shares[0]:,.2f}{unit}")
    else:
        lines.extend(
            f"{name} pays : {share:,.2f}{unit}"
            for name, share in zip(names, shares)
        )
        lines.append("(Remainder cents are assigned in the listed order.)")
    lines.append("=" * 48)
    return "\n".join(lines)


def prompt_amount(label: str) -> Decimal:
    while True:
        try:
            return parse_amount(input(f"{label}: "))
        except ValueError as exc:
            print(f"Error: {exc}")


def prompt_people() -> int:
    while True:
        try:
            value = int(input("Number of people: ").strip())
            return _validate_people(value)
        except ValueError as exc:
            print(f"Error: {exc}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calculate and split shared household expenses exactly.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--rent", help="Total rent")
    parser.add_argument("--food", help="Total food costs")
    parser.add_argument("--electricity", help="Total electricity bill")
    parser.add_argument("--people", type=int, help="Number of people sharing costs")
    parser.add_argument("--names", help="Comma-separated participant names, in split order")
    parser.add_argument("--currency", default="", help="Currency label, e.g. BDT, USD or EUR")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args(argv)

    values = (args.rent, args.food, args.electricity, args.people)
    if any(value is not None for value in values) and not all(
        value is not None for value in values
    ):
        parser.error("Provide --rent, --food, --electricity and --people together, or use interactive mode.")
    if args.names and args.people is None:
        parser.error("--names requires the four expense options.")

    if all(value is not None for value in values):
        try:
            rent, food, electricity = (
                parse_amount(value) for value in (args.rent, args.food, args.electricity)
            )
            _validate_people(args.people)
            names = [name.strip() for name in args.names.split(",")] if args.names else None
            result = expense_data(rent, food, electricity, args.people, names)
            if args.currency:
                result["currency"] = args.currency.strip()
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(expense_report(rent, food, electricity, args.people, names, args.currency))
        except ValueError as exc:
            parser.error(str(exc))
        return 0

    if args.json or args.names or args.currency:
        parser.error("--json, --names and --currency require all four expense options.")
    print("HOUSEHOLD RENT & EXPENSE CALCULATOR")
    print("Enter amounts without commas. Press Ctrl+C to quit.\n")
    try:
        rent = prompt_amount("Rent")
        food = prompt_amount("Food")
        electricity = prompt_amount("Electricity")
        people = prompt_people()
        names = None
        if input("Add participant names? [y/N]: ").strip().casefold() in {"y", "yes"}:
            while True:
                raw_names = input(f"Enter {people} names separated by commas: ")
                try:
                    names = _validate_names([name.strip() for name in raw_names.split(",")], people)
                    break
                except ValueError as exc:
                    print(f"Error: {exc}")
        print(expense_report(rent, food, electricity, people, names))
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
