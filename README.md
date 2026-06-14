# Host Connectivity in a Data Farm by Frenki Selmani

This is the private repo for my assignment on Data Farm Connectivity.

## Files

- `main.py` - The Python implementation for this assignment.
- `sample_input.txt` - Sample input (no link budget).
- `budget_input.txt` - Sample input with budget = 2.
- `sample_output.txt` - Output for `sample_input.txt`.
- `budget_output.txt` - Output for `budget_input.txt`.
- `Data Farm Report by Frenki Selmani.docx` - Technical report for the assignment.



## Algorithm choice

- For cases in which `budget = -1`, the program uses Dijkstra's algorithm.
- For cases in which `budget >= 0`, the program uses a budget-limited dynamic programming (shortest path algorithm).

## Output

For every host, the program prints either:
- the minimum latency and the corresponding path, or
- `unreachable` if no valid transfer chain exists.
