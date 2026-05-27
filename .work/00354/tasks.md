# Tasks: test-setup.sh — branch selection, metrics collection, and persistent report files

**PR**: #355
**Issue**: #354
**Updated**: 2026-05-27

## Fact-Based Work Rule

すべての調査・実装・判断は事実ベースで行う。推測・仮定で進めない。
- 実装前に対象ファイルを実際に読んで構造を確認する
- stream-json の出力フィールドは実機確認済み（`type:result` 行に `total_cost_usd` / `usage.input_tokens` / `usage.output_tokens` / `duration_ms` が含まれる）
- jq 利用可能確認済み（/usr/bin/jq 1.7）
- `tools/tests/reports/` は `.gitignore` に記載なし → git-tracked になる

## In Progress

### Task 12: Static Checks 改善 → 全バージョン実行 → レポート出力・比較

**背景:**
- Static Checks は知識ファイルのセットアップ確認。FAIL = セットアップ失敗 = Dynamic を動かしても無意味
- main ブランチは現在 Static 全 FAIL（知識ファイル不足）→ main が PASS するよう改善が必要
- Static FAIL が1件でも出たら Dynamic を実行せず終了する変更は実装済み（未コミット）
- Static Notes 列削除も実装済み（未コミット）

**手順:**

**Step A: test-setup.sh 改善コミット**
- [x] Static FAIL で即終了 + Notes 列削除 をコミット・プッシュ — committed `5eb22528e`

**Step B: main の Static FAIL 原因調査 → 修正**
- [x] 原因特定: verify_env が knowledge/docs の期待値をローカル nabledge-dev と比較していたため、NABLEDGE_BRANCH=main 時は常に FAIL。ロジックを「develop → ローカル参照 / それ以外 → GitHub API で該当ブランチ参照」に修正 — committed `0463039b9`

**Step C: (Step B の修正で解消済み — 削除)**

**Step D: 全バージョン実行**
- [x] `NABLEDGE_BRANCH=main bash tools/tests/test-setup.sh` — Static 全 PASS 確認済み、レポート生成済み `tools/tests/reports/main-20260527-101040.md`
- [ ] Dynamic WARN 判定実装 → main レポート再生成（Step D-1 参照）
- [ ] `NABLEDGE_BRANCH=develop bash tools/tests/test-setup.sh`

**Step D-1: Dynamic WARN 判定実装**

**背景:** main ブランチのスキルは旧ワークフローで 結論/根拠/注意点/参照 の 4 セクション形式を返さないが、実用的な回答は返している。FAIL と WARN を区別したい。

**判定ロジック:**
- PASS — SKILL.md 読込済み + 4セクション揃い + 順序正しい
- WARN — SKILL.md 読込済み + セクション形式不一致 + `claude -p` による内容判定で「実用的な回答」と判定
- FAIL — SKILL.md 未読込 OR 回答テキスト空 OR `claude -p` 判定で「回答になっていない」

**`claude -p` 判定プロンプト（スクリプト内でのみ使用）:**
```
あなたはNablarchフレームワークの専門家です。
以下のテキストを読み、これが「Nablarchに関する技術的な質問への実用的な回答」になっているかを判定してください。
YESまたはNOのみ答えてください。

<text>
{final_answer_text の先頭 2000 文字}
</text>
```

**`verify_fail` の扱い:** WARN は `verify_fail` をセットしない（exit 0）。
**Notes:** WARN の場合は `format mismatch (content OK)` + 不足セクション名を記載。

**実装箇所:** `test-setup.sh` の `verify_dynamic` 関数内、`result_status` 決定ロジック（行 520 付近）。

**Steps:**
- [ ] `verify_dynamic` の result_status 決定ロジックを PASS/WARN/FAIL の 3 値に変更
  - `answered=0` かつ `final_answer_text` 非空 の場合 → `claude -p` で判定
  - `claude -p` が YES → WARN、NO → FAIL
  - `verify_fail` は FAIL のみセット（WARN はセットしない）
  - Notes: WARN は `format mismatch (content OK); missing sections: ...`、FAIL は従来通り
- [ ] main レポートを再生成して確認（WARN が正しく出るか）
- [ ] コミット・プッシュ

**Step E: レポート内容の詳細セルフチェック（ユーザー報告前）**
- [ ] 各レポートの全フィールドを目視確認
  - Branch / Commit / Repository / Run datetime / Version filter が正しいか
  - Static: 環境名・結果が正しいか
  - Dynamic: 各行の Version / Tool / Result / Time / tokens / Cost / Keywords が妥当な範囲か
  - Totals: 合計値が各行の足し算と一致するか
- [ ] CC input tokens: main（知識少）< develop（知識多）になっているか確認
- [ ] GHC output tokens: PASS 行は十分な量（500+ tokens）か確認（極端に少ない場合は空振りの可能性）
- [ ] FAIL の Notes が正確か（missing sections が本当に欠けているかログで確認）

**Step F: 比較レポート出力・コミット・プッシュ**
- [ ] `tools/tests/reports/comparison-main-vs-develop-YYYYMMDD.md` を更新（旧版は削除）
- [ ] コミット・プッシュ
- [ ] ユーザーに結果報告

## Not Started

---

## Done

- [x] Task 1: Create `tools/tests/reports/` directory with `.gitkeep` — committed `738c5175e`
- [x] Task 2: Add metrics collection to `verify_dynamic` in `test-setup.sh` — committed `e03a125bc`
- [x] Task 3: Add static check results collection to `verify_env` in `test-setup.sh` — committed `e03a125bc`
- [x] Task 4: Add report generation function and write report file — committed `e03a125bc`, fixed `a53aaf51d`
- [x] Task 5: Preview report Markdown rendering — committed `18fc71f3e`
- [x] Task 6: Update README to document `main` branch testing and before/after comparison — committed `3858608d0`
- [x] Task 7: Diff check — committed `c644d86cd`
- [x] Task 8: Expert review (Software Engineer + QA Engineer) — 2 Findings found and fixed in `a53aaf51d`, committed `58f2de046`
- [x] Task 9: Fix answered/keyword detection for JSON log formats (CC + GHC) — committed `26b2a9655`
- [x] Task 10: Request user PR review
- [x] Task 11: Apply user feedback (Notes column, Commit SHA, GHC output tokens) + generate reports (main/develop all versions) + comparison report — committed `4175549c0`, `26b673eeb`, `f6297d6ee`
