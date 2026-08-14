#!/usr/bin/env python3
"""
run_budget_scenarios.py
========================
Parametric analysis: solves hc.mod + SL.dat for several values of param U[1]
(max number of new PHC units allowed), without modifying hc.mod at all.

Rationale: the municipality may not fund the full R$ ~18M / 12-unit plan at
once. Varying U[1] approximates "how many of the 12 units can we afford this
year" and produces a budget-vs-cost-vs-facilities curve for charting.

Refactored to break total cost down by care level (Primary/Secondary/
Tertiary), matching hc.mod's existing "Primary/Secondary/Tertiary Health
Care Cost" report blocks - useful since U[1] only builds new PHC (level 1)
capacity directly, but the extra referred flow changes SHC/THC variable
cost too, which the flat top-level summary alone doesn't show.

Requirements: Python 3.7+, glpsol on PATH (Windows: install GLPK for Windows,
https://sourceforge.net/projects/winglpk/, and add its folder to PATH, or set
GLPSOL_PATH below).

Usage:  python run_budget_scenarios.py
Output: budget_scenarios.csv
"""

import re
import shutil
import subprocess
import sys
import csv
from pathlib import Path

# --------------------------------------------------------------------------- CONFIG
MODEL = "hc.mod"
DATA = "SL.dat"
SEED = 42                      # fixed so scenarios differ only by U[1]
U1_VALUES = [0, 3, 6, 9, 12, 15]
OUT_CSV = "budget_scenarios_results/budget_scenarios.csv"
GLPSOL_PATH = None             # e.g. r"C:\glpk\w64\glpsol.exe" if not on PATH
# ---------------------------------------------------------------------------


def find_glpsol():
    if GLPSOL_PATH and Path(GLPSOL_PATH).exists():
        return GLPSOL_PATH
    for cand in ("glpsol", "glpsol.exe"):
        found = shutil.which(cand)
        if found:
            return found
    sys.exit("ERROR: glpsol not found on PATH. Install GLPK, or set GLPSOL_PATH.")


def set_u1(data_text, value):
    """Return a copy of the .dat text with only 'param U[1]' changed."""
    lines = data_text.splitlines(keepends=True)
    out, in_block = [], False
    for line in lines:
        s = line.strip()
        if not in_block and re.match(r"^param\s+U\s*:=", s):
            in_block = True
            out.append(line)
            continue
        if in_block:
            if s.startswith(";"):
                in_block = False
                out.append(line)
                continue
            if s.split()[:1] == ["1"]:
                out.append(f"1\t{value}\n")
                continue
        out.append(line)
    return "".join(out)


# --------------------------------------------------------------------------- PARSING
# Top "Health Care Plan" summary block
TOP_PATTERNS = {
    "Logistic_Cost":       r"Logist cost:\s*\$\s*([\-\d\.]+)",
    "Fixed_Cost_Existing": r"Fixed cost \[E\]:\s*\$\s*([\-\d\.]+)",
    "Fixed_Cost_New":      r"Fixed cost \[C\]:\s*\$\s*([\-\d\.]+)",
    "New_Team_Cost":       r"New team cost \[C\]:\s*\$\s*([\-\d\.]+)",
    "Variable_Cost":       r"Variable Cost:\s*\$\s*([\-\d\.]+)",
    "Total_Cost":          r"Total\s+Cost:\s*\$\s*([\-\d\.]+)",
}

# Per-level ("Primary/Secondary/Tertiary Health Care Cost") blocks all share
# this same field layout, just with different section headers/totals.
LEVEL_FIELD_PATTERNS = {
    "Logistic":       r"Logistic cost:\s*\$\s*([\-\d\.]+)",
    "Fixed_Existing":  r"Fixed cost \[Existing\]:\s*\$\s*([\-\d\.]+)",
    "Fixed_New":       r"Fixed cost \[New\]:\s*\$\s*([\-\d\.]+)",
    "New_Team":        r"New team cost:\s*\$\s*([\-\d\.]+)",
    "Variable":        r"Variable cost:\s*\$\s*([\-\d\.]+)",
}

LEVELS = [
    ("PHC", r"Primary Health Care Cost \(PHC\):(.*?)Total PHC Cost:\s*\$\s*([\-\d\.]+)"),
    ("SHC", r"Secondary Health Care Cost \(SHC\):(.*?)Total SHC Cost:\s*\$\s*([\-\d\.]+)"),
    ("THC", r"Tertiary Health Care Cost \(THC\):(.*?)Total THC Cost:\s*\$\s*([\-\d\.]+)"),
]

NEW_PHC_RE = r"PHC\s+:\s*(\d+)\s+(\d+)\s+([\d\.]+)%"


def parse_report(log_text):
    row = {}
    for col, pat in TOP_PATTERNS.items():
        m = re.search(pat, log_text)
        row[col] = float(m.group(1)) if m else None

    for level, block_pat in LEVELS:
        m = re.search(block_pat, log_text, re.S)
        body, total = (m.group(1), m.group(2)) if m else ("", None)
        for field, pat in LEVEL_FIELD_PATTERNS.items():
            fm = re.search(pat, body)
            row[f"{level}_{field}"] = float(fm.group(1)) if fm else None
        row[f"{level}_Total"] = float(total) if total is not None else None

    m = re.search(NEW_PHC_RE, log_text)
    if m:
        row["New_Facilities"] = int(m.group(1))
        row["U1_Cap_Reported"] = int(m.group(2))
        row["Facility_Cap_Use_Pct"] = float(m.group(3))
    else:
        row["New_Facilities"] = row["U1_Cap_Reported"] = row["Facility_Cap_Use_Pct"] = None

    return row


def run_scenario(glpsol, u1_value, outdir):
    data_text = Path(DATA).read_text(encoding="utf-8")
    scen_data = outdir / f"scenario_U1_{u1_value}.dat"
    scen_data.write_text(set_u1(data_text, u1_value), encoding="utf-8")

    log_path = outdir / f"run_U1_{u1_value}.log"
    cmd = [glpsol, "-m", MODEL, "-d", str(scen_data), "--seed", str(SEED)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_text = result.stdout + result.stderr
    log_path.write_text(log_text, encoding="utf-8")

    row = {"U1": u1_value}
    row.update(parse_report(log_text))
    row["Status"] = "FEASIBLE" if row["Total_Cost"] is not None else "INFEASIBLE/ERROR"
    return row


def main():
    glpsol = find_glpsol()
    outdir = Path("budget_scenarios_results")
    outdir.mkdir(exist_ok=True)

    rows = []
    for u1 in U1_VALUES:
        print(f">> Solving with U[1] = {u1} ...")
        row = run_scenario(glpsol, u1, outdir)
        rows.append(row)
        print(f"   {row['Status']}  New facilities={row['New_Facilities']}  "
              f"Total cost=${row['Total_Cost']}  "
              f"(PHC ${row['PHC_Total']} | SHC ${row['SHC_Total']} | THC ${row['THC_Total']})")

    columns = ["U1", "Status", "New_Facilities", "Total_Cost",
               "Logistic_Cost", "Fixed_Cost_Existing", "Fixed_Cost_New",
               "New_Team_Cost", "Variable_Cost", "Facility_Cap_Use_Pct"]
    for level, _ in LEVELS:
        columns += [f"{level}_Logistic", f"{level}_Fixed_Existing", f"{level}_Fixed_New",
                    f"{level}_New_Team", f"{level}_Variable", f"{level}_Total"]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})

    print(f"\nCSV written to: {OUT_CSV}")
    print(f"Per-scenario logs in: {outdir}/")


if __name__ == "__main__":
    main()
