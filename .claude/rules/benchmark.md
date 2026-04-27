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

## Simulate before measuring

30件フル計測は $8 / 20分かかる。改善案を思いついたら即計測ではなく、まず
スクリプトで手元シミュレーションして手応えを確認してから本計測に進む。

**Why:** 改善案を試しては 20分待ち、結果を見て別案を試す、を繰り返すと時間もコストも
膨らむ。LLM を呼ばずに再現できる部分 (キーワード抽出、grep ヒット、index 変更後の
見え方、候補タイトルに対する人間判定) はローカルで先に確認できる。期待できる改善幅を
目視で掴めてから計測に進むと、1 回の計測で判断が付く。

**How to apply:**
- 改善案を出したら、まず LLM を呼ばない形で再現する小スクリプトを書く
- 数件〜30件に対してドライランし、想定どおり変化するかユーザーに見せる
- ユーザーと合意が取れてから `run.py` での本計測へ進む
- 計測した結果だけで判断せず、計測前のシミュレーション結果と照らし合わせる
