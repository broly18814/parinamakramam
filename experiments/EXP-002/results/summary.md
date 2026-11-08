# EXP-001 summary

Generated 2026-11-08T20:31:37+0530 · budget 30000 values/round · rounds 5 · seeds 10-19

Metric: strict test solve rate (correct on 6 training inputs AND 4 held-out inputs), final round. CI = bootstrap over seeds.


## D-flat

| condition | test solve | 95% CI | Δ vs C0 [95% CI] (W/T/L) | Δ vs C1 [95% CI] | by level | compute (values) |
|---|---|---|---|---|---|---|
| C0_fixed | 67.3% | [63.3, 71.3] | — | — | L2:89%, L3:70%, L4:43% | 150000 |
| C3_evolve | 65.2% | [60.5, 70.0] | -2.2 pp [-3.7, -0.7] (0/5/5) | — | L2:88%, L3:66%, L4:42% | 150000 |
| C5_prospective | 65.3% | [60.2, 70.3] | -2.0 pp [-3.8, -0.3] (0/6/4) | — | L2:88%, L3:65%, L4:43% | 150000 |
| O_oracle | 62.3% | [58.5, 66.3] | -5.0 pp [-6.7, -3.3] (0/1/9) | — | L2:84%, L3:62%, L4:42% | 150000 |

## D-struct

| condition | test solve | 95% CI | Δ vs C0 [95% CI] (W/T/L) | Δ vs C1 [95% CI] | by level | compute (values) |
|---|---|---|---|---|---|---|
| C0_fixed | 55.3% | [52.0, 58.2] | — | — | L2:89%, L3:50%, L4:27% | 150000 |
| C3_evolve | 54.8% | [51.3, 57.8] | -0.5 pp [-3.7, +2.3] (4/3/3) | — | L2:88%, L3:50%, L4:27% | 150000 |
| C5_prospective | 52.5% | [49.0, 56.0] | -2.8 pp [-5.2, -0.3] (2/2/6) | — | L2:82%, L3:48%, L4:27% | 150000 |
| O_oracle | 71.3% | [66.5, 75.7] | +16.0 pp [+13.2, +18.7] (10/0/0) | — | L2:90%, L3:75%, L4:48% | 150000 |
