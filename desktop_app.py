"""Desktop interface for the two small Python projects (Tkinter)."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from periodic_table import element_report, find_element
from rent_calculator import expense_report, parse_amount


class ProjectApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Python Small Projects")
        self.geometry("700x530")
        self.minsize(560, 430)
        self.configure(bg="#f4f6fa")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#f4f6fa", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(20, 10), font=("Arial", 11))
        style.configure("TFrame", background="#f4f6fa")
        style.configure("TLabel", background="#f4f6fa", font=("Arial", 11))
        style.configure("TButton", padding=(10, 8), font=("Arial", 10))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=18, pady=18)
        periodic_tab = ttk.Frame(notebook, padding=18)
        rent_tab = ttk.Frame(notebook, padding=18)
        notebook.add(periodic_tab, text="Periodic Table")
        notebook.add(rent_tab, text="Rent Calculator")
        self.build_periodic_tab(periodic_tab)
        self.build_rent_tab(rent_tab)

    @staticmethod
    def output(parent: ttk.Frame) -> tk.Text:
        box = tk.Text(
            parent, height=14, wrap="word", font=("Courier", 11),
            bg="#ffffff", fg="#18243a", relief="flat", padx=12, pady=12,
        )
        box.pack(fill="both", expand=True, pady=(12, 0))
        box.configure(state="disabled")
        return box

    @staticmethod
    def show_output(box: tk.Text, text: str) -> None:
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    def build_periodic_tab(self, tab: ttk.Frame) -> None:
        ttk.Label(tab, text="Search by number, symbol, or name").pack(anchor="w")
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=(8, 0))
        query = ttk.Entry(row, font=("Arial", 12))
        query.pack(side="left", fill="x", expand=True, padx=(0, 10))
        result = self.output(tab)

        def search(event=None) -> None:
            try:
                self.show_output(result, element_report(find_element(query.get())))
            except (ValueError, RuntimeError) as exc:
                messagebox.showerror("Element lookup", str(exc), parent=self)

        ttk.Button(row, text="Search", command=search).pack(side="right")
        query.bind("<Return>", search)
        query.focus_set()

    def build_rent_tab(self, tab: ttk.Frame) -> None:
        fields = {}
        for label, default in (
            ("Rent", "6500"),
            ("Food", "2250.50"),
            ("Electricity", "499.50"),
            ("People", "3"),
        ):
            row = ttk.Frame(tab)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=14).pack(side="left")
            entry = ttk.Entry(row, font=("Arial", 11))
            entry.insert(0, default)
            entry.pack(side="left", fill="x", expand=True)
            fields[label] = entry
        result = self.output(tab)

        def calculate() -> None:
            try:
                rent = parse_amount(fields["Rent"].get())
                food = parse_amount(fields["Food"].get())
                electricity = parse_amount(fields["Electricity"].get())
                people = int(fields["People"].get().strip())
                self.show_output(
                    result, expense_report(rent, food, electricity, people)
                )
            except ValueError as exc:
                messagebox.showerror("Invalid expense", str(exc), parent=self)

        ttk.Button(tab, text="Calculate split", command=calculate).pack(
            anchor="e", pady=(12, 0)
        )


if __name__ == "__main__":
    try:
        app = ProjectApp()
        app.mainloop()
    except tk.TclError as exc:
        raise SystemExit(
            f"Cannot start desktop GUI: {exc}. Run on a graphical desktop."
        ) from exc
