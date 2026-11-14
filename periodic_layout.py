"""Standard periodic-table positions and broad element families."""
from __future__ import annotations

CATEGORIES = {
    "alkali metal": {3, 11, 19, 37, 55, 87},
    "alkaline earth metal": {4, 12, 20, 38, 56, 88},
    "transition metal": set(range(21, 31)) | set(range(39, 49)) | set(range(72, 81)) | set(range(104, 113)),
    "post-transition metal": {13, 31, 49, 50, 81, 82, 83, 113, 114, 115, 116},
    "metalloid": {5, 14, 32, 33, 51, 52, 84},
    "reactive nonmetal": {1, 6, 7, 8, 15, 16, 34},
    "halogen": {9, 17, 35, 53, 85, 117},
    "noble gas": {2, 10, 18, 36, 54, 86, 118},
    "lanthanide": set(range(57, 72)),
    "actinide": set(range(89, 104)),
}

CATEGORY_COLORS = {
    "alkali metal": "#ef4444",
    "alkaline earth metal": "#f97316",
    "transition metal": "#eab308",
    "post-transition metal": "#84cc16",
    "metalloid": "#14b8a6",
    "reactive nonmetal": "#22c55e",
    "halogen": "#06b6d4",
    "noble gas": "#3b82f6",
    "lanthanide": "#8b5cf6",
    "actinide": "#d946ef",
}

def element_category(number: int) -> str:
    """Return a broad educational family for an atomic number."""
    for category, members in CATEGORIES.items():
        if number in members:
            return category
    raise ValueError(f"Atomic number must be between 1 and 118, got {number}.")

def periodic_positions() -> dict[int, tuple[int, int]]:
    """Map atomic number to (zero-based row, zero-based column)."""
    positions = {}
    for number, column in ((1, 0), (2, 17)):
        positions[number] = (0, column)
    for number, column in zip(range(3, 11), (0, 1, 12, 13, 14, 15, 16, 17)):
        positions[number] = (1, column)
    for number, column in zip(range(11, 19), (0, 1, 12, 13, 14, 15, 16, 17)):
        positions[number] = (2, column)
    for period, start in ((4, 19), (5, 37)):
        for offset in range(18):
            positions[start + offset] = (period - 1, offset)
    positions[55], positions[56] = (5, 0), (5, 1)
    for offset, number in enumerate(range(72, 87), start=3):
        positions[number] = (5, offset)
    positions[87], positions[88] = (6, 0), (6, 1)
    for offset, number in enumerate(range(104, 119), start=3):
        positions[number] = (6, offset)
    for offset, number in enumerate(range(57, 72), start=3):
        positions[number] = (7, offset)
    for offset, number in enumerate(range(89, 104), start=3):
        positions[number] = (8, offset)
    return positions

def validate_periodic_positions() -> bool:
    positions = periodic_positions()
    return (
        len(positions) == 118
        and set(positions) == set(range(1, 119))
        and len(set(positions.values())) == 118
    )
