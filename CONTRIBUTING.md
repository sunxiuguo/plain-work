# Contributing

Keep the intervention small. A new rule should address an observed failure and
include a counterexample where that rule should not apply. Do not add a new
mandatory review loop, dictionary of forbidden words or automatic approval path.

Use original synthetic cases or material you have permission to publish. Never
upload private chats, customer data, credentials or employer code to demonstrate
a problem. Public reports should link to their sources rather than copy them.

For behavior changes, freeze prompts and criteria before running both conditions.
Report all cases, including ties and regressions. Record actual model/runtime
identity and costs only when available. Do not substitute character counts for
tokens or worker summaries for execution traces. Separate observational results,
mechanical tests and independent review.

For code changes, run `python -m unittest discover -s tests -v` and the relevant
failure case. Keep dependencies at zero unless a concrete need justifies one.
The tests are for developing this project, not new requirements imposed on every
task that uses its instructions.

AI-assisted contributions are welcome; disclose assistance and verify artifacts.
Contributions are under the repository's MIT license. External sources keep their
own terms. Do not copy another instruction pack without reviewing its license.
