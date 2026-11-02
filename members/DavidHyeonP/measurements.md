# Measurements — DavidHyeonP

## Task 1: Reporting

### Before the fix
- Sample (100,000 orders): 21.09 s elapsed, 13.88 s user, 4.49 s system, 175,284 KB peak memory.
- Full dataset: 89.08 s elapsed, 64.71 s user, 25.28 s system, 2,143,632 KB peak memory.
- The original full-data process was terminated by signal 9.

### Diagnosis and fix
The original reporting script loaded the entire 8.4-million-row dataset into memory at once. This caused excessive memory consumption, and the process was terminated by the operating system.

The fix changed the script to process the dataset in smaller chunks rather than loading everything into memory at once. This reduced peak memory usage significantly.

### After the fix
- Full dataset (8.4 million orders): 39.09 s elapsed, 33.76 s user, 6.01 s system, 190,932 KB peak memory.
- Successfully processed all 8.4 million orders.

## Task 2: Regional extracts

### Before the fix
- All six regional output files contained zero rows.
- The script used an incorrect relative path to the input CSV.
- Error messages were suppressed with `2>/dev/null`, so the script reported completion despite failing to find the input file.

### Diagnosis and fix
The script changed directory to the output folder before accessing the input dataset. Its relative path was therefore incorrect.

The fix used the `DATA` environment variable to reference the input file directly, wrote outputs to the specified `OUT` directory, and enabled error handling with `set -euo pipefail`.

### After the fix
All six regional files were generated successfully from the full dataset.

| Region | Rows generated |
|---|---:|
| Benelux | 1,006,912 |
| DACH | 1,846,894 |
| France | 1,345,118 |
| Iberia | 2,183,057 |
| Italy | 1,178,032 |
| Nordics | 839,987 |

All six outputs passed `tools/check.py`.

## Task 3: Auditing

### Before the fix
Dataset: 8,400,000 orders

- Elapsed time: 422.68 s
- User CPU time: 229.19 s
- System CPU time: 187.70 s
- Peak memory: 632,820 KB

System calls on a 100,000-order sample:
- `openat`: 100,689
- `write`: 100,001
- `close`: 100,677

### After the fix
Dataset: 8,400,000 orders

- Elapsed time: 62.04 s
- User CPU time: 51.89 s
- System CPU time: 8.02 s
- Peak memory: 633,752 KB

System calls on a 100,000-order sample:
- `openat`: 689
- `write`: 17
- `close`: 677

### Diagnosis and fix
The original script opened and closed the output file for every order. The fix moved file opening outside the loop, allowing all records to be written through one file handle.

The fixed script successfully generated all 8,400,000 audit records.