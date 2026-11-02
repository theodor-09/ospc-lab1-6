# My Measurements

## Warm-up: Running the report

- Command: `ls -l run_report.sh`
- Before: `-rw-r--r--` (no execute permission).
- Fix: `chmod +x run_report.sh`
- After: `-rwxr-xr-x` (the script can now run directly).
- I committed the fix and pushed it to GitHub.

## Worker experiment

- Command: `bash tools/sweep.sh ajhernandezieu2024-design`
- I tested 1, 2, 4, 8, and 16 workers, three times each.
- Average times:
  - 1 worker: 25.63 seconds
  - 2 workers: 13.54 seconds
  - 4 workers: 7.09 seconds
  - 8 workers: 4.82 seconds
  - 16 workers: 4.75 seconds
- The program became faster with more workers, but the improvement was very small after 8 workers.
- My laptop had 10 CPUs available inside Docker.
