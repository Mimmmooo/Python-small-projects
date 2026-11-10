"""Modern, dependency-light desktop app for element lookup and shared expenses."""
from __future__ import annotations

import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from periodic_table import element_data, find_element, require_periodictable
from rent_calculator import expense_data, parse_amount

BG = "#0f172a"
PANEL = "#1e293b"
TEXT = "#e2e8f0"
MUTED = "#94a3b8"
ACCENT = "#38bdf8"


class ProjectApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Python Lab • Element Explorer & Expense Splitter")
        self.geometry("1000x700")
        self.minsize(760, 550)
        self.configure(bg=BG)
        self.last_expense = None
        self.setup_styles()
        self.build_header()
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=24, pady=(8, 24))
        self.element_tab = ttk.Frame(self.tabs, padding=18)
        self.expense_tab = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(self.element_tab, text="  Element Explorer  ")
        self.tabs.add(self.expense_tab, text="  Expense Splitter  ")
        self.build_elements()
        self.build_expenses()

    def setup_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("DejaVu Sans", 10))
        style.configure("TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT)
        style.configure("Muted.TLabel", background=PANEL, foreground=MUTED)
        style.configure("Title.TLabel", background=PANEL, foreground=TEXT, font=("DejaVu Sans", 16, "bold"))
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT, padding=(18, 12))
        style.map("TNotebook.Tab", background=[("selected", "#0369a1")])
        style.configure("TEntry", padding=8, fieldbackground="#f8fafc", foreground="#0f172a")
        style.configure("TButton", padding=(14, 9), background="#0284c7", foreground="#ffffff")
        style.map("TButton", background=[("active", "#0369a1")])
        style.configure("Treeview", background="#0f172a", foreground=TEXT, fieldbackground="#0f172a", rowheight=30)
        style.configure("Treeview.Heading", background="#334155", foreground=TEXT)
        style.map("Treeview", background=[("selected", "#0369a1")])

    def build_header(self) -> None:
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="x", padx=26, pady=(22, 10))
        tk.Label(frame, text="PYTHON LAB", font=("DejaVu Sans", 22, "bold"), bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(frame, text="Explore chemistry. Split expenses accurately.", bg=BG, fg=MUTED).pack(anchor="w")

    def build_elements(self) -> None:
        tab = self.element_tab
        ttk.Label(tab, text="Element Explorer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Search by atomic number, name or symbol. Double-click a row to inspect.", style="Muted.TLabel").pack(anchor="w", pady=(3, 12))
        controls = ttk.Frame(tab)
        controls.pack(fill="x")
        self.element_query = tk.StringVar()
        entry = ttk.Entry(controls, textvariable=self.element_query)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(controls, text="Search", command=self.search_elements).pack(side="left")
        ttk.Button(controls, text="Show all", command=self.show_all_elements).pack(side="left", padx=(8, 0))
        entry.bind("<Return>", lambda _: self.search_elements())
        columns = ("number", "symbol", "name", "mass")
        wrapper = ttk.Frame(tab)
        wrapper.pack(fill="both", expand=True, pady=14)
        self.element_tree = ttk.Treeview(wrapper, columns=columns, show="headings", selectmode="browse")
        for key, label, width in (("number", "#", 70), ("symbol", "Symbol", 100), ("name", "Element", 220), ("mass", "Mass (u)", 130)):
            self.element_tree.heading(key, text=label)
            self.element_tree.column(key, width=width, anchor="center" if key != "name" else "w")
        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=self.element_tree.yview)
        self.element_tree.configure(yscrollcommand=scroll.set)
        self.element_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.element_tree.bind("<<TreeviewSelect>>", self.select_element)
        self.element_details = tk.StringVar(value="Select an element to view details.")
        ttk.Label(tab, textvariable=self.element_details, wraplength=800, justify="left").pack(anchor="w", pady=(2, 8))
        self.show_all_elements()

    def show_all_elements(self) -> None:
        self.element_query.set("")
        self.populate_elements("")

    def search_elements(self) -> None:
        self.populate_elements(self.element_query.get().strip())

    def populate_elements(self, query: str) -> None:
        self.element_tree.delete(*self.element_tree.get_children())
        try:
            table = require_periodictable()
            term = query.casefold()
            matches = [
                element for element in table.elements
                if 1 <= element.number <= 118 and (
                    not term or term in element.name.casefold()
                    or term in element.symbol.casefold()
                    or term == str(element.number)
                )
            ]
            for element in matches:
                self.element_tree.insert("", "end", iid=str(element.number), values=(
                    element.number, element.symbol, element.name.title(),
                    f"{element.mass:.4f}" if element.mass is not None else "N/A"
                ))
            self.element_details.set(f"{len(matches)} element(s) found. Select a row for details.")
        except (RuntimeError, ValueError) as exc:
            self.element_details.set(str(exc))
            messagebox.showerror("Element Explorer", str(exc), parent=self)

    def select_element(self, _event=None) -> None:
        selection = self.element_tree.selection()
        if not selection:
            return
        try:
            data = element_data(find_element(selection[0]))
            mass = data["atomic_mass_u"]
            density = data["density_g_cm3"]
            self.element_details.set(
                f'{data["name"]} ({data["symbol"]})  •  Atomic number: {data["atomic_number"]}\n'
                f'Mass: {mass if mass is not None else "N/A"} u  •  '
                f'Density: {density if density is not None else "N/A"} g/cm³'
            )
        except (RuntimeError, ValueError) as exc:
            messagebox.showerror("Element Explorer", str(exc), parent=self)

    def build_expenses(self) -> None:
        tab = self.expense_tab
        ttk.Label(tab, text="Expense Splitter", style="Title.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Every cent is accounted for, even when the total does not divide evenly.", style="Muted.TLabel").pack(anchor="w", pady=(3, 14))
        form = ttk.Frame(tab)
        form.pack(fill="x")
        self.expense_fields = {}
        for row, (name, default) in enumerate((
            ("Rent", "6500"), ("Food", "2250.50"), ("Electricity", "499.50"), ("People", "3")
        )):
            ttk.Label(form, text=name).grid(row=row, column=0, sticky="w", pady=6, padx=(0, 16))
            variable = tk.StringVar(value=default)
            field = ttk.Entry(form, textvariable=variable, width=35)
            field.grid(row=row, column=1, sticky="ew", pady=6)
            field.bind("<Return>", lambda _: self.calculate())
            self.expense_fields[name] = variable
        form.columnconfigure(1, weight=1)
        buttons = ttk.Frame(tab)
        buttons.pack(fill="x", pady=(14, 10))
        ttk.Button(buttons, text="Calculate", command=self.calculate).pack(side="left")
        ttk.Button(buttons, text="Export CSV", command=self.export_csv).pack(side="left", padx=10)
        ttk.Button(buttons, text="Reset", command=self.reset_expenses).pack(side="left")
        self.summary = tk.StringVar(value="Enter your expenses and press Calculate.")
        ttk.Label(tab, textvariable=self.summary, style="Title.TLabel", wraplength=800).pack(anchor="w", pady=(4, 8))
        holder = ttk.Frame(tab)
        holder.pack(fill="both", expand=True)
        self.share_tree = ttk.Treeview(holder, columns=("person", "amount"), show="headings")
        self.share_tree.heading("person", text="Person")
        self.share_tree.heading("amount", text="Amount")
        self.share_tree.column("person", anchor="center")
        self.share_tree.column("amount", anchor="center")
        scrollbar = ttk.Scrollbar(holder, orient="vertical", command=self.share_tree.yview)
        self.share_tree.configure(yscrollcommand=scrollbar.set)
        self.share_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def calculate(self) -> None:
        try:
            amounts = [parse_amount(self.expense_fields[key].get()) for key in ("Rent", "Food", "Electricity")]
            people = int(self.expense_fields["People"].get().strip())
            result = expense_data(*amounts, people)
        except (ValueError, OverflowError) as exc:
            messagebox.showerror("Invalid expense", str(exc), parent=self)
            return
        self.last_expense = result
        self.share_tree.delete(*self.share_tree.get_children())
        for index, share in enumerate(result["shares"], 1):
            self.share_tree.insert("", "end", values=(f"Person {index}", share))
        self.summary.set(f'Total: {result["total"]}   •   {result["people"]} people')

    def reset_expenses(self) -> None:
        for key in self.expense_fields:
            self.expense_fields[key].set("")
        self.last_expense = None
        self.share_tree.delete(*self.share_tree.get_children())
        self.summary.set("Enter your expenses and press Calculate.")

    def export_csv(self) -> None:
        if self.last_expense is None:
            messagebox.showinfo("Export CSV", "Calculate expenses first.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            parent=self, defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            initialfile="expense_split.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(["Category", "Amount"])
                for key in ("rent", "food", "electricity", "total"):
                    writer.writerow([key.title(), self.last_expense[key]])
                writer.writerow([])
                writer.writerow(["Person", "Share"])
                for index, share in enumerate(self.last_expense["shares"], 1):
                    writer.writerow([index, share])
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc), parent=self)
        else:
            messagebox.showinfo("Export complete", f"Saved to:\n{path}", parent=self)


if __name__ == "__main__":
    try:
        ProjectApp().mainloop()
    except tk.TclError as exc:
        raise SystemExit(f"GUI unavailable: {exc}. Start a graphical desktop session.") from exc
