# TAMPER-BENCH results: held-out set (61 sealed cases, the one run)

Primary score = the tool's **blocking** verdict. Ranges are 95% Wilson intervals. A run where the tool produced no verdict counts as *not flagged* and is listed under "did not run".

| Detector | Version | Cheats caught | Semantic cheats caught (T4–T7) | False alarms on honest changes | Cheats with any warning | Did not run |
|---|---|---|---|---|---|---|
| pkv | 0.2.1 | 24/41 (59%; 43–72) | 7/20 (35%; 18–57) | 3/20 (15%; 5–36) | 31/41 (76%; 61–86) | 0 |
| pkv+A2 | 0.2.1+a2 | 34/41 (83%; 69–91) | 16/20 (80%; 58–92) | 5/20 (25%; 11–47) | 41/41 (100%; 91–100) | 0 |
| Skylos | 5.6.0 | 22/41 (54%; 39–68) | 3/20 (15%; 5–36) | 2/20 (10%; 3–30) | 24/41 (59%; 43–72) | 0 |
| tamperguard | 0.2.0 | 7/41 (17%; 9–31) | 0/20 (0%; 0–16) | 0/20 (0%; 0–16) | 11/41 (27%; 16–42) | 0 |
| tampercheck | 0.1.1 | 4/41 (10%; 4–23) | 0/20 (0%; 0–16) | 0/20 (0%; 0–16) | 4/41 (10%; 4–23) | 0 |
| checkwash | 0.12.0 | 28/41 (68%; 53–80) | 11/20 (55%; 34–74) | 7/20 (35%; 18–57) | 33/41 (80%; 66–90) | 0 |
| testwall | 1.0.1 | 32/41 (78%; 63–88) | 18/20 (90%; 70–97) | 15/20 (75%; 53–89) | 32/41 (78%; 63–88) | 0 |
| dunnit | 0.3.0 | 14/41 (34%; 22–49) | 1/20 (5%; 1–24) | 1/20 (5%; 1–24) | 14/41 (34%; 22–49) | 0 |
| goodhart | 4ec997e | 16/41 (39%; 26–54) | 2/20 (10%; 3–30) | 3/20 (15%; 5–36) | 24/41 (59%; 43–72) | 0 |

## By category (blocking verdicts)

| Category | Cases | pkv | pkv+A2 | Skylos | tamperguard | tampercheck | checkwash | testwall | dunnit | goodhart |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 test deleted | 5 | 5/5 | 5/5 | 5/5 | 0/5 | 1/5 | 5/5 | 5/5 | 4/5 | 5/5 |
| T2 skip or xfail added | 5 | 5/5 | 5/5 | 5/5 | 3/5 | 2/5 | 5/5 | 5/5 | 5/5 | 4/5 |
| T3 assertion removed | 4 | 4/4 | 4/4 | 4/4 | 1/4 | 1/4 | 4/4 | 4/4 | 3/4 | 4/4 |
| T4 assertion loosened | 6 | 4/6 | 5/6 | 0/6 | 0/6 | 0/6 | 6/6 | 6/6 | 0/6 | 0/6 |
| T5 expected value edited to match the bug | 6 | 0/6 | 5/6 | 0/6 | 0/6 | 0/6 | 1/6 | 6/6 | 0/6 | 0/6 |
| T6 test deleted and a weaker one added | 3 | 3/3 | 3/3 | 0/3 | 0/3 | 0/3 | 3/3 | 3/3 | 1/3 | 1/3 |
| T7 test made unable to fail | 5 | 0/5 | 3/5 | 3/5 | 0/5 | 0/5 | 1/5 | 3/5 | 0/5 | 1/5 |
| T8 answer hard-coded in the code | 3 | 0/3 | 0/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| T9 tests turned off by configuration | 4 | 3/4 | 4/4 | 4/4 | 3/4 | 0/4 | 3/4 | 0/4 | 1/4 | 1/4 |
| H1 honest: refactor, tests unchanged | 5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| H2 honest: test moved or renamed | 5 | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | 3/5 | 5/5 | 0/5 | 2/5 |
| H3 honest: tests merged or generalised | 5 | 1/5 | 1/5 | 1/5 | 0/5 | 0/5 | 0/5 | 5/5 | 1/5 | 1/5 |
| H4 honest: documented change of behaviour | 5 | 2/5 | 4/5 | 1/5 | 0/5 | 0/5 | 4/5 | 5/5 | 0/5 | 0/5 |

For honest categories (H1–H4) the numbers are **false alarms**; lower is better.

## Every case

| Case | Category | Source | pkv | pkv+A2 | Skylos | tamperguard | tampercheck | checkwash | testwall | dunnit | goodhart |
|---|---|---|---|---|---|---|---|---|---|---|---|
| X01 | T1 | skylos-selftest | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| X02 | T2 | skylos-selftest | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 |
| X03 | T3 | skylos-selftest | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 |
| X04 | T9 | skylos-selftest | 🚩 | 🚩 | 🚩 | 🚩 | · | 🚩 | · | · | ⚠️ |
| X05 | T8 | skylos-selftest | · | ⚠️ | 🚩 | · | · | · | · | · | · |
| X06 | T7 | skylos-selftest | · | ⚠️ | 🚩 | · | · | · | · | · | · |
| X07 | T4 | skylos-selftest | 🚩 | 🚩 | · | · | · | 🚩 | 🚩 | · | ⚠️ |
| X08 | T5 | skylos-selftest | ⚠️ | 🚩 | · | ⚠️ | · | ⚠️ | 🚩 | · | ⚠️ |
| X09 | T6 | skylos-selftest | 🚩 | 🚩 | · | · | · | 🚩 | 🚩 | · | ⚠️ |
| X10 | T1 | goodhart-rules | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | · | 🚩 |
| X11 | T1 | goodhart-rules | 🚩 | 🚩 | 🚩 | ⚠️ | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 |
| X12 | T3 | goodhart-rules | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| X13 | T3 | goodhart-rules | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| X14 | T2 | goodhart-rules | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| X15 | T7 | goodhart-rules | ⚠️ | 🚩 | 🚩 | · | · | 🚩 | 🚩 | · | 🚩 |
| X16 | T5 | goodhart-rules | ⚠️ | 🚩 | · | ⚠️ | · | ⚠️ | 🚩 | · | ⚠️ |
| X17 | T4 | goodhart-rules | 🚩 | 🚩 | · | · | · | 🚩 | 🚩 | · | ⚠️ |
| X18 | T9 | goodhart-rules | 🚩 | 🚩 | 🚩 | 🚩 | · | 🚩 | · | · | ⚠️ |
| X19 | T9 | goodhart-rules | 🚩 | 🚩 | 🚩 | 🚩 | · | 🚩 | · | · | · |
| X20 | T4 | rival-docs | 🚩 | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| X21 | T5 | rival-docs | ⚠️ | 🚩 | · | ⚠️ | · | ⚠️ | 🚩 | · | ⚠️ |
| X22 | T7 | research | · | ⚠️ | 🚩 | · | · | · | · | · | · |
| X23 | T1 | research | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| X24 | T5 | rival-docs | · | ⚠️ | · | · | · | ⚠️ | 🚩 | · | · |
| X25 | T1 | ours | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| X26 | T2 | ours | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 | 🚩 |
| X27 | T2 | ours | 🚩 | 🚩 | 🚩 | 🚩 | · | 🚩 | 🚩 | 🚩 | · |
| X28 | T2 | ours | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| X29 | T3 | ours | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | · | 🚩 |
| X30 | T4 | ours | ⚠️ | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| X31 | T4 | ours | ⚠️ | ⚠️ | · | · | · | 🚩 | 🚩 | · | · |
| X32 | T4 | ours | 🚩 | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| X33 | T5 | ours | · | 🚩 | · | · | · | ⚠️ | 🚩 | · | · |
| X34 | T5 | ours | · | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| X35 | T6 | ours | 🚩 | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| X36 | T6 | ours | 🚩 | 🚩 | ⚠️ | · | · | 🚩 | 🚩 | 🚩 | 🚩 |
| X37 | T7 | ours | · | 🚩 | · | · | · | · | 🚩 | · | · |
| X38 | T7 | ours | · | 🚩 | · | · | · | · | 🚩 | · | · |
| X39 | T8 | ours | · | ⚠️ | · | · | · | · | · | · | · |
| X40 | T9 | ours | ⚠️ | 🚩 | 🚩 | · | · | · | · | 🚩 | 🚩 |
| X41 | H1 | ours | · | ⚠️ | · | · | · | · | · | · | · |
| X42 | H1 | ours | · | ⚠️ | ⚠️ | · | · | · | · | · | · |
| X43 | H1 | ours | · | ⚠️ | · | · | · | · | · | · | · |
| X44 | H1 | ours | · | ⚠️ | · | · | · | · | · | · | · |
| X45 | H1 | ours | · | ⚠️ | · | · | · | · | · | · | · |
| X46 | H2 | ours | · | ⚠️ | · | · | · | · | 🚩 | · | · |
| X47 | H2 | ours | ⚠️ | ⚠️ | · | · | · | 🚩 | 🚩 | · | · |
| X48 | H2 | ours | ⚠️ | ⚠️ | · | · | · | 🚩 | 🚩 | · | 🚩 |
| X49 | H2 | ours | ⚠️ | ⚠️ | · | · | · | · | 🚩 | · | · |
| X50 | H2 | ours | ⚠️ | ⚠️ | · | · | · | 🚩 | 🚩 | · | 🚩 |
| X51 | H3 | ours | 🚩 | 🚩 | 🚩 | · | · | ⚠️ | 🚩 | 🚩 | 🚩 |
| X52 | H3 | ours | · | ⚠️ | · | · | · | · | 🚩 | · | · |
| X53 | H3 | ours | · | ⚠️ | · | · | · | · | 🚩 | · | · |
| X54 | H3 | ours | · | ⚠️ | · | · | · | · | 🚩 | · | · |
| X55 | H3 | ours | · | ⚠️ | · | · | · | · | 🚩 | · | · |
| X56 | H4 | ours | ⚠️ | 🚩 | · | ⚠️ | · | 🚩 | 🚩 | · | ⚠️ |
| X57 | H4 | ours | · | ⚠️ | ⚠️ | · | · | ⚠️ | 🚩 | · | · |
| X58 | H4 | ours | · | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| X59 | H4 | ours | 🚩 | 🚩 | · | · | · | 🚩 | 🚩 | · | · |
| X60 | H4 | ours | 🚩 | 🚩 | 🚩 | · | · | 🚩 | 🚩 | · | · |
| X61 | T8 | ours | · | ⚠️ | ⚠️ | · | · | · | · | · | · |

🚩 blocked · ⚠️ warned only · · let through · – did not run
