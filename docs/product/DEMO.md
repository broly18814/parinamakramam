# Demonstration: what pkv does, in two minutes

Run it yourself. It needs git, Python 3.10 or newer and pytest, and everything happens in a temporary folder that is deleted afterwards:

```bash
product/verify/demo/demo.sh
```

The script ([`product/verify/demo/demo.sh`](../../product/verify/demo/demo.sh)) builds a tiny shop with one function, `apply_discount`, and one test with two checks. Then it shows pkv's verdict on three changes an AI coding assistant might make.

## The output (pkv 0.2.1, run on 9 November 2026)

```
=== 1. An honest change ===
Adds a docstring and rounds to cents. Both checks still pass.

# ✅ VERIFIED

- all 1 test(s) affected by the change passed, on exactly this code
(exit code 0)

=== 2. A bug, hidden by deleting the check that caught it ===
Breaks the maths, then deletes the assert that failed. pytest alone would say 'passed'.

# ⚠️ SUSPICIOUS

- 1 sign(s) that the tests were weakened
- **suspicious:** the test test_discount in tests/test_pricing.py now checks less: 2 checks before, 1 now.
(exit code 4)

=== 3. The same bug, tests left alone ===
Breaks the maths and leaves the tests as they were.

# ❌ FAILED

- 1 test(s) failed
(exit code 1)
```

## Why scene 2 matters

The bug turns `price - price * percent / 100` into `price - percent`.
- By coincidence, that still gives the right answer for `apply_discount(100, 10)`, which is 90.
- It gives the wrong answer for `apply_discount(80, 25)`: 55 instead of 60.

The assistant deleted the second check, so **pytest reports "1 passed"**, and a busy reviewer sees green. pkv compares the test with its previous version, sees that it now checks less, and says SUSPICIOUS, with a different exit code (4), so an automatic check blocks the change.

What pkv can't do is tell whether the *remaining* check is correct. If the assistant had changed `== 90` to the wrong value, which still matches the bug, the test would look like an honest fix. That limitation is documented in the [guide](../../product/verify/README.md).
