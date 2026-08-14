#!/usr/bin/env python3
"""
run_inflation_scenarios.py
======================
Parametric analysis: solves hc.mod + SL.dat for several construction-cost /
inflation multipliers applied to param FC1 (fixed cost of a new PHC unit,
currently hardcoded as 780000 in hc.mod).

IMPORTANT (two things this script works around, without touching your files):
  1. FC1 is assigned directly in hc.mod ('param FC1{L[1]} := 780000;'), not
     read from SL.dat, so GLPK will not accept an override from a .dat file
     ("FC1 needs no data" error - confirmed by testing). There is therefore
     no way to vary FC1 without changing that one line somewhere. This
     script does NOT modify your hc.mod: it reads it, writes a small
     scenario copy with only that line's number rescaled, solves the copy,
     and leaves your original hc.mod on disk exactly as it is.
  2. FC1{L[1]} is a single uniform value applied to EVERY PHC location -
     existing facilities as well as new candidates - so scaling it also
     re-prices the existing network's annual operating cost, not just
     new-construction cost. The CSV separates this out via
     Existing_Network_Repricing_vs_Base (existing count is read from your
     SL.dat's EL[1] set, not hardcoded) so you can see the two effects
     apart.
  3. Your SL.dat currently has U[1]=0 (no new PHC allowed at all), which
     would force New_Facilities=0 in every scenario and hide any real
     effect of FC1 on the investment decision. This script writes a
     scenario copy of SL.dat with U[1] unlocked to a non-binding value
     (see U1_UNLOCK below) so the model can freely choose its cost-optimal
     facility count under each cost scenario. Your original SL.dat is left
     untouched.

Rationale: +10% / +20% / +30% construction-cost stress test shows how
sensitive the ~R$18M investment estimate is to cost overruns.

Requirements: Python 3.7+, glpsol on PATH (Windows: install GLPK for Windows,
https://sourceforge.net/projects/winglpk/, and add its folder to PATH, or set
GLPSOL_PATH below).

Usage:  python run_inflation_scenarios.py
Output: inflation_scenarios.csv
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
SEED = 42                          # fixed so scenarios differ only by FC1
FC1_BASE = 780000
MULTIPLIERS = [1.00, 1.10, 1.20, 1.30]   # baseline, +10%, +20%, +30%
U1_UNLOCK = 15                    # non-binding cap so the model can freely
                                    # pick its cost-optimal facility count;
                                    # your SL.dat currently has U[1]=0, which
                                    # would force 0 new facilities in every
                                    # scenario and hide any real FC1 effect.
OUT_CSV = "inflation_scenarios_results/inflation_scenarios.csv"
GLPSOL_PATH = None                 # e.g. r"C:\glpk\w64\glpsol.exe" if not on PATH
# ---------------------------------------------------------------------------

FC1_LINE_RE = re.compile(r"(param\s+FC1\{L\[1\]\}\s*:=\s*)([\d.]+)(\s*;)")


def find_glpsol():
    if GLPSOL_PATH and Path(GLPSOL_PATH).exists():
        return GLPSOL_PATH
    for cand in ("glpsol", "glpsol.exe"):
        found = shutil.which(cand)
        if found:
            return found
    sys.exit("ERROR: glpsol not found on PATH. Install GLPK, or set GLPSOL_PATH.")


def unlock_u1(data_text, value):
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


def make_scenario_model(model_text, fc1_value):
    new_text, n = FC1_LINE_RE.subn(lambda m: f"{m.group(1)}{fc1_value}{m.group(3)}", model_text)
    if n != 1:
        sys.exit("ERROR: expected exactly one 'param FC1{L[1]} := ...;' line in hc.mod, "
                  f"found {n}. Aborting so nothing is silently mis-edited.")
    return new_text


# Metrics available in hc.mod's existing (unmodified) printf report.
# NOTE: "Fixed cost [Existing]:" (long form) appears once per level (PHC,
# then SHC, then THC) in the network's per-level cost breakdown; re.search
# grabs the FIRST occurrence, which is the PHC block - the level FC1 (and
# this whole analysis) actually applies to. The short form "Fixed cost
# [E]:" used in the top summary is deliberately NOT used here because it
# sums PHC+SHC+THC together, which would mix in FC2/FC3 (untouched by this
# scenario) and make the existing-network repricing figure wrong.
PATTERNS = {
    "Logistic_Cost":       r"Logist cost:\s*\$\s*([\-\d\.]+)",
    "Fixed_Cost_Existing": r"Fixed cost \[Existing\]:\s*\$\s*([\-\d\.]+)",
    "Fixed_Cost_New":      r"Fixed cost \[C\]:\s*\$\s*([\-\d\.]+)",
    "New_Team_Cost":       r"New team cost \[C\]:\s*\$\s*([\-\d\.]+)",
    "Variable_Cost":       r"Variable Cost:\s*\$\s*([\-\d\.]+)",
    "Total_Cost":          r"Total\s+Cost:\s*\$\s*([\-\d\.]+)",
}
NEW_PHC_RE = r"PHC\s+:\s*(\d+)\s+(\d+)\s+([\d\.]+)%"
N_EXISTING_PHC_RE = r"^set EL\[1\] :="


def count_existing_phc(data_text):
    """Count EL[1] members (existing PHC locations) directly from SL.dat,
    instead of assuming a fixed number - keeps the script correct even if
    the data file changes."""
    m = re.search(r"set\s+EL\[1\]\s*:=(.*?);", data_text, re.S)
    return len(m.group(1).split()) if m else None


def run_scenario(glpsol, multiplier, outdir, model_text, data_text, n_existing):
    fc1_value = round(FC1_BASE * multiplier, 2)
    pct_label = f"{round((multiplier - 1) * 100)}pct"

    scen_model = outdir / f"scenario_FC1_{pct_label}.mod"
    scen_model.write_text(make_scenario_model(model_text, fc1_value), encoding="utf-8")

    scen_data = outdir / f"scenario_FC1_{pct_label}.dat"
    scen_data.write_text(unlock_u1(data_text, U1_UNLOCK), encoding="utf-8")

    log_path = outdir / f"run_FC1_{pct_label}.log"
    cmd = [glpsol, "-m", str(scen_model), "-d", str(scen_data), "--seed", str(SEED)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_text = result.stdout + result.stderr
    log_path.write_text(log_text, encoding="utf-8")

    row = {"Multiplier": multiplier, "Cost_Increase_Pct": round((multiplier - 1) * 100),
           "FC1_Value": fc1_value}
    for col, pat in PATTERNS.items():
        m = re.search(pat, log_text)
        row[col] = float(m.group(1)) if m else None

    m = re.search(NEW_PHC_RE, log_text)
    row["New_Facilities"] = int(m.group(1)) if m else None

    # FC1 re-prices EXISTING facilities too (see note in module docstring),
    # so split the existing-network re-pricing effect from the new-build cost
    if row["Fixed_Cost_Existing"] is not None and n_existing:
        row["Existing_Network_Repricing_vs_Base"] = round(
            row["Fixed_Cost_Existing"] - FC1_BASE * n_existing, 2)

    row["Status"] = "FEASIBLE" if row["Total_Cost"] is not None else "INFEASIBLE/ERROR"
    return row


def main():
    glpsol = find_glpsol()
    model_text = Path(MODEL).read_text(encoding="utf-8")
    data_text = Path(DATA).read_text(encoding="utf-8")
    outdir = Path("inflation_scenarios_results")
    outdir.mkdir(exist_ok=True)

    print(f"(Note: U[1] unlocked to {U1_UNLOCK} in scenario copies so the model "
          f"can freely choose its cost-optimal facility count; your SL.dat's own "
          f"U[1] value is left untouched.)\n")

    n_existing = count_existing_phc(data_text)

    rows = []
    for mult in MULTIPLIERS:
        print(f">> Solving with FC1 = {FC1_BASE} x {mult} = {FC1_BASE*mult:,.2f} ...")
        row = run_scenario(glpsol, mult, outdir, model_text, data_text, n_existing)
        rows.append(row)
        print(f"   {row['Status']}  New facilities={row['New_Facilities']}  "
              f"Total cost=${row['Total_Cost']}")

    columns = ["Cost_Increase_Pct", "FC1_Value", "Status", "New_Facilities",
               "Total_Cost", "Fixed_Cost_New", "New_Team_Cost", "Logistic_Cost",
               "Fixed_Cost_Existing", "Existing_Network_Repricing_vs_Base",
               "Variable_Cost"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})

    print(f"\nCSV written to: {OUT_CSV}")
    print(f"Per-scenario model/log files in: {outdir}/")
    

if __name__ == "__main__":
    main()
