#!/bin/bash
# Bootstrap 95% confidence intervals for the average order value of every
# region and month. The work is split among WORKERS processes that run at
# the same time: more workers, faster results.

CPUS=$(nproc)
WORKERS=${WORKERS:-$CPUS}
OUT=${OUT:-$HOME/data/out}

pids=()

cleanup() {
    trap - INT TERM
    if ((${#pids[@]} > 0)); then
        kill "${pids[@]}" 2>/dev/null
        wait "${pids[@]}" 2>/dev/null
    fi
    exit 130
}

trap cleanup INT TERM

python3 steps/stats_prepare.py
mkdir -p "$OUT/stats"
rm -f "$OUT"/stats/part_*.csv
for k in $(seq 0 $((WORKERS - 1))); do
    python3 steps/stats_worker.py "$k" "$WORKERS" &
    pids+=("$!")
done

wait
pids=()
cat "$OUT"/stats/part_*.csv | sort > "$OUT/stats.csv"
echo "stats: done with $WORKERS workers"
