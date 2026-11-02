# Measurements — theodor-09
nproc: 4

## Task 1: report.py
Before (original, 8.4M rows): 13.67s elapsed, 11.45s user, 2.42s system, 2088632 KB peak. Exit 137 (SIGKILL). oom_kill 1. Table: 887 MiB.
Before (original, 1M rows): 1.75s elapsed, 1.60s user, 0.21s system, 205860 KB peak.
After (fixed, 8.4M rows): 9.38s elapsed, 8.57s user, 0.85s system, 205736 KB peak. Exit 0.

## Task 2: extracts.sh
Before (original): all 6 CSV files had 0 rows. Exit 0 (silent failure).
After (fixed): 3.63s elapsed, 3.94s user, 1.68s system, 8016 KB peak. Exit 0. 8,400,000 total rows.

## Task 3: audit.py
Before (original, 8.4M rows): 70.28s elapsed, 50.32s user, 19.98s system, 635296 KB peak.
After (fixed, 8.4M rows): 14.09s elapsed, 13.54s user, 0.63s system, 635264 KB peak.

## Task 4: segments.py
Before (original, 8.4M rows): 48.02s elapsed, 47.54s user, 0.71s system, 743952 KB peak.
After (fixed, 8.4M rows): 21.88s elapsed, 20.70s user, 1.23s system, 1260948 KB peak.

## Task 5: stats.sh
Before (16 workers, sweep avg): ~38s elapsed, ~106s user, ~45s system.
After (4 workers via nproc): "done with 4 workers". No orphans after kill.
Sweep data in sweep.csv.

## Full pipeline (fixed)
119.62s elapsed, 157.29s user, 55.71s system, 1260436 KB peak.
