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

## L1/L0 シナリオ分析の報告形式

採点で低評価になったシナリオを分析・報告するときは、以下の4項目を**実装詳細でなくユーザーが理解できる言葉**で書く。

| 項目 | 書き方 |
|------|--------|
| **質問** | ユーザーが nabledge に投げた質問（そのまま） |
| **事象** | AI が何を答えられなかったか / 採点が何点になったか |
| **直接原因** | AI のどのステップで何が起きたか（「〜を選ばなかった」「〜を誤判定した」など） |
| **根本原因** | なぜそのステップがそう動いたか（設計の問題 / データの問題 / バグ など） |

**書いてはいけないこと**:
- クラス名・メソッド名・変数名をそのまま原因として書く（例: `verify_kb_evidence.py が mismatch` → NG）
- ログの生データをそのまま貼る

**良い例**:
- 直接原因: 「採点 AI が KB にある文章を引用した際に、引用元のセクションを 1 つ間違えて指定した」
- 根本原因: 「採点ツールが引用文字列を照合する際に、文中の特殊文字をシェルコマンドとして解釈してしまう実装バグがある」

tasks.md の調査メモにも同じ形式で記録し、セッションをまたいでも方針が引き継がれるようにする。
