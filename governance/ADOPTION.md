# Adoption: public numbers only

Rule D-002: no interviews, ever. We judge demand only from what people do on their own, using public counters. pkv itself sends nothing anywhere.

Take a reading with `scripts/adoption.sh` (dates are UTC) and add the row below. One reading a week is enough.

| Date (UTC) | PyPI downloads (day / week / month) | Wheel downloads from GitHub releases | Stars | Forks | Repository views, 14 days | Clones, 14 days | Open issues | Action repository (Marketplace): stars, views 14 days |
|---|---|---|---|---|---|---|---|---|
| 2026-11-08 | not available yet (pypistats updates daily) | 2, both our own release checks | 0 | 0 | 0 (0 unique) | 0 (0 unique) | 0 | — (not yet created) |
| 2026-11-10 | 12 / 99 / 0 (the month counter hasn't caught up yet) | 3 | 0 | 0 | 29 (20 unique) | 472 (67 unique) | 0 | — (not yet created) |
| 2026-11-13 | 2 / 111 / 111 | 4 | 0 | 0 | 47 (21 unique) | 1135 (186 unique) | 0 | 0, 11 (3 unique) |

## Notes on each reading

- **2026-11-13: the baseline before the launch** (pkv 0.3.0 released today).
  - **Downloads:** many of the 111 this week are robots, plus our own release and install checks.
  - **Clones:** the 1,135 follow from about 80 uploads, each running several CI jobs.
  - **Users:** a public code search for workflows using `broly18814/parinama-verify-action` or `broly18814/parinamakramam/product/verify` found **0** repositories other than ours.
  - **What it's for:** the launch (A6) is judged against this row.

- **2026-11-10 (day 3).** No sign of real use yet, as expected two days after publishing.
  - PyPI, not counting mirrors: 87 downloads on 8 November and 12 on 9 November. The first-day spike followed by a sharp drop is the usual pattern of scanners and mirrors picking up a new package, plus our own install checks (D-032).
  - The 472 clones are consistent with GitHub's robot fetching the code for our own checks on every upload (about 40 uploads, several jobs each). We can't tell from the counter how many, if any, were people.
  - 20 unique visitors viewed the repository page. Nobody starred it, forked it or opened an issue.
  - A public code search for workflows that use the Action (`broly18814/parinamakramam/product/verify`) found **0** repositories other than ours.

## How to read these numbers honestly

- **PyPI downloads include robots.** Mirrors and security scanners download every new package. Expect dozens of "downloads" in the first days that aren't people. A real signal is a *steady weekly* number that keeps growing.
- **Our own downloads count too.** Release checks, CI installs from PyPI and demos all add to the counts. Note them in the row when we know.
- **Stars and forks are cheap. Use is not.** The strongest signals are:
  - a public repository using `broly18814/parinama-verify-action` (listed on GitHub's Marketplace since 11 November 2026, D-047) or `broly18814/parinamakramam/product/verify` in its workflow. Search GitHub code for both strings, and don't count this repository: its own robot uses both;
  - an issue filed from a real project, using the templates in `.github/ISSUE_TEMPLATE/`.
- **Activation and retention** (the day 71–90 goals): a project that adds the Action and *keeps* it for 30 days counts as retained. These are counted by hand from public repositories only.
