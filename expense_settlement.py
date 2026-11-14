"""Fair expense settlement for groups with unequal payments."""
from __future__ import annotations

from decimal import Decimal
from rent_calculator import split_expenses


def calculate_settlement(total: Decimal, contributions: list[tuple[str, Decimal]]) -> dict:
    """Return fair shares, net balances, and a minimal repayment list."""
    cent = Decimal("0.01")
    if not total.is_finite() or total < 0 or total != total.quantize(cent):
        raise ValueError("Total must be a non-negative amount with at most two decimals.")
    if not contributions:
        raise ValueError("Add at least one participant.")
    names = [name.strip() for name, _ in contributions]
    if any(not name for name in names):
        raise ValueError("Participant names cannot be empty.")
    if len({name.casefold() for name in names}) != len(names):
        raise ValueError("Participant names must be unique.")
    paid = [amount for _, amount in contributions]
    if any(not amount.is_finite() or amount < 0 or amount != amount.quantize(cent) for amount in paid):
        raise ValueError("Payments must be non-negative amounts with at most two decimals.")
    if sum(paid, Decimal("0.00")) != total:
        raise ValueError("Participant payments must add up exactly to the total expenses.")
    shares = split_expenses(total, Decimal("0.00"), Decimal("0.00"), len(contributions))
    balances = [amount - share for amount, share in zip(paid, shares)]
    creditors = [[i, value] for i, value in enumerate(balances) if value > 0]
    debtors = [[i, -value] for i, value in enumerate(balances) if value < 0]
    transfers = []
    ci = di = 0
    while ci < len(creditors) and di < len(debtors):
        amount = min(creditors[ci][1], debtors[di][1])
        transfers.append({"from": names[debtors[di][0]], "to": names[creditors[ci][0]], "amount": f"{amount:.2f}"})
        creditors[ci][1] -= amount
        debtors[di][1] -= amount
        if creditors[ci][1] == 0:
            ci += 1
        if debtors[di][1] == 0:
            di += 1
    participants = [{"name": name, "paid": f"{amount:.2f}", "share": f"{share:.2f}", "net": f"{balance:+.2f}"}
                    for (name, amount), share, balance in zip(contributions, shares, balances)]
    return {"participants": participants, "transfers": transfers}