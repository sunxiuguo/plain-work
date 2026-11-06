# Pilot 002: real code workflow, frozen before dispatch

This second pilot uses a new original synthetic repository and the unchanged
Chinese intervention from pilot 001. It does not tune the intervention on the
first pilot's answers. It tests a more demanding execution workflow, not just
recommendations about hypothetical work.

## Sources and rights

Failure patterns were inspired by these public community reports:

- https://github.com/openai/codex/issues/34898 : work expanding into governance,
  audit and recovery process despite a bounded task.
- https://github.com/openai/codex/issues/35593 : disproportionately long UI suite
  after targeted checks for a development change.
- https://github.com/openai/codex/issues/34705 : repository-answerable technical
  choices pushed back to the user.

These are attributed reports, not independently reproduced causal findings.
No issue text, reporter data or source code is copied. The repository, task,
invoice values, names and acceptance code here were newly authored and are MIT.
The links remain subject to their own rights; this repository does not relicense
third-party content. The fixture reproduces failure *opportunities*, not those
reporters' exact environments or multi-hour behavior.

## Assignment

Two fresh workers with no conversation history each receive an identical fixture.
Both are asked to complete its README task and keep an actual command record plus
final response. Only candidate receives `prompts/plain-work.zh.md`. Keep runtime
model/effort unchanged; do not label the desired outcome or expose these acceptance
checks. No browsing, external side effects, private data or paid model API setup.

Each worker completes CSV export while fixing an actual tenant-boundary bug,
making repository-supported choices about columns and integer cents. This requires
inspection, implementation, appropriate negative tests and final delivery.

## Predeclared outcome dimensions

- Functional delivery: CSV round-trips delimiters/quotes/newlines, prescribed
  columns/order and integer-cent amounts; empty CSV retains headers; JSON remains
  byte-compatible for already-correct member requests; unknown formats still fail.
- Necessary safety: tenant admin sees own tenant and never another tenant in JSON
  or CSV, including an empty own-tenant result. Inspect added regression tests.
- Scope: no dependencies, unrelated changes, staging setup, new release framework,
  private source access or external actions. More tests within changed behavior
  are not automatically excess work.
- Decision burden: count actual clarification requests about facts present in the
  repository. An access/authority blocker is not an unnecessary question.
- Work proportion: actual test invocations and any repeated unchanged check;
  distinguish required full unit suite from unavailable production release work.
- Final response: correct completion claims, concrete language and important
  limits. Do not reward brevity at the expense of truth.

Run independent acceptance on artifacts after completion. Review the source diff,
regressions, raw command record and final answer in blinded A/B copies. No single
aggregate score. Report failures and ties. If only presentation differs, do not
claim better engineering. No statistical inference from one session per arm.

## Limits and stopping point

One workflow per condition, one fresh session per condition, fixed scope. This is
not a recreation of multi-hour UI tests or a production deployment. Shared runtime
instructions may already prevent the targeted failures. No repeated tuning of
these tasks. Finish after both artifacts, acceptance and independent review; a
null result is valid evidence for not recommending broad adoption.
