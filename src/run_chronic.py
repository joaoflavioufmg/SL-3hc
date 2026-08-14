#!/usr/bin/env python3
"""
Monte Carlo sensitivity analysis focused on PHC Family Health Strategy
staffing (lack / surplus) under Low / Medium / High chronic burden (MS1).

Key professions whose MS1 changes across scenarios:
  ME1 (Médico da família), EF1 (Enfermeiro), TE1 (Técnico de enfermagem),
  DE1 (Dentista), TD1 (Técnico em saúde bucal)

Runs 3 scenarios × 10 seeds = 30 solves.
Keeps random parameters (PP, O1/O2, D*, TC*) as in the model.
Writes detailed and summary CSVs suitable for charting lack/surplus.
"""

import subprocess
import csv
import sys
from pathlib import Path
from collections import defaultdict
import statistics

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL = "hc.mod"
DATA = "SL.dat"
# WORKDIR = Path(__file__).resolve().parent
WORKDIR = Path("chronic_scenarios_results")
WORKDIR.mkdir(parents=True, exist_ok=True)
N_RUNS = 10
SCENARIOS = {1: "Low", 2: "Medium", 3: "High"}
BASE_SEEDS = [1001, 1017, 1031, 1049, 1063, 1087, 1093, 1103, 1117, 1129]

PROFESSIONS = ["ME1", "EF1", "TE1", "DE1", "TD1"]  # focus set

RESULTS_CSV = WORKDIR / "chronic_staffing_results.csv"
SUMMARY_CSV = WORKDIR / "chronic_staffing_summary.csv"
LONG_CSV = WORKDIR / "chronic_staffing_long.csv"  # tidy format for charts


def write_scenario_dat(scenario: int, path: Path) -> None:
    path.write_text(f"param Scenario := {scenario};\n")


def run_glpk(scenario: int, seed: int, scen_dat: Path) -> str:
    cmd = [
        "glpsol",
        # "-m", str(WORKDIR / MODEL),
        # "-d", str(WORKDIR / DATA),
        "-m", str(MODEL),
        "-d", str(DATA),
        "-d", str(scen_dat),
        "--seed", str(seed),
        "--cuts",
    ]
    result = subprocess.run(
        # cmd, cwd=str(WORKDIR), capture_output=True, text=True, timeout=120
        cmd, capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"  ERROR glpsol rc={result.returncode}", file=sys.stderr)
        print((result.stderr or result.stdout)[-1500:], file=sys.stderr)
        raise RuntimeError("glpsol failed")
    return result.stdout


def parse_csv_summary(output: str) -> dict:
    start = output.find("CSV_SUMMARY_START")
    end = output.find("CSV_SUMMARY_END")
    if start < 0 or end < 0:
        raise ValueError("CSV_SUMMARY block not found")
    data = {}
    for line in output[start:end].splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("CSV_"):
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            try:
                data[k] = float(v) if "." in v else int(v)
            except ValueError:
                data[k] = v
    return data


def main():
    print("=" * 64)
    print("Chronic Burden → PHC Staffing Lack/Surplus (Monte Carlo)")
    print(f"Scenarios: {list(SCENARIOS.values())}   |   Runs/scenario: {N_RUNS}")
    print(f"Focus professions: {', '.join(PROFESSIONS)}")
    print("=" * 64)

    results = []
    scen_dat = WORKDIR / "_tmp_scenario.dat"

    for scen_id, scen_name in SCENARIOS.items():
        write_scenario_dat(scen_id, scen_dat)
        print(f"\n>>> Scenario {scen_id} ({scen_name})")
        for run_idx, seed in enumerate(BASE_SEEDS[:N_RUNS], start=1):
            print(f"  Run {run_idx:2d}/{N_RUNS}  seed={seed} ...", end=" ", flush=True)
            try:
                out = run_glpk(scen_id, seed, scen_dat)
                p = parse_csv_summary(out)
                row = {
                    "scenario_id": scen_id,
                    "scenario_name": scen_name,
                    "run": run_idx,
                    "seed": seed,
                    "PP1": p.get("PP1"),
                    "Unserved": p.get("Unserved"),
                    "TotalCost": p.get("TotalCost"),
                    "NewPHC": p.get("NewPHC"),
                }
                for prof in PROFESSIONS:
                    row[f"l1_{prof}"] = p.get(f"l1_{prof}")
                    row[f"req_{prof}"] = p.get(f"req_{prof}")
                    row[f"cnes_{prof}"] = p.get(f"cnes_{prof}")
                results.append(row)
                # quick feedback: show ME1 lack/surplus
                print(f"l1_ME1={row.get('l1_ME1', 'NA'):+.2f}  req_ME1={row.get('req_ME1', 'NA'):.1f}")
            except Exception as e:
                print(f"FAILED: {e}")
                results.append({
                    "scenario_id": scen_id,
                    "scenario_name": scen_name,
                    "run": run_idx,
                    "seed": seed,
                    "error": str(e),
                })

    if scen_dat.exists():
        scen_dat.unlink()

    if not results:
        print("No results.")
        return

    # ----- Wide results CSV -----
    fieldnames = [
        "scenario_id", "scenario_name", "run", "seed",
        "PP1", "Unserved", "TotalCost", "NewPHC",
    ]
    for prof in PROFESSIONS:
        fieldnames += [f"l1_{prof}", f"req_{prof}", f"cnes_{prof}"]

    with open(RESULTS_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"\nDetailed (wide) results → {RESULTS_CSV}")

    # ----- Long / tidy CSV (ideal for charts: one row per profession per run) -----
    long_rows = []
    for r in results:
        if "error" in r:
            continue
        for prof in PROFESSIONS:
            long_rows.append({
                "scenario_id": r["scenario_id"],
                "scenario_name": r["scenario_name"],
                "run": r["run"],
                "seed": r["seed"],
                "profession": prof,
                "l1": r.get(f"l1_{prof}"),
                "req": r.get(f"req_{prof}"),
                "cnes": r.get(f"cnes_{prof}"),
                "PP1": r.get("PP1"),
                "NewPHC": r.get("NewPHC"),
                "TotalCost": r.get("TotalCost"),
            })

    with open(LONG_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(long_rows[0].keys()))
        w.writeheader()
        w.writerows(long_rows)
    print(f"Tidy (long) results     → {LONG_CSV}")

    # ----- Summary statistics -----
    by_scen = defaultdict(list)
    for r in results:
        if "l1_ME1" in r:
            by_scen[r["scenario_id"]].append(r)

    summary = []
    metrics = []
    for prof in PROFESSIONS:
        metrics += [f"l1_{prof}", f"req_{prof}"]
    metrics += ["PP1", "NewPHC", "TotalCost", "Unserved"]

    for scen_id in sorted(by_scen):
        rows = by_scen[scen_id]
        srow = {
            "scenario_id": scen_id,
            "scenario_name": SCENARIOS[scen_id],
            "n_runs": len(rows),
        }
        for m in metrics:
            vals = [r[m] for r in rows if m in r and isinstance(r[m], (int, float))]
            if vals:
                srow[f"{m}_mean"] = statistics.mean(vals)
                srow[f"{m}_std"] = statistics.stdev(vals) if len(vals) > 1 else 0.0
                srow[f"{m}_min"] = min(vals)
                srow[f"{m}_max"] = max(vals)
        summary.append(srow)

    if summary:
        sum_fields = ["scenario_id", "scenario_name", "n_runs"]
        for m in metrics:
            sum_fields += [f"{m}_mean", f"{m}_std", f"{m}_min", f"{m}_max"]
        sum_fields = [f for f in sum_fields if any(f in r for r in summary)]

        with open(SUMMARY_CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=sum_fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(summary)
        print(f"Summary statistics     → {SUMMARY_CSV}")

        # Console table: mean lack/surplus
        print("\n" + "=" * 64)
        print("MEAN LACK / SURPLUS (l1) by scenario   [negative = shortage]")
        print("=" * 64)
        header = f"{'Scenario':<10}" + "".join(f"{p:>10}" for p in PROFESSIONS)
        print(header)
        print("-" * len(header))
        for s in summary:
            line = f"{s['scenario_name']:<10}"
            for p in PROFESSIONS:
                v = s.get(f"l1_{p}_mean", float("nan"))
                line += f"{v:>+10.2f}"
            print(line)

        print("\nMEAN REQUIRED PROFESSIONALS (req = pop × MS1[scenario])")
        print("-" * len(header))
        for s in summary:
            line = f"{s['scenario_name']:<10}"
            for p in PROFESSIONS:
                v = s.get(f"req_{p}_mean", float("nan"))
                line += f"{v:>10.1f}"
            print(line)

        # CNES is constant (existing stock)
        if results and "cnes_ME1" in results[0]:
            print("\nExisting CNES stock (constant across scenarios/seeds):")
            for p in PROFESSIONS:
                print(f"  {p}: {results[0].get(f'cnes_{p}', 'NA')}")

    print("\nDone. Use the long CSV for boxplots / bar charts of l1 by profession × scenario.")


if __name__ == "__main__":
    main()
