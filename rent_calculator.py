"""Split shared household expenses with exact two-decimal arithmetic."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation

CENT = Decimal("0.01")


def parse_amount(value: str) -> Decimal:
    """Parse a finite, non-negative amount with at most two decimal places."""
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError("Enter a valid amount (e.g. 1250 or 1250.50).") from None
    if not amount.is_finite() or amount < 0:
        raise ValueError("Amount must be a finite, non-negative number.")
    if amount != amount.quantize(CENT):
        raise ValueError("Use no more than two decimal places.")
    return amount.quantize(CENT)


def split_expenses(
    rent: Decimal, food: Decimal, electricity: Decimal, people: int
) -> list[Decimal]:
    """Distribute all cents; the first few people pay one extra cent if needed."""
    if people < 1:
        raise ValueError("Number of people must be at least 1.")
    for amount in (rent, food, electricity):
        if not amount.is_finite() or amount < 0 or amount != amount.quantize(CENT):
            raise ValueError("Expenses must be non-negative amounts in cents.")
    total_cents = int((rent + food + electricity) * 100)
    base, remainder = divmod(total_cents, people)
    return [
        Decimal(base + (1 if index < remainder else 0)) / 100
        for index in range(people)
    ]


def expense_report(
    rent: Decimal, food: Decimal, electricity: Decimal, people: int
) -> str:
    shares = split_expenses(rent, food, electricity, people)
    total = rent + food + electricity
    lines = [
        "", "=" * 40, "HOUSEHOLD EXPENSE BREAKDOWN", "=" * 40,
        f"Rent             : {rent:,.2f}",
        f"Food             : {food:,.2f}",
        f"Electricity      : {electricity:,.2f}",
        "-" * 40,
        f"Total expenses   : {total:,.2f}",
        f"Number of people : {people}",
        "-" * 40,
    ]
    if len(set(shares)) == 1:
        lines.append(f"Each person pays : {shares[0]:,.2f}")
    else:
        lines.extend(
            f"Person {index} pays    : {share:,.2f}"
            for index, share in enumerate(shares, start=1)
        )
        lines.append("(Extra cents go to the first people.)")
    lines.append("=" * 40)
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
            if value < 1:
                raise ValueError
            return value
        except ValueError:
            print("Error: Enter a whole number greater than zero.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Split shared household expenses.")
    parser.add_argument("--rent", help="Total rent")
    parser.add_argument("--food", help="Total food costs")
    parser.add_argument("--electricity", help="Total electricity bill")
    parser.add_argument("--people", type=int, help="Number of people sharing costs")
    args = parser.parse_args(argv)
    values = (args.rent, args.food, args.electricity, args.people)
    if any(value is not None for value in values) and not all(
        value is not None for value in values
    ):
        parser.error("Provide all four options together, or use interactive mode.")
    if all(value is not None for value in values):
        try:
            rent = parse_amount(args.rent)
            food = parse_amount(args.food)
            electricity = parse_amount(args.electricity)
            print(expense_report(rent, food, electricity, args.people))
        except ValueError as exc:
            parser.error(str(exc))
        return 0
    print("HOUSEHOLD RENT & EXPENSE CALCULATOR")
    print("Enter amounts without commas. Press Ctrl+C to quit.\n")
    try:
        rent = prompt_amount("Rent")
        food = prompt_amount("Food")
        electricity = prompt_amount("Electricity")
        people = prompt_people()
        print(expense_report(rent, food, electricity, people))
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
