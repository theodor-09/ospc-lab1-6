# Individual Measurements — ana Lab 1

## Task 1 — Report memory problem

Docker memory limit: 2 GiB.

### Original implementation

| Orders | Elapsed (s) | User (s) | System (s) | Peak memory (KB) |
|---|---:|---:|---:|---:|
| 1,000,000 | 1.19 | 1.24 | 0.14 | 511372 |
| 2,000,000 | 2.05 | 2.08 | 0.22 | 857516 |
| 4,000,000 | 3.91 | 3.79 | 0.37 | 1567584 |
| 8,400,000 | OOM killed | — | — | Exceeded container limit |

The original program created 12 monthly DataFrames and combined them, using too much memory.

### Fixed implementation

| Orders | Elapsed (s) | User (s) | System (s) | Peak memory (KB) |
|---|---:|---:|---:|---:|
| 8,400,000 | 6.03 | 5.71 | 0.52 | 1867592 |

Fix: Removed the unnecessary monthly DataFrame copies and grouped the original DataFrame directly by region and month.

Result: The program completes without being killed.

## Task 2 — Extracting data

Original problem: An incorrect relative path caused empty CSV files. The script also hid errors.

Fix: Used the `DATA` environment variable, removed hidden errors, and added strict Bash error handling.

Validation:
- Sample dataset: 100,000 orders extracted.
- Full dataset: 8,400,000 orders extracted.
- Iberia sample: 25,928 orders.
- Iberia full dataset: 2,183,057 orders.

## Task 3 — Auditing

### Original implementation timing

| Orders | Elapsed (s) | User (s) | System (s) | Peak memory (KB) |
|---|---:|---:|---:|---:|
| 100,000 | 0.59 | 0.69 | 0.15 | 127716 |
| 8,400,000 | 35.74 | 25.88 | 10.11 | 634544 |

### System calls for 100,000 orders

| System call | Calls |
|---|---:|
| openat | 100686 |
| write | 100001 |
| close | 100673 |
| Total | 301360 |

The original implementation repeatedly opens, writes to, and closes the output file. This creates unnecessary system-call overhead.

Kernel CPU share on the full dataset:

10.11 / (25.88 + 10.11) × 100 = 28.1%.

The sample output file was 1,952,269 bytes. With a 128 KiB buffer, this would require approximately 15 buffer-sized writes.

### Fixed audit.py — Measurements

The original implementation opened and closed the output file for every order. The corrected implementation opens the output file once and writes all orders through a 128 KiB buffer.

| Measurement | Original | Fixed |
|---|---:|---:|
| Sample elapsed time | 0.59 s | 0.30 s |
| Sample user CPU time | 0.69 s | 0.52 s |
| Sample system CPU time | 0.15 s | 0.04 s |
| Full elapsed time | 35.74 s | 8.27 s |
| Full user CPU time | 25.88 s | 8.46 s |
| Full system CPU time | 10.11 s | 0.06 s |
| Full peak memory (KB) | 634544 | 634712 |

#### System calls — 100,000 orders

| System call | Before | After |
|---|---:|---:|
| openat | 100686 | 686 |
| write | 100001 | 17 |
| close | 100673 | 673 |
| Total | 301360 | 1376 |

The full audit is approximately 4.3 times faster, reducing elapsed time by 76.9%. The measured system calls decreased by approximately 99.5%.

The corrected program successfully wrote all 8,400,000 orders, and `tools/check.py` reported `PASS audit_2025.csv`.
### Fixed audit.py — Measurements

The original implementation opened and closed the output file for every order. The corrected implementation opens the output file once and writes all orders through a 128 KiB buffer.

| Measurement | Original | Fixed |
|---|---:|---:|
| Sample elapsed time | 0.59 s | 0.30 s |
| Sample user CPU time | 0.69 s | 0.52 s |
| Sample system CPU time | 0.15 s | 0.04 s |
| Full elapsed time | 35.74 s | 8.27 s |
| Full user CPU time | 25.88 s | 8.46 s |
| Full system CPU time | 10.11 s | 0.06 s |
| Full peak memory (KB) | 634544 | 634712 |

#### System calls — 100,000 orders

| System call | Before | After |
|---|---:|---:|
| openat | 100686 | 686 |
| write | 100001 | 17 |
| close | 100673 | 673 |
| Total | 301360 | 1376 |

The full audit is approximately 4.3 times faster, reducing elapsed time by 76.9%. The measured system calls decreased by approximately 99.5%.

The corrected program successfully wrote all 8,400,000 orders, and `tools/check.py` reported `PASS audit_2025.csv`.


## Task 4 — Segment profiling and optimization

The original `segments.py` used `datetime.strptime()` for every order to calculate the quarter. Profiling with `cProfile` on 100,000 orders showed that `strptime()` was called 100,000 times.

We replaced the date parsing with `int(order.order_date[5:7])`, which extracts the month directly from the `YYYY-MM-DD` date string.

### Sample dataset — 100,000 orders

| Measurement | Before | After |
|---|---:|---:|
| Elapsed time (s) | 0.42 | 0.28 |
| User CPU time (s) | 0.66 | 0.52 |
| System CPU time (s) | 0.02 | 0.02 |
| Peak memory (KB) | 132544 | 131252 |

The optimized version reduced elapsed time by approximately 33.3% on the sample dataset.

### Full dataset — Optimized version

| Measurement | Result |
|---|---:|
| Elapsed time (s) | 10.27 |
| User CPU time (s) | 10.49 |
| System CPU time (s) | 0.04 |
| Peak memory (KB) | 743688 |

The optimized version successfully processed the full dataset. `tools/check.py` reported `PASS segments.csv`.
## Task 5 — Parallel worker management and scaling

The original `stats.sh` launched background processes without individually checking their exit status. The corrected version saves each worker PID, waits for every worker, checks failures, and handles interruption signals.

The invalid-input test (`WORKERS=0`) returned exit status 1.

### Original implementation

| Workers | Elapsed time (s) |
|---|---:|
| 1 | 26.33 |
| 16 | 8.34 |

### Fixed implementation

| Workers | Elapsed time (s) |
|---|---:|
| 2 | 13.47 |
| 16 | 7.97 |

The corrected version passed the output checker.

### Worker sweep — Three repetitions

| Workers | Run 1 (s) | Run 2 (s) | Run 3 (s) | Average (s) |
|---|---:|---:|---:|---:|
| 1 | 25.76 | 26.26 | 26.01 | 26.01 |
| 2 | 13.49 | 13.76 | 13.47 | 13.57 |
| 4 | 7.51 | 8.08 | 7.92 | 7.84 |
| 8 | 8.09 | 8.59 | 8.56 | 8.41 |
| 16 | 8.40 | 8.69 | 8.84 | 8.64 |

The best result was with four workers, averaging 7.84 seconds. This was approximately 3.32 times faster than one worker.

Increasing the number of workers beyond four did not improve performance. Additional process overhead and competition for CPU resources may explain this result.

The raw measurements are saved in `sweep.csv`.

