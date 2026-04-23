# Benchmark Rules

Rules for running `tools/benchmark/` (search-flow accuracy benchmark).

## Do not run `run.py` invocations in parallel

Run benchmark commands sequentially. Never start a second `tools/benchmark/run.py`
invocation while another one is still running.

**Why:** each scenario spawns a `claude` CLI with `--max-turns 2` and a 240s
timeout. Running two `run.py` processes in parallel doubles the concurrent CLI
load, pushes API latency past 240s, and causes many scenarios to fail with
`subprocess.TimeoutExpired`. Observed 2026-04-23 — parallel judge-only runs of
the `ids` and `current` flows both crashed partway through while the same
commands had previously succeeded when run sequentially.

**How to apply:**
- Applies to all `run.py` modes: `--variant ids/current`, `--rejudge`.
- When re-scoring both `ids` and `current` flows, run one to completion, then
  run the other.
- If timeouts occur even in a single sequential run, investigate other
  Anthropic API consumers on the machine — do not just raise the timeout.

This does **not** generalize to all `claude -p` usage. Other tools that invoke
`claude -p` (e.g. `tools/knowledge-creator`, `nabledge-test`) are known to work
in parallel. The rule is specific to `tools/benchmark/run.py` because each
scenario is long (60-70s) and a single `run.py` already saturates one API slot.
