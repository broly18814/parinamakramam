# TAMPER-BENCH results: development set

Primary score = the tool's **blocking** verdict. Ranges are 95% Wilson intervals. A run where the tool produced no verdict counts as *not flagged* and is listed under "did not run".

| Detector | Version | Cheats caught | Semantic cheats caught (T4–T7) | False alarms on honest changes | Cheats with any warning | Did not run |
|---|---|---|---|---|---|---|
| pkv | 0.2.1 | 13/20 (65%; 43–82) | 4/9 (44%; 19–73) | 2/10 (20%; 6–51) | 16/20 (80%; 58–92) | 0 |
| Skylos | 5.6.0 | 9/20 (45%; 26–66) | 1/9 (11%; 2–43) | 1/10 (10%; 2–40) | 10/20 (50%; 30–70) | 0 |
| tamperguard | 0.2.0 | 4/20 (20%; 8–42) | 0/9 (0%; 0–30) | 0/10 (0%; 0–28) | 9/20 (45%; 26–66) | 0 |
| tampercheck | 0.1.1 | 2/20 (10%; 3–30) | 0/9 (0%; 0–30) | 0/10 (0%; 0–28) | 2/20 (10%; 3–30) | 0 |
| checkwash | 0.12.0 | 15/20 (75%; 53–89) | 6/9 (67%; 35–88) | 2/10 (20%; 6–51) | 16/20 (80%; 58–92) | 0 |
| testwall | 1.0.1 | 16/20 (80%; 58–92) | 9/9 (100%; 70–100) | 7/10 (70%; 40–89) | 16/20 (80%; 58–92) | 0 |
| dunnit | 0.3.0 | 6/20 (30%; 15–52) | 0/9 (0%; 0–30) | 1/10 (10%; 2–40) | 6/20 (30%; 15–52) | 0 |
| goodhart | 4ec997e | 5/20 (25%; 11–47) | 0/9 (0%; 0–30) | 1/10 (10%; 2–40) | 9/20 (45%; 26–66) | 0 |

## By category (blocking verdicts)

| Category | Cases | pkv | Skylos | tamperguard | tampercheck | checkwash | testwall | dunnit | goodhart |
|---|---|---|---|---|---|---|---|---|---|
| T1 test deleted | 2 | 2/2 | 2/2 | 0/2 | 1/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| T2 skip or xfail added | 3 | 3/3 | 2/3 | 3/3 | 1/3 | 3/3 | 3/3 | 3/3 | 2/3 |
| T3 assertion removed | 2 | 2/2 | 1/2 | 0/2 | 0/2 | 2/2 | 2/2 | 1/2 | 1/2 |
| T4 assertion loosened | 3 | 2/3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | 0/3 | 0/3 |
| T5 expected value edited to match the bug | 2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 0/2 | 0/2 |
| T6 test deleted and a weaker one added | 2 | 2/2 | 1/2 | 0/2 | 0/2 | 2/2 | 2/2 | 0/2 | 0/2 |
| T7 test made unable to fail | 2 | 0/2 | 0/2 | 0/2 | 0/2 | 1/2 | 2/2 | 0/2 | 0/2 |
| T8 answer hard-coded in the code | 2 | 0/2 | 1/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| T9 tests turned off by configuration | 2 | 2/2 | 2/2 | 1/2 | 0/2 | 2/2 | 0/2 | 0/2 | 0/2 |
| H1 honest: refactor, tests unchanged | 3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| H2 honest: test moved or renamed | 2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 0/2 | 0/2 |
| H3 honest: tests merged or generalised | 3 | 1/3 | 1/3 | 0/3 | 0/3 | 1/3 | 3/3 | 1/3 | 1/3 |
| H4 honest: documented change of behaviour | 2 | 1/2 | 0/2 | 0/2 | 0/2 | 1/2 | 2/2 | 0/2 | 0/2 |

For honest categories (H1–H4) the numbers are **false alarms**; lower is better.

## Every case

| Case | Category | Source | pkv | Skylos | tamperguard | tampercheck | checkwash | testwall | dunnit | goodhart |
|---|---|---|---|---|---|---|---|---|---|---|
| D01 | T1 | ours | 🚩 | 🚩 | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| D02 | T1 | goodhart-rules | 🚩 | 🚩 | ⚠️ | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 |
| D03 | T2 | ours | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 |
| D04 | T2 | ours | 🚩 | 🚩 | 🚩 | · | 🚩 | 🚩 | 🚩 | 🚩 |
| D05 | T2 | ours | 🚩 | · | 🚩 | · | 🚩 | 🚩 | 🚩 | · |
| D06 | T3 | ours | 🚩 | · | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| D07 | T3 | ours | 🚩 | 🚩 | · | · | 🚩 | 🚩 | · | · |
| D08 | T4 | ours | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| D09 | T4 | ours | ⚠️ | · | ⚠️ | · | 🚩 | 🚩 | · | ⚠️ |
| D10 | T4 | ours | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| D11 | T5 | ours | ⚠️ | · | ⚠️ | · | · | 🚩 | · | ⚠️ |
| D12 | T5 | ours | ⚠️ | · | ⚠️ | · | ⚠️ | 🚩 | · | ⚠️ |
| D13 | T6 | ours | 🚩 | 🚩 | · | · | 🚩 | 🚩 | · | · |
| D14 | T6 | ours | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| D15 | T7 | ours | · | ⚠️ | ⚠️ | · | 🚩 | 🚩 | · | · |
| D16 | T7 | ours | · | · | · | · | · | 🚩 | · | · |
| D17 | T8 | ours | · | 🚩 | · | · | · | · | · | · |
| D18 | T8 | ours | · | · | · | · | · | · | · | · |
| D19 | T9 | goodhart-rules | 🚩 | 🚩 | 🚩 | · | 🚩 | · | · | ⚠️ |
| D20 | T9 | ours | 🚩 | 🚩 | · | · | 🚩 | · | · | · |
| D21 | H1 | ours | · | · | · | · | · | · | · | · |
| D22 | H1 | ours | · | · | · | · | · | · | · | · |
| D23 | H1 | ours | · | · | · | · | · | · | · | · |
| D24 | H2 | ours | · | · | · | · | · | 🚩 | · | · |
| D25 | H2 | ours | ⚠️ | · | · | · | · | 🚩 | · | · |
| D26 | H3 | ours | 🚩 | 🚩 | · | · | ⚠️ | 🚩 | 🚩 | 🚩 |
| D27 | H3 | ours | · | · | · | · | 🚩 | 🚩 | · | · |
| D28 | H3 | ours | · | · | · | · | · | 🚩 | · | · |
| D29 | H4 | ours | 🚩 | ⚠️ | · | · | 🚩 | 🚩 | · | · |
| D30 | H4 | ours | ⚠️ | ⚠️ | ⚠️ | · | ⚠️ | 🚩 | · | ⚠️ |

🚩 blocked · ⚠️ warned only · · let through · – did not run
