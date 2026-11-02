# Lab 1: The Nightly Report

Write your answers in this file. Keep them short: a few sentences, the commands
you used, and the numbers you measured. Copy the lines of output that matter,
not whole screens.

## Warm-up: Generating the report

- What happened, and why: The script did not have permission to run directly. However, using bash run_report.sh worked because Bash can read the file without that permission.
- Your fix, and how it reached your teammates: I used chmod +x run_report.sh to make the script executable. Then I committed the change and pushed it to GitHub so my teammates could get it using git pull.

## Task 1: Generating the report… again

- **Symptom:** The original `steps/report.py` exceeded the 2 GiB Docker memory limit and was killed (OOM, exit status 137).

- **Commands and recordings:** We tested the original script on 1, 2 and 4 million orders to investigate memory growth. We measured the optimized script using `/usr/bin/time -v python3 steps/report.py` and validated its output with `python3 tools/check.py`.

- **Cause:** The script loaded all 8.4 million orders into memory and created 12 monthly DataFrames followed by `pd.concat()`, causing excessive memory consumption.

- **Fix:** Replaced full-file loading with `pd.read_csv(DATA, chunksize=100_000)`. Each chunk is grouped by region and month, keeping only accumulated revenue totals.

- **Before and after (measurements):**
  - Before: OOM kill under the 2 GiB limit (exit status 137).
  - After: 8,400,000 orders processed successfully.
  - Elapsed time: 9.14 s.
  - User CPU time: 9.39 s.
  - System CPU time: 0.53 s.
  - Peak RSS: 207,600 KB (approximately 202.7 MiB).
  - Exit status: 0.
  - Validation: `PASS revenue_by_region_month.csv`.

**Conclusion:** Chunking reduced peak memory while preserving the expected output.

## Task 2: Extracting data

- **Symptom:**

The extraction script printed `extracts: done`, but all six regional CSV files were empty (0 rows). The script appeared to work even though no data was extracted.

- **Commands and recordings:**

1. `bash steps/extracts.sh` — We first ran the script to see whether it worked. It printed `extracts: done`, which suggested that the extraction had finished successfully.

2. `echo $?` — We checked the exit code of the script. It returned `0`, meaning the system reported no error. However, this did not prove that the output was correct, so we checked the files next.

3. `ls -l ~/data/out/extracts` — We inspected the files created by the script. All six regional CSV files had a size of 0 bytes. This showed that the script was creating files but not extracting any data.

4. `less steps/extracts.sh` — We read the original script to understand its commands. We noticed that it changed the working directory and used a relative path to find the dataset. We also saw that `2>/dev/null` was hiding error messages.

5. `grep ",Iberia," ../data/sales_2025.csv | cut -d, -f1,2,4,6,7 | wc -l` — We tested the extraction pipeline manually using Iberia as an example. `grep` searches for Iberia orders. Instead of finding records, we received `No such file or directory` and a count of 0. This suggested that the input path was incorrect.

6. `echo ${PIPESTATUS[@]}` — We checked the exit code of each command in the pipeline. The result was `2 0 0`, meaning `grep` failed, but `cut` and `wc` succeeded. This explained why the script could appear successful even when the extraction failed.

7. `pwd` — We checked our current working directory. It was `/home/analyst/data/out/extracts`, confirming that the relative path was being interpreted from the extraction folder rather than from the repository.

8. `grep -c ',Iberia,' ~/data/sales_2025_sample.csv` — We checked whether the dataset actually contained Iberia orders. It returned 25,928 records, confirming that the data existed and the problem was the incorrect file path.

- **Cause:**

The script used `cd "$OUT/extracts"` and then tried to read `../data/sales_2025.csv`. This relative path did not point to the dataset. Additionally, `2>/dev/null` hid the error messages, and the script did not detect failures in the pipeline.

- **Fix:**

We removed the unnecessary `cd` command and replaced the relative input path with the `DATA` environment variable, defaulting to `$HOME/data/sales_2025.csv`. We also removed `2>/dev/null` and added `set -euo pipefail` so that errors are visible and the script stops if a command fails.

- **Before and after (your measurements):**

| Measurement       | Before           | After                                   |
| ----------------- | ---------------- | --------------------------------------- |
| Sample dataset    | 0 rows extracted | 100,000 rows extracted                  |
| Full dataset      | 0 rows extracted | 8,400,000 rows extracted                |
| Iberia sample     | 0 rows           | 25,928 rows                             |
| Error detection   | Errors hidden    | Errors visible; script stops on failure |
| Output validation | Incorrect        | All six regional checks passed          |

After the fix, the script generated all six regional CSV files correctly. We verified the results using `wc -l` and `python3 tools/check.py`.


## Task 3: Auditing

- **Symptom:** `audit.py` was very slow because it opened and closed the output file for every order.
- **Commands:** Used `/usr/bin/time` to measure performance, `strace -c` to count system calls, and `wc -l` to verify the output.
- **Cause:** Opening, writing and closing the file inside the loop caused excessive file-system operations.
- **Fix:** Moved the file opening outside the loop so all orders are written using one open file handle.
- **Before and after (8.4 million orders):**
  - Before: 422.68 s elapsed, 229.19 s user, 187.70 s system, 632,820 KB memory.
  - After: 62.04 s elapsed, 51.89 s user, 8.02 s system, 633,752 KB memory.
- **System calls (100,000-order sample):** `openat` decreased from 100,689 to 689; `write` from 100,001 to 17; `close` from 100,677 to 677.
- **Result:** The fixed script successfully generated all 8,400,000 audit records.

## Task 4: Segmenting the orders

- Symptom: The segments step was taking much longer than reading the CSV.
- Commands and recordings you used, why you chose them, and what they showed: I used /usr/bin/time to measure execution time and CPU usage, and cProfile to find the slow functions. The profiler showed 100,000 calls to strptime() on the sample.
- Cause: The script was converting dates one by one inside a loop, which wasted CPU time.
- Fix: I used pandas to calculate the quarters before the loop, instead of converting each date separately.
- Before and after (your measurements): On 100,000 rows, execution time dropped from 1.01 s to 0.29 s (about 71% less time). cProfile time dropped from 0.890 s to 0.402 s. The output was identical. The full dataset ran in 10.43 s with 1,265,744 KB peak memory.

## Task 5: Computing the statistics

- Symptom: stats.sh hardcodes 16 workers. With nproc=4, 16 workers gives ~32s elapsed but ~90s user and ~38s system time. Ctrl-C leaves orphan workers running.
- Commands: `nproc` (returned 4), `bash tools/sweep.sh theodor-09`, `ps -ef` after `kill %1`.
- Cause: 16 workers on 4 CPUs means time-sharing overhead (Lecture 12). Background children (`&`) not killed when parent exits (Lecture 4).
- Fix: Changed `WORKERS=${WORKERS:-16}` to `WORKERS=${WORKERS:-$(nproc)}`. Added `trap 'kill $(jobs -p) 2>/dev/null; wait' EXIT INT TERM`.
- Before: 1 worker ~41s, 16 workers ~32s but 90s user + 38s system.
- After: 4 workers ~25s (best), 70s user + 25s system. No orphans after kill.

Sweep results (theodor-09, nproc=4, clean environment):
| Workers | Avg elapsed | Avg user | Avg system |
|---------|------------|----------|------------|
| 1       | 41.0s      | 34.5s    | 6.9s       |
| 2       | 27.5s      | 39.9s    | 12.6s      |
| 4       | 25.3s      | 70.3s    | 25.5s      |
| 8       | 30.2s      | 83.8s    | 33.9s      |
| 16      | 32.5s      | 89.1s    | 38.5s      |

Elapsed drops from 41s (1 worker) to 25s (4 workers) then rises. User and system time grow with workers due to context switching and OS overhead. 4 workers matches nproc and gives the best tradeoff.

We chose `$(nproc)` as the default because it matches available CPUs on any machine automatically.

## The worker experiment

Every member runs `tools/sweep.sh` on their own laptop. Then run
`python3 tools/plot_sweep.py` and commit `results/sweep.png`.

![Elapsed time against the number of workers](results/sweep.png)

- How does the elapsed time change with the number of workers on each laptop?
- Why do the curves of your laptops differ? Use the cores and threads of each
  laptop, listed in `TEAM.md`.
- Which default number of workers did you choose for `stats.sh`, and why?

### Worker experiment answers

**1. How does elapsed time change with the number of workers?**

> The graph shows that increasing the number of workers generally makes the program faster at first. However, after a certain point, the improvements become smaller or execution time increases again. For example, my laptop performed best with 8 workers, while Theo's performed best with 4. David's laptop became significantly slower with 16 workers. Therefore, adding more workers does not always improve performance.

**2. Why do the curves differ between laptops?**

> The laptops have different processors, CPU cores, threads, and Docker configurations. These differences affect how efficiently they can execute multiple processes at the same time. When too many workers compete for resources, context switching and other overhead can reduce performance. This explains why some laptops benefit from more workers while others slow down.

**3. Which default number of workers did you choose for stats.sh, and why?**

> We chose `$(nproc)` as the default number of workers because it automatically detects the CPUs available in each container. Instead of always using 16 workers, the script adapts to each computer. Our results show that the optimal worker count varies between laptops, so this is a reasonable and flexible default.

## Use of generative AI

Follow the format in the syllabus: quote any generated text and name the tool
and the prompts; add the same note as a comment before any generated code. If
you did not use GenAI, write: "No content generated by AI technologies has been
used in this assignment."

### AI use for the worker experiment - Isabella

Tool: ChatGPT (OpenAI).

Prompts: I asked ChatGPT for step-by-step guidance using Docker, running the worker experiment, generating results/sweep.png, and uploading my work to GitHub. I also asked for help interpreting the graph and drafting the three worker experiment answers.

AI-generated text: The three worker experiment answers above were drafted with ChatGPT assistance and marked as blockquotes. I executed the commands myself and reviewed the results against the graph.

### AI use for Task 4

Tool: ChatGPT (OpenAI).

Prompts: I asked ChatGPT to guide me step by step through Task 4, help identify the slow part of segments.py using cProfile, suggest a simpler way to calculate quarters, compare execution times, and help write my findings.

Generated code:
`orders["quarter"] = pd.to_datetime(orders["order_date"]).dt.quarter`
`quarter = order.quarter`

Generated report text: The five bullet points under "Task 4: Segmenting the orders" were drafted with ChatGPT's assistance.

I ran the commands myself, checked the profiler results, and verified that the optimized output matched the original.

### AI use for Task 2
Tool: ChatGPT (OpenAI).
We used ChatGPT to help us understand and debug the problems in extracts.sh. It helped as a guide trough terminal commands and understanding new outputs. We also used it to review our solution and organize the explanation in the report. All commands were executed by us, and we checked the results using the sample and full datasets.

### AI Use — Task 1 

Tool: ChatGPT. Used it as a learning tool and for support. I asked for step by step guidance in the use of GitHub as I had limited experience with this tool, understanding the issues, guide through commands, drafting and testing. 

### AI use for Task 5
Tool: Claude (Anthropic)
Prompts: I asked to highlight the bugs in stats.sh and the necessary edits to remove the fix number of workers and deal with orphan processes. I also asked for help formatting this report section based on my answers and measurements and to correct my work / interpretation if necessary.

### AI use for Task 3
Used ChatGPT to help understand the audit problem, interpret timing and system-call results, and prepare the report. I ran the commands, implemented the fix and verified the output myself.
