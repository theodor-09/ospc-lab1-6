
#!/bin/bash
set -euo pipefail

# Input dataset and output folder
DATA=${DATA:-$HOME/data/sales_2025.csv}
OUT=${OUT:-$HOME/data/out}

mkdir -p "$OUT/extracts"

# Create one CSV file for each region
for region in Iberia DACH France Italy Benelux Nordics; do
    grep ",$region," "$DATA" |
      cut -d, -f1,2,4,6,7 > "$OUT/extracts/$region.csv"
done

echo "extracts: done"

