"""
Dance KG Explorer — Tkinter UI
--------------------------------
Select any combination of filters from the dropdowns and click Search.
A SPARQL query is built dynamically and results are shown in the table.
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

# Make sure the wrapper is importable when running this file directly
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simple_sparql_wrapper import SimpleDanceKG

# ── Filter definitions ────────────────────────────────────────────────────────
# Each entry: (display label, SPARQL property path, linked class property for schema1:name)
# "direct" properties link via an object → schema1:name
# "datatype" properties compare the literal directly

FILTERS = [
    {
        "label":    "Dance Type",
        "prop":     "dance:hasDanceType",
        "name_prop": "schema1:name",
        "var":      "danceType",
    },
    {
        "label":    "Difficulty",
        "prop":     "dance:hasLearningDifficulty",
        "name_prop": "schema1:name",
        "var":      "difficulty",
    },
    {
        "label":    "Formation",
        "prop":     "dance:hasDanceFormation",
        "name_prop": "schema1:name",
        "var":      "formation",
    },
    {
        "label":    "Age Group",
        "prop":     "dance:hasAgeGroup",
        "name_prop": "schema1:name",
        "var":      "ageGroup",
    },
    {
        "label":    "Origin",
        "prop":     "dance:hasOrigin",
        "name_prop": "schema1:name",
        "var":      "origin",
    },
    {
        "label":    "Music Genre",
        "prop":     "dance:hasAssociatedMusicGenre",
        "name_prop": "schema1:name",
        "var":      "musicGenre",
    },
    {
        "label":    "Health Benefit",
        "prop":     "dance:hasHealthBenefit",
        "name_prop": "schema1:name",
        "var":      "healthBenefit",
    },
    {
        "label":    "Time Period",
        "prop":     "dance:hasTimePeriod",
        "name_prop": "schema1:name",
        "var":      "timePeriod",
    },
]

RESULT_COLUMNS = ["Dance Style", "Dance Type", "Difficulty", "Formation", "Age Group", "Origin"]


# ── Helper: load distinct values for every filter from the KG ─────────────────

def load_filter_options(kg: SimpleDanceKG) -> dict[str, list[str]]:
    options: dict[str, list[str]] = {}
    for f in FILTERS:
        query = f"""
        PREFIX dance: <http://example.org/dance/>
        PREFIX schema1: <http://schema.org/>

        SELECT DISTINCT ?name WHERE {{
          ?record a dance:DanceRecord ;
                  {f['prop']} ?obj .
          ?obj {f['name_prop']} ?name .
        }}
        ORDER BY ?name
        """
        rows = kg.select(query)
        options[f["var"]] = ["(any)"] + [r["name"] for r in rows if r.get("name")]
    return options


# ── Helper: build and run the dynamic SPARQL query ────────────────────────────

def run_query(kg: SimpleDanceKG, selected: dict[str, str], limit: int) -> list[dict]:
    """Build a SPARQL query from the active (non-'(any)') selections."""
    where_blocks = ""
    select_vars = "?styleName ?videoTitle ?videoUrl"

    for f in FILTERS:
        var      = f["var"]
        varName  = f"{var}Name"
        value    = selected.get(var, "(any)")

        if value and value != "(any)":
            safe_val = value.replace("'", "\\'")
            where_blocks += (
                f"  ?record {f['prop']} ?{var} .\n"
                f"  ?{var} {f['name_prop']} ?{varName} .\n"
                f"  FILTER(LCASE(STR(?{varName})) = LCASE('{safe_val}'))\n"
            )
        else:
            where_blocks += (
                f"  OPTIONAL {{\n"
                f"    ?record {f['prop']} ?{var} .\n"
                f"    ?{var} {f['name_prop']} ?{varName} .\n"
                f"  }}\n"
            )
        select_vars += f" ?{varName}"

    query = f"""
    PREFIX dance:   <http://example.org/dance/>
    PREFIX schema1: <http://schema.org/>

    SELECT DISTINCT {select_vars} WHERE {{
      ?record a dance:DanceRecord ;
              dance:hasDanceStyle ?style .
      ?style schema1:name ?styleName .
      OPTIONAL {{
        ?style dance:hasYTLink ?video .
        ?video schema1:title ?videoTitle .
        BIND(REPLACE(STR(?video), "http://example.org/dance/video_", "https://www.youtube.com/watch?v=") AS ?videoUrl)
      }}
{where_blocks}    }}
    ORDER BY ?styleName
    LIMIT {int(limit)}
    """
    return kg.select(query)


# ── Main UI class ─────────────────────────────────────────────────────────────
class DanceKGApp(tk.Tk):
    def __init__(self, kg: SimpleDanceKG, filter_options: dict[str, list[str]]):
        super().__init__()
        self.kg = kg
        self.filter_options = filter_options

        self.title("Dance KG Explorer")
        self.resizable(True, True)
        self.configure(padx=16, pady=16)

        self._build_filter_frame()
        self._build_controls()
        self._build_results_table()

    # ── Filter dropdowns ──────────────────────────────────────────────────────
    def _build_filter_frame(self):
        frame = ttk.LabelFrame(self, text="Filters", padding=10)
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.columnconfigure(0, weight=1)

        self.filter_vars: dict[str, tk.StringVar] = {}

        cols = 4  # dropdowns per row
        for idx, f in enumerate(FILTERS):
            var_key = f["var"]
            sv = tk.StringVar(value="(any)")
            self.filter_vars[var_key] = sv

            col = (idx % cols) * 2
            row = idx // cols

            ttk.Label(frame, text=f["label"]).grid(row=row, column=col, sticky="w", padx=(8, 2), pady=4)
            cb = ttk.Combobox(
                frame,
                textvariable=sv,
                values=self.filter_options.get(var_key, ["(any)"]),
                state="readonly",
                width=18,
            )
            cb.grid(row=row, column=col + 1, sticky="ew", padx=(0, 12), pady=4)
            frame.columnconfigure(col + 1, weight=1)

    # ── Limit + buttons ───────────────────────────────────────────────────────
    def _build_controls(self):
        frame = ttk.Frame(self)
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(frame, text="Max results:").pack(side="left")
        self.limit_var = tk.StringVar(value="50")
        ttk.Spinbox(frame, from_=1, to=500, textvariable=self.limit_var, width=6).pack(side="left", padx=(4, 16))

        ttk.Button(frame, text="Search", command=self._search).pack(side="left", padx=(0, 8))
        ttk.Button(frame, text="Reset filters", command=self._reset).pack(side="left")

        self.status_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.status_var, foreground="gray").pack(side="left", padx=16)

    # ── Results table ─────────────────────────────────────────────────────────
    def _build_results_table(self):
        frame = ttk.Frame(self)
        frame.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Dance Style + video columns + one per filter
        self._all_cols = (
            ["styleName", "videoTitle", "videoUrl"]
            + [f["var"] + "Name" for f in FILTERS]
        )
        display = (
            ["Dance Style", "Video Title", "Video URL"]
            + [f["label"] for f in FILTERS]
        )

        self.tree = ttk.Treeview(frame, columns=self._all_cols, show="headings", height=20)
        for col, disp in zip(self._all_cols, display):
            self.tree.heading(col, text=disp)
            w = 260 if col == "videoTitle" else (300 if col == "videoUrl" else 140)
            self.tree.column(col, width=w, anchor="w", stretch=True)

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Double-click a row → open the YouTube URL in the browser
        self.tree.bind("<Double-1>", self._open_url)

    def _open_url(self, event):
        item = self.tree.focus()
        if not item:
            return
        values = self.tree.item(item, "values")
        url_idx = self._all_cols.index("videoUrl")
        url = values[url_idx] if len(values) > url_idx else ""
        if url and url.startswith("http"):
            webbrowser.open(url)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _search(self):
        selected = {var: sv.get() for var, sv in self.filter_vars.items()}
        try:
            limit = max(1, int(self.limit_var.get()))
        except ValueError:
            limit = 50

        try:
            rows = run_query(self.kg, selected, limit)
        except Exception as exc:
            messagebox.showerror("Query error", str(exc))
            return

        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            values = [row.get(col) or "" for col in self._all_cols]
            self.tree.insert("", "end", values=values)

        active = sum(1 for v in selected.values() if v != "(any)")
        self.status_var.set(f"{len(rows)} result(s) — {active} active filter(s)")

    def _reset(self):
        for sv in self.filter_vars.values():
            sv.set("(any)")
        self.status_var.set("")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading knowledge graph...")
    kg = SimpleDanceKG()
    print("Loading filter options from KG...")
    filter_options = load_filter_options(kg)
    print("Launching UI...")
    app = DanceKGApp(kg, filter_options)
    app.mainloop()

