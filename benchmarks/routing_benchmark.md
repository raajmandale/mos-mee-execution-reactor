# Routing Reuse Benchmark (PRC-2)

## Objective
Measure whether pattern reuse improves execution behavior.

---

## Test Cases

| Workload | Baseline (ms) | Reuse (ms) | Improvement |
|---------|----------------|-----------|-------------|
| Image Flow | 220 | 130 | 40.9% |
| Bundle Workload | 310 | 190 | 38.7% |
| Similar Match | 180 | 95 | 47.2% |

---

## Observations

- Reuse reduced routing latency across all tested workloads.
- Similar structures produced strongest gains.
- Bundle workloads showed stable improvement.

---

## Conclusion

Pattern reuse appears to improve execution efficiency under structured workloads.