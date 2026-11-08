# Publishing pkv to PyPI: the founder's runbook

**PyPI** (the Python Package Index, pypi.org) is the public store of Python packages. Once pkv is there, anyone can install it with one command:

```bash
python -m pip install parinama-verify
```

Everything on the repository's side is ready. The publishing workflow is [`.github/workflows/publish.yml`](../../.github/workflows/publish.yml), and the package is checked on every upload by the `package` job in CI. What's left needs **your own PyPI account**, which only you can create and sign in to.

## How it works, in plain words

We use **Trusted Publishing**. You tell PyPI, once, "trust the workflow `publish.yml` in `broly18814/parinamakramam` to publish `parinama-verify`". From then on, each time a `pkv-v…` release is published on GitHub, the workflow:
- builds the package from that exact tag;
- checks that the tag matches the package version;
- checks the files the way PyPI will;
- installs and runs the wheel in a clean environment;
- sends the files to PyPI;
- and attaches the very same files and their checksums to the GitHub release.

**No password or API token is stored anywhere.** GitHub proves the workflow's identity to PyPI on each run, and PyPI also records a signed statement of where the files came from (an "attestation").

## Your steps (about 10 minutes, one time only)

1. **Create a PyPI account** at https://pypi.org/account/register/ and verify your email.
2. **Turn on two-factor authentication**, which PyPI requires before publishing: Account settings → Two factor authentication. Save the recovery codes somewhere safe.
3. **Add a "pending trusted publisher"**: Your account → Publishing → *Add a new pending publisher* → GitHub. Enter exactly:

   | Field | Value |
   |---|---|
   | PyPI Project Name | `parinama-verify` |
   | Owner | `broly18814` |
   | Repository name | `parinamakramam` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` |

   A pending publisher does **not** reserve the name. The name becomes yours at the first successful upload.
4. **Done on 9 November 2026: your approval is required for each publish.** The GitHub environment `pypi` has `broly18814` as its required reviewer, and only tags matching `pkv-v*` may deploy to it. `testpypi` exists too, and only the `main` branch may deploy to it. Every PyPI upload waits for your click in GitHub's Actions tab (*Review deployments* → *Approve*).
5. **Optional rehearsal on TestPyPI**, PyPI's practice copy:
   - repeat steps 1–3 on https://test.pypi.org with Environment name `testpypi`;
   - then run the workflow by hand: Actions → publish → *Run workflow* → target `testpypi`.

Then tell Claude it's done. The last step is publishing the `pkv-v0.2.1` release on GitHub, which starts the upload. It's another publishing step, so it needs your go-ahead.

## Good to know

- **PyPI uploads are permanent.** A version number can never be uploaded twice, even if it's deleted. A mistake is fixed by releasing the next version (0.2.2), never by replacing a file.
- **The install name and the import name differ.** You install `parinama-verify`, and it provides the command `pkv` and the Python module `pkv`. An unrelated package called `pkv` already exists on PyPI and uses the same module name, so the two shouldn't be installed in the same environment (open problem OI-14).
