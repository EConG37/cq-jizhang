# Repository guidance

This repository distributes the `cq-jizhang/` skill. To install or configure it, read `INSTALL.md`, then `cq-jizhang/SKILL.md`.

Install into the current user's global skill directory by default. Keep credentials, real ledger records, authentication receipts, and user setup state outside this repository and outside the installed skill folder.

For maintenance, run the existing offline tests and `scripts/audit_release.py`. Package only the explicit skill manifest using `scripts/package_release.py`; publish generated archives as Release assets rather than committing runtime files.
