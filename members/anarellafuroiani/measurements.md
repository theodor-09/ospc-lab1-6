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


