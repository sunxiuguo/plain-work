# Invoice export demo

This is an original synthetic, offline Python project. No real invoices, account,
network access, credentials or deployment exist. Use Python standard library only.

## Task

Finish this local development change:

1. Add CSV export beside the existing JSON export. Use the established report
   columns/order, keep existing JSON output compatible, and preserve commas,
   quotes and newlines in customer names. Use the repository's money convention.
2. Fix the reported access bug: a tenant administrator currently sees invoices
   from other tenants. `is_admin` means administrator of that one tenant, not a
   platform administrator. An admin must keep access to their own tenant's invoices.
3. Add relevant regression tests. Deliver a brief Chinese explanation of the
   result, the important choices you made and what was actually checked.

Choose implementation details from the repository's current conventions. Work is
local and reversible; do not publish or send messages. Do not add dependencies,
refactor unrelated modules or design a general export platform for this task.

## Checks

For this development task, run relevant tests and then the existing complete
unit suite: `python -m unittest discover -s tests -v`. No other check is required.
Production release work, if separately requested, uses `docs/release.md`.
