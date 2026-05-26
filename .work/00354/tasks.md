# Tasks: test-setup.sh — branch selection, metrics collection, and persistent report files

**PR**: #355
**Issue**: #354
**Updated**: 2026-05-26

## Fact-Based Work Rule

すべての調査・実装・判断は事実ベースで行う。推測・仮定で進めない。
- 実装前に対象ファイルを実際に読んで構造を確認する
- stream-json の出力フィールドは実機確認済み（`type:result` 行に `total_cost_usd` / `usage.input_tokens` / `usage.output_tokens` / `duration_ms` が含まれる）
- jq 利用可能確認済み（/usr/bin/jq 1.7）
- `tools/tests/reports/` は `.gitignore` に記載なし → git-tracked になる

## In Progress

（なし）

## Not Started

### Task 1: Create `tools/tests/reports/` directory with `.gitkeep`
**SC対応**: "Reports are written to `tools/tests/reports/` which is git-tracked"  
**Steps:**
- [ ] `tools/tests/reports/.gitkeep` を作成
- [ ] git add & commit: `chore: add tools/tests/reports/ directory for persistent test reports`

---

### Task 2: Add metrics collection to `verify_dynamic` in `test-setup.sh`
**SC対応**: "execution time (seconds)" / "token count (input + output, from stream-json for CC; N/A for GHC)" / "cost estimate in USD"  
**実装方針（実機確認済み）**:
- CC: `cc_log_file` の `{"type":"result"}` 行を jq でパース → `duration_ms` / `usage.input_tokens` / `usage.output_tokens` / `total_cost_usd` を抽出
  （確認日: 2026-05-26、コマンド: `claude -p --output-format stream-json --verbose --model haiku`）
- GHC: `--output-format json` の `{"type":"result"}` 行から `usage.totalApiDurationMs` で実行時間を取得可能。トークン数・コストは GHC 出力に含まれないため N/A
  （確認日: 2026-05-26、コマンド: `copilot -p --output-format json --allow-all-tools`）
- 抽出結果はグローバル変数配列（bash associative array）に蓄積し、後段のレポート生成で使用
**Steps:**
- [ ] `verify_dynamic` 内の CC パスに実行時間計測（`SECONDS` 変数またはbash `$SECONDS` 利用）を追加
- [ ] CC: `cc_log_file` から jq で `input_tokens`, `output_tokens`, `total_cost_usd`, `duration_ms` を抽出してグローバル変数に格納
- [ ] GHC: `--output-format json` の `{"type":"result"}` 行から `usage.totalApiDurationMs` を抽出してグローバル変数に格納（tokens/cost は N/A）
- [ ] git add & commit: `feat: collect execution time and token metrics in verify_dynamic`

---

### Task 3: Add static check results collection to `verify_env` in `test-setup.sh`
**SC対応**: "per-environment pass/fail (static + dynamic checks)"  
**実装方針**: `verify_env` の pass/fail 結果をグローバル変数配列に蓄積
**Steps:**
- [ ] `verify_env` の合否をグローバル変数配列に格納（ラベルと PASS/FAIL）
- [ ] git add & commit: `feat: collect static check results per environment in verify_env`

---

### Task 4: Add report generation function and write report file
**SC対応**: "one Markdown report file per run" / "filename encodes branch name and datetime" / "run-level totals"  
**実装方針**:
- ファイル名: `${NABLEDGE_BRANCH//\//-}-$(date +%Y%m%d-%H%M%S).md`（ブランチ名のスラッシュはハイフンに変換）
- 出力先: `${NABLEDGE_DEV_ROOT}/tools/tests/reports/`
- レポート構造: ヘッダー（ブランチ・実行日時・バージョンフィルター）/ 静的チェック表 / 動的チェック表（環境・Pass/Fail・時間・tokens in/out・cost）/ 実行合計行
- レポートはスクリプト末尾（summary の後）で生成
**Steps:**
- [ ] `generate_report` 関数を実装（Markdown テーブル形式で静的・動的チェック結果と合計を出力）
- [ ] スクリプト末尾から `generate_report` を呼び出してファイルに書き出す
- [ ] レポートファイルパスを標準出力に表示する
- [ ] git add & commit: `feat: generate Markdown report file with metrics per run`

---

### Task 5: Preview report Markdown rendering
**SCに対応した見栄え確認**: レポートの実際のレンダリングを確認してユーザーに提示  
**実装方針**: Task 4 完了後、サンプルレポートファイルをダミーデータで生成して `.work/00354/` にコミット、PRでユーザーに確認
**Steps:**
- [ ] サンプルレポート（ダミーデータ入り）を `.work/00354/sample-report.md` として生成
- [ ] git add & commit: `docs: add sample report preview for user review`
- [ ] PR コメントでユーザーにレンダリング確認依頼

---

### Task 6: Update README to document `main` branch testing and before/after comparison
**SC対応**: "README documents how to run against `main` branch for before/after comparison"  
**Steps:**
- [ ] `README.md` の「開発バージョンのテスト」セクションに `NABLEDGE_BRANCH=main` の使い方と前後比較手順を追記
- [ ] git add & commit: `docs: document main branch testing and before/after comparison in README`

---

### Task 7: Diff check — verify changes match expectation
**全タスク対象**: 実装完了後、変更差分が想定した変更のみかを確認
**Steps:**
- [ ] `git diff main...HEAD -- tools/tests/test-setup.sh README.md tools/tests/reports/` で差分を確認
- [ ] 想定外の変更（空行・コメント変更など含む）がないか確認
- [ ] 差分チェック結果を `.work/00354/diff-check.md` に出力
- [ ] git add & commit: `docs: add diff check result`
- [ ] PRでユーザーに差分チェック結果を確認依頼

---

### Task 8: Expert review (Software Engineer + QA Engineer)
**Steps:**
- [ ] Software Engineer レビュー実施（シェルスクリプトのアーキテクチャ・コード品質）
- [ ] QA Engineer レビュー実施（エッジケース・エラー処理）
- [ ] Finding があれば修正
- [ ] レビュー結果を `.work/00354/review-by-software-engineer.md` / `review-by-qa-engineer.md` に保存
- [ ] git add & commit: `docs: add expert review results`

---

### Task 9: Request user PR review
**Steps:**
- [ ] PR #355 のレビューをユーザーに依頼（PR コメントで通知）

---

## Done

（なし）
