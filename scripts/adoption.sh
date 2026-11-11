#!/usr/bin/env bash
# Public adoption numbers for pkv, with no interviews and no tracking of users (decision D-002).
# Plain words: ask PyPI and GitHub for their public counters and print one dated table row.
# Usage: scripts/adoption.sh            (paste the row into governance/ADOPTION.md)
# Needs: curl, python3, and gh signed in as the repository owner (for the traffic numbers).
set -euo pipefail
repo=broly18814/parinamakramam
action=broly18814/parinama-verify-action   # the Marketplace copy (D-047)
day="$(date -u +%Y-%m-%d)"
pypi="$(curl -s https://pypistats.org/api/packages/parinama-verify/recent \
  | python3 -c 'import json,sys
try: d=json.load(sys.stdin)["data"]; print("%s / %s / %s" % (d["last_day"], d["last_week"], d["last_month"]))
except Exception: print("not available yet")')"
stars="$(gh api "repos/$repo" -q '.stargazers_count')"
forks="$(gh api "repos/$repo" -q '.forks_count')"
views="$(gh api "repos/$repo/traffic/views" -q '"\(.count) (\(.uniques) unique)"' 2>/dev/null || echo "n/a")"
clones="$(gh api "repos/$repo/traffic/clones" -q '"\(.count) (\(.uniques) unique)"' 2>/dev/null || echo "n/a")"
assets="$(gh api "repos/$repo/releases" -q '[.[].assets[] | select(.name | endswith(".whl")) | .download_count] | add // 0')"
issues="$(gh api "repos/$repo" -q '.open_issues_count')"
action_stars="$(gh api "repos/$action" -q '.stargazers_count')"
action_views="$(gh api "repos/$action/traffic/views" -q '"\(.count) (\(.uniques) unique)"' 2>/dev/null || echo "n/a")"
echo "| $day | $pypi | $assets | $stars | $forks | $views | $clones | $issues | $action_stars, $action_views |"
