#!/usr/bin/env python3
"""
monte_carlo.py
================
Monte Carlo / seed-robustness check for the unconstrained model
(hc.mod + SL.dat).

Several parameters are drawn stochastically inside hc.mod itself, using
GLPK's --seed to control the draw:
  - TC1{I,L[1]}      travel cost per patient, demand point -> PHC ($/min)
  - O1{L[1]}, O2{L[2]}  referral proportions PHC->SHC and SHC->THC
  - PP{P}            proportion of chronic (p=1) vs acute (p=2) patients

Running the SAME model+data across 30 different seeds re-draws all of
these together and shows how much the reported total cost (and facility
count) actually depends on that randomness, vs. being a stable result of
the optimization itself.

"Unconstrained" here means U[1] is left exactly as given in SL.dat (12 -
already the model's own cost-optimal facility count from the deterministic
analysis, i.e. non-binding); nothing else is overridden.

Requirements: Python 3.8+ (uses statistics.NormalDist - stdlib only, no
extra packages), glpsol on PATH (Windows: install GLPK for Windows,
https://sourceforge.net/projects/winglpk/, and add its folder to PATH, or
set GLPSOL_PATH below).

Usage:  python monte_carlo.py
Output: monte_carlo_runs.csv     (one row per seed - for histograms/scatter)
        monte_carlo_summary.csv  (mean, stdev, 95% CI - one row)
"""

import csv
import shutil
import subprocess
import sys
import statistics
from pathlib import Path

# --------------------------------------------------------------------------- CONFIG
MODEL = "hc.mod"
DATA = "SL.dat"
N_SEEDS = 30
SEEDS = list(range(1, N_SEEDS + 1))     # 30 distinct seeds -> 30 independent draws
CONFIDENCE = 0.95
RUNS_CSV = "monte_carlo_results/monte_carlo_runs.csv"
SUMMARY_CSV = "monte_carlo_results/monte_carlo_summary.csv"
GLPSOL_PATH = None                      # e.g. r"C:\glpk\w64\glpsol.exe" if not on PATH
# ---------------------------------------------------------------------------

TOTAL_COST_RE = r"Total\s+Cost:\s*\$\s*([\-\d\.]+)"
NEW_PHC_RE = r"PHC\s+:\s*(\d+)\s+(\d+)\s+([\d\.]+)%"


def find_glpsol():
    if GLPSOL_PATH and Path(GLPSOL_PATH).exists():
        return GLPSOL_PATH
    for cand in ("glpsol", "glpsol.exe"):
        found = shutil.which(cand)
        if found:
            return found
    sys.exit("ERROR: glpsol not found on PATH. Install GLPK, or set GLPSOL_PATH.")


def run_seed(glpsol, seed, outdir):
    import re
    log_path = outdir / f"run_seed{seed}.log"
    cmd = [glpsol, "-m", MODEL, "-d", DATA, "--seed", str(seed)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_text = result.stdout + result.stderr
    log_path.write_text(log_text, encoding="utf-8")

    cost_m = re.search(TOTAL_COST_RE, log_text)
    phc_m = re.search(NEW_PHC_RE, log_text)
    return {
        "Seed": seed,
        "Total_Cost": float(cost_m.group(1)) if cost_m else None,
        "New_Facilities": int(phc_m.group(1)) if phc_m else None,
        "Status": "FEASIBLE" if cost_m else "INFEASIBLE/ERROR",
    }


def main():
    glpsol = find_glpsol()
    outdir = Path("monte_carlo_results")
    outdir.mkdir(exist_ok=True)

    rows = []
    for seed in SEEDS:
        print(f">> Solving seed={seed} ...")
        row = run_seed(glpsol, seed, outdir)
        rows.append(row)
        print(f"   {row['Status']}  Total cost=${row['Total_Cost']}  "
              f"New facilities={row['New_Facilities']}")

    with open(RUNS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Seed", "Status", "Total_Cost", "New_Facilities"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nPer-seed CSV written to: {RUNS_CSV}")

    costs = [r["Total_Cost"] for r in rows if r["Total_Cost"] is not None]
    n_failed = len(rows) - len(costs)
    if n_failed:
        print(f"WARNING: {n_failed} seed(s) were infeasible/errored - excluded from stats.")

    if len(costs) < 2:
        sys.exit("ERROR: fewer than 2 feasible runs - cannot compute distribution stats.")

    n = len(costs)
    mean = statistics.mean(costs)
    stdev = statistics.stdev(costs)          # sample stdev (n-1)
    sem = stdev / (n ** 0.5)                 # standard error of the mean
    z = statistics.NormalDist().inv_cdf(0.5 + CONFIDENCE / 2)  # e.g. 1.959964 for 95%
    ci_lo, ci_hi = mean - z * sem, mean + z * sem

    summary = {
        "N_Seeds": n,
        "Mean_Total_Cost": round(mean, 2),
        "StdDev_Total_Cost": round(stdev, 2),
        "CoefVar_Pct": round(100 * stdev / mean, 4),
        "SEM": round(sem, 2),
        "Confidence_Level": CONFIDENCE,
        "CI_Lower": round(ci_lo, 2),
        "CI_Upper": round(ci_hi, 2),
        "Min_Total_Cost": round(min(costs), 2),
        "Max_Total_Cost": round(max(costs), 2),
    }
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary.keys()))
        w.writeheader()
        w.writerow(summary)

    print(f"Summary CSV written to: {SUMMARY_CSV}\n")
    print("=== Total cost distribution across seeds ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
