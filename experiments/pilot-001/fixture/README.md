# Port parser

Python standard library only. `parse_port` accepts a decimal string for a port
in the inclusive range 1..65535. Whitespace is accepted. Invalid inputs raise
ValueError. Existing code has a report that a valid port at the upper bound
is rejected. Fix that reported behavior, keep the contract and add an
appropriate regression test. Do not add unrelated features.

Run project tests with `python -m unittest -v`. No other project checks are required.
