# Pilot 002 results

**No material delivery advantage observed.** Both conditions produced identical
implementation code, passed all fixed acceptance checks and retained necessary
tenant-isolation tests. The intervention did not demonstrate less scope drift:
neither condition drifted in this task.

Run date: 2026-11-06. The workflow is an original synthetic adaptation of the
public failure patterns attributed in `protocol.md`, not a recreation of those
reporters' environments.

## Frozen inputs

The same Chinese intervention from pilot 001 was used without revision.
The new task, protocol and acceptance script were fixed and their hashes recorded
before the two fresh workers were dispatched:

- Intervention: `3d235ee13c9a606bd5b2decef7ca9d8eb28213f9987fdc9b17b5fc764750842e`
- Protocol: `927c8bc418060632371f22fbb5f8521cf8660b5ba443ec55e577a28224323724`
- Acceptance: `c8ec215c0b3813f0c05f0245650224244d45dbb4806c84c8dc3fe37b43d27803`
- Fixture README: `3b0e549f5ba277ab42ef3ddb9cddca7e1e16f29595abfba72defa0ff9c84ea7b`

This was an internal prospective plan, not a public preregistration. Exact model
version, sampler settings, token usage, full runtime configuration and monetary
cost were not exposed in the collected artifacts. Both fresh workers used the
same parent runtime without a deliberate model override.

## Actual outcomes

| Dimension | Baseline | Candidate |
| --- | --- | --- |
| Fixed independent acceptance | 11/11 passed | 11/11 passed |
| Independent rerun of submitted unit suite | 12/12 passed | 12/12 passed |
| Implementation | Identical to candidate | Identical to baseline |
| New regression tests | 7 | 7 |
| Observed test invocations | 3 | 2 |
| Pre-fix failure demonstration | Recorded | Not recorded |
| Dependencies or unrelated implementation changes | None observed | None observed |
| Clarification in recorded artifacts | None observed | None observed |
| Final answer Unicode code points | 525 | 520 |

Both implementation files have SHA-256
`89912edcfd7a2fa00b269af16f8ff8936e8bdacbab38d0b257d7d991f37f0637`.

The actual file hash is also captured in the release manifest. Do not infer model
efficiency from the 3-versus-2 test count: the baseline's additional call
demonstrated expected failures before the fix. Both ran focused tests and the
README-required complete unit suite after implementation. There was only one test
file, so those two commands covered the same tests. That duplication came from
the task's own instructions and is not evidence of agent over-testing.

Both fixed tenant administrator isolation for JSON and CSV, retained own-tenant
access, escaped customer-name punctuation/newlines, preserved integer cents and
compatible member JSON output, emitted empty CSV headers and rejected unsupported
formats. No production release was attempted.

## Independent blinded review

After completion, the two result directories were randomly assigned A/B. The
reviewer saw task instructions, implementation, tests, commands/output and final
answers. Workspace paths were replaced and the intervention-loading step was
removed from the candidate's **review copy** to avoid revealing the condition.
The public condition-labeled logs retain that step with project/workspace paths
normalized; `log-source.json` records each original log hash and replacements.

The reviewer did not receive the condition key, first pilot's condition mapping,
desired result or independent acceptance outcomes. It found no material delivery
difference and no safety failure. It noted complementary test strengths: one
set explicitly covered both user roles across report paths, the other used fixed
independent expected column/JSON values. Both final explanations were clear.

`results/ratings.json` preserves the full review; `review-key.json` maps A/B to
conditions. `results/blind/` preserves the exact review copies and a preparation
record with log hashes. This was an assistant review, not a human/user preference study.
The recorded shell logs do not contain a complete conversation, so absence of a
clarification in those artifacts is not proof of zero requests throughout.

## Reproduce the artifact checks

From the repository root:

```sh
python experiments/pilot-002/acceptance.py experiments/pilot-002/results/baseline
python experiments/pilot-002/acceptance.py experiments/pilot-002/results/candidate
(cd experiments/pilot-002/results/baseline && python -m unittest discover -s tests -v)
(cd experiments/pilot-002/results/candidate && python -m unittest discover -s tests -v)
```

These rerun code checks, not model generation. Original outputs, final answers,
tests and normalized logs are retained. This project has no paid API runner and
does not scan private model sessions.

## Limits and decision

One workflow per condition, no repeated independent trials, no human blind panel,
and no long-running production task. The README supplied unusually clear scope,
completion conditions and money/authorization semantics. Shared runtime guidance
also already encouraged good behavior. We did not reproduce the community
failures, so this experiment cannot establish a remedy for them.

The correct next decision is **not to recommend broad installation based on these
results**. Keep the small reversible intervention as an experiment and publish
the null results. A future test should use independently selected, authorized,
sanitized real failure patterns and repeated fresh runs, rather than keep changing
this fixture or stacking rules until a favorable result appears.
