# EXP-001 summary

Generated 2026-11-08T20:30:25+0530 · budget 30000 values/round · rounds 5 · seeds 100

Metric: strict test solve rate (correct on 6 training inputs AND 4 held-out inputs), final round. CI = bootstrap over seeds.


## D-flat

| condition | test solve | 95% CI | Δ vs C0 [95% CI] (W/T/L) | Δ vs C1 [95% CI] | by level | compute (values) |
|---|---|---|---|---|---|---|
| C0_fixed | 76.7% | [76.7, 76.7] | — | — | L2:90%, L3:80%, L4:60% | 150000 |
| C3_evolve | 65.0% | [65.0, 65.0] | -11.7 pp [-11.7, -11.7] (0/0/1) | — | L2:80%, L3:75%, L4:40% | 150000 |
| C5_prospective | 76.7% | [76.7, 76.7] | +0.0 pp [+0.0, +0.0] (0/1/0) | — | L2:90%, L3:80%, L4:60% | 150000 |
| O_oracle | 70.0% | [70.0, 70.0] | -6.7 pp [-6.7, -6.7] (0/0/1) | — | L2:85%, L3:80%, L4:45% | 150000 |

## D-struct

| condition | test solve | 95% CI | Δ vs C0 [95% CI] (W/T/L) | Δ vs C1 [95% CI] | by level | compute (values) |
|---|---|---|---|---|---|---|
| C0_fixed | 55.0% | [55.0, 55.0] | — | — | L2:85%, L3:40%, L4:40% | 150000 |
| C3_evolve | 56.7% | [56.7, 56.7] | +1.7 pp [+1.7, +1.7] (1/0/0) | — | L2:90%, L3:40%, L4:40% | 150000 |
| C5_prospective | 53.3% | [53.3, 53.3] | -1.7 pp [-1.7, -1.7] (0/0/1) | — | L2:80%, L3:45%, L4:35% | 150000 |
| O_oracle | 73.3% | [73.3, 73.3] | +18.3 pp [+18.3, +18.3] (1/0/0) | — | L2:95%, L3:60%, L4:65% | 150000 |
