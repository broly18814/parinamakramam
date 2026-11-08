# Security policy

Parinama Verify (`pkv`) exists to make software *more* trustworthy, so a security problem in it is taken seriously.

## Reporting a problem

**Please don't open a public issue for a security problem.** Report it privately through GitHub's private vulnerability reporting: the repository's **Security** tab → **Report a vulnerability**.

Please include:
- what you found;
- how to reproduce it (the smallest example you can);
- what you think the impact is.

We aim to acknowledge reports within 7 days, and to say within 30 days what we'll do. This is a one-person project, so these are targets, not guarantees.

## What counts as a security problem in pkv

- A way to make pkv say **VERIFIED** when the affected tests did not really run and pass on exactly the code being checked. That includes stale fingerprints, unselected tests, and hidden test failures.
- A way for the code being checked to read secrets that pkv promises to hide (environment variables not passed with `--keep-env`).
- A way to make pkv execute anything other than the configured test command, or write outside the project folder and its `.pkv/` receipts folder.
- A crash that a crafted repository can trigger to stop a check from giving a verdict.

## Known limits (not vulnerabilities, documented on purpose)

- pkv runs the project's tests, and tests are code. pkv is **not a sandbox**: it doesn't cut off the network or limit file access for the tests themselves. Run untrusted code only in an isolated environment, such as a disposable CI runner.
- The cheating detector reports *signals*, not proof. Some cheats are known to be missed; see `product/verify/benchmark/results/` for the measured list.

## Supported versions

Only the latest version gets fixes until version 1.0.
