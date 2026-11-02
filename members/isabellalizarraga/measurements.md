
# My Measurements - Isabella

## Task 5: Worker Experiment

### Setup
- GitHub username: isabellalizarraga
- Available CPUs in Docker: 10
- Dataset: sales_2025.csv (8.4 million rows)
- Command: `bash tools/sweep.sh isabellalizarraga`

### Worker Experiment Results

I tested 1, 2, 4, 8, and 16 workers, running each configuration three times.

| Workers | Average elapsed time (s) |
|---------|--------------------------|
| 1       | 28.81                    |
| 2       | 14.89                    |
| 4       | 7.88                     |
| 8       | 5.83                     |
| 16      | 6.15                     |

### Observations

The execution time decreased as the number of workers increased from 1 to 8.

However, using 16 workers was slightly slower than using 8 workers.

### Conclusion

My Docker container has 10 CPUs available, but 8 workers gave the best performance.

Using more workers does not always make a program faster because workers compete for CPU resources and introduce additional overhead.

The results suggest that a sensible worker count should depend on the available CPUs and the actual performance measurements.
