# Adoption: public numbers only

Rule D-002: no interviews, ever. We judge demand only from what people do on their own, using public counters. pkv itself sends nothing anywhere.

Take a reading with `scripts/adoption.sh` (dates are UTC) and add the row below. One reading a week is enough.

| Date (UTC) | PyPI downloads (day / week / month) | Wheel downloads from GitHub releases | Stars | Forks | Repository views, 14 days | Clones, 14 days | Open issues |
|---|---|---|---|---|---|---|---|
| 2026-11-08 | not available yet (pypistats updates daily) | 2, both our own release checks | 0 | 0 | 0 (0 unique) | 0 (0 unique) | 0 |

## How to read these numbers honestly

- **PyPI downloads include robots.** Mirrors and security scanners download every new package. Expect dozens of "downloads" in the first days that aren't people. A real signal is a *steady weekly* number that keeps growing.
- **Our own downloads count too.** Release checks, CI installs from PyPI and demos all add to the counts. Note them in the row when we know.
- **Stars and forks are cheap. Use is not.** The strongest signals are:
  - a public repository using `broly18814/parinamakramam/product/verify` in its workflow (search GitHub code for that string);
  - an issue filed from a real project, using the templates in `.github/ISSUE_TEMPLATE/`.
- **Activation and retention** (the day 71–90 goals): a project that adds the Action and *keeps* it for 30 days counts as retained. These are counted by hand from public repositories only.
