# Measurements — anarellafuroiani

## Warm-up: File Permissions

Command: ls -l run_report.sh

Result: -rwxr-xr-x

The script already had execute permission for the owner, group, and others. Thats why ./run_report.sh was able to execute successfully. The permission issue had already been fixed in the team repository.

## Task 1: Generating the Report — Memory

### Full dataset (8.4 million orders)

- Dfe size: 887 MiB
- Container memory limit: 2 GiB
- Exit status: 137 (SIGKILL)
- memory.events: oom = 1, oom_kill = 1
- Result: report.py was killed by the kernel due to insufficient memory.

### Memory experiment

| Orders | DataFrame (MiB) | Peak memory (KB) | Elapsed (s) | User (s) | System (s) |
|---|---:|---:|---:|---:|---:|
| 1,000,000 | 106 | 505696 | 2.03 | 2.54 | 0.25 |
| 2,000,000 | 211 | 856884 | 3.64 | 4.01 | 0.41 |
| 4,000,000 | 423 | 1572628 | 6.92 | 6.99 | 0.68 |

### Interpretation

Peak(RES) memory increases almost linearly with the number of orders. Its important to note that it is much larger than the DataFrame size since Python uses extra memory for temporary objects and intermediate calculations.

Estimated peak memory for 8.4m orders: approx 3 GB, exceeding the container's 2 gb limit.

### Output buffering experiment

Command: python3 steps/report.py | tee /tmp/report.log

Result: none/empty

Explanation: Standard output is buffered when sent through a pipe. The process was killed before Python flushed its output buffer, so tee did not receive the printed message.

## Task 2: Extracting Data

- Command: bash steps/extracts.sh
- Script exit status: 0
- Result: All files were empty (0 bytes).
- Cause: The relative path ../data/sales_2025.csv is incorrect when the working directory is ~/data/out/extracts.
- Actual input file: ~/data/sales_2025.csv
- grep error: No such file or directory.
- Pipeline exit statuses: 2 0 0 (grep failed; cut and wc succeeded).
- The script hides grep's error using 2>/dev/null.
- The final echo command succeeds, so the script reports status 0.
- Solution: Use the correct input path and add set -euo pipefail to detect failures.

## Task 3: Audit 
- Dataset: 1,000 orders.
- Original script: 1,686 openat, 1,673 close, 1,001 write calls.
- Optimized script: 686 openat, 673 close, 2 write calls.
- Ssystem calls decreased from 4360 to 1361.
- Original elapsed time: 0.36 ; optimized version reduced it to 0.29
- Original system CPU time: 0.10 s; optimized: 0.05 s.
- Optimized output: 1,000 lines verified with wc -l.
- The original script opened and closed the file for row, with the optimized version we opened the file just once, reducing overhead and allowing buffered writes.
- However buffered output may lose recent unwritten data if the program crashes.


## Task 4: Segmenting Orders — Profiling and Optimization

- Dataset: 100,000 orders.
- Tool: `cProfile`, sorted by cumulative time.
- Bottleneck: `datetime.strptime()` was called 100,000 times.
- Original elapsed time: 0.77s.
- Optimized elapsed time: 0.53s.
- Original user CPU time: 1.52 s; optimized: 1.26 s.
- Original system CPU time: 0.03 s; optimized: 0.06 s.
- Og peak memory: 132,848 KB; optimized: 132,688 KB.
- Optimization: Replaced full date parsing with direct month extraction
- Verification: `diff` returned exit status 0, confirming identical outputs for the test dataset.
- Therefore deleting date parsing improved execution time while preserving the results. 

## Task 5: Computing the Statistics

### Problem 1: Worker Count

The original stats.sh uses 16 workers by default, regardless of the available CPU resources.

### Worker Experiment

| Workers | Elapsed (s) | User (s) | System (s) | Speedup |
|---|---:|---:|---:|---:|
| 1 | 35.20 | 35.93 | 0.79 | 1.00 |
| 2 | 18.63 | 36.95 | 0.99 | 1.89 |
| 4 | 10.57 | 40.99 | 1.49 | 3.33 |
| 8 | 6.34 | 45.03 | 1.61 | 5.55 |
| 16 | 5.90 | 51.12 | 2.74 | 5.97 |

### Interpretation

- Increasing workers reduced elapsed time from 35.20 s to 5.90 s.
- User CPU time increased from 35.93 s to 51.12 s.
- The improvement from 8 to 16 workers was small which demonstrates diminishing returns.
- 16 workers achieved the shortest elapsed time, but 8 workers required fewer processes for similar performance.
- Fix: Replaced the fixed default of 16 workers with the available CPU count using nproc.

### Problem 2: Orphan Processes

- Ran stats.sh and interrupted it using Ctrl+C.
- The original script left stats_worker.py running with PID 679 and PPID 1.
- This showed that the background worker continued after its parent shell terminated.
- Fix: Added a trap for SIGINT and SIGTERM, stored worker PIDs using $!, and used kill and wait during cleanup.
- Verification: After interrupting the modified script, ps showed no remaining stats_worker.py processes.

### Conclusion

The original script used a fixed number of workers and didn’t clean up background processes. Now, with the new version, it selects workers based on available CPUs and terminates tracked workers when interrupted. 

