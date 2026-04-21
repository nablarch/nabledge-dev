# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-22 (session 38, Phase 21-I complete)

全フェーズ TDD（verify が質問ゲートのため順序に注意）:
- **verify 追加時**: verify テスト作成 → RED確認 → verify チェック実装 → GREEN確認 → RBKC 実装 → verify GREEN確認 → サブエージェント品質チェック
- **CLI 追加時**: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

## verify 実装ルール（絶対遵守）

- **設計書通りに実装する**: `tools/rbkc/docs/rbkc-verify-quality-design.md` が唯一の実装仕様。問題・疑問が生じたらユーザーに相談し、勝手に判断して実装を変更しない
- **設計書 → 実装の順序**: ユーザーと合意して verify の内容を見直す場合は、必ず設計書を更新してから実装を進める。設計書と実装の整合は常に維持する
- **マトリクスの ✅ 条件**: 実装が完了し、かつ実際の RBKC 出力に対して動作を確認した時点で初めて ✅ にする

---

## 現状サマリー（session 38 Phase 21-I 完了後）

`bash rbkc.sh verify 6` → **FAIL 合計 139件**（QL1 314件解消済み）

| カテゴリ | 件数 | 受け皿 Phase |
|---|---|---|
| hints `file entry not matched by any knowledge section` | 74 | Phase 21-J |
| hints `docs MD hints differ from hints file` | 65 | Phase 21-J |

---

## In Progress

### Phase 21-J: hints mismatch 139件の解消

**背景**: Phase 21-H で hints file を R1〜R6 ルールでゼロベース再生成したが、verify に残る FAIL が 139 件ある。内訳:
- 74件 = hints file にあるが JSON section.title に一致する section が無い（`file entry not matched`）
- 65件 = 一致するが docs MD 側に hints ブロックが出ていない／値が違う（`docs MD hints differ`）

両者は同根（title マッチング or hints 注入の取りこぼし）の可能性が高い。

**Steps:**
- [ ] 74件を 10 件サンプルし、hints file の title と JSON 側 section title のペアを出力
- [ ] 65件を 10 件サンプルし、JSON section / docs MD セクション / hints file の三者を突き合わせ
- [ ] ミスマッチの全パターンを分類（例: 正規化差分 / section 構造差分 / 同名見出しの round-robin 取りこぼし 等）
- [ ] ユーザーに分類結果と修正方針を提示・承認
- [ ] TDD: 該当パターンを再現する最小 fixture → 実装（converter or hints.py or docs.py どこに帰属するか確定してから）→ GREEN
- [ ] rbkc create 6 → verify 6 で hints FAIL 0 件確認
- [ ] サブエージェント品質チェック (SE + QA)
- [ ] コミット

---

## Not Started

### Phase 21-G: verify パイプラインの配線漏れを解消（QC1/QC2/QC3/QC4 等）

**問題（事実）**:
- `scripts/verify/verify.py` に実装された RST/MD 用チェック (`check_content_completeness`, `check_format_purity`, `check_hints_completeness`, `check_external_urls`) が、`scripts/run.py` の verify オーケストレーションから一切呼ばれていない
- `verify_file()` は `fmt != "xlsx"` で即 return — RST/MD では完全に noop
- 設計書マトリクス 4章 の ❌ は「verify が検証していない」状態を正しく示していた

**このフェーズの前提**:
- Phase 21-I / 21-J を先に完了させ、現在検知されている FAIL を全て解消してから配線する
- そうしないと、配線直後に 21-I/21-J 由来の FAIL が大量に QC2 として顕在化して切り分け困難になる

**Steps:**
- [ ] 調査: verify.py 内の各 check_* 関数と設計書マトリクスとの対応を整理（どの関数がどの QC/QL/QO に対応するか）
- [ ] 調査: run.py から呼ばれていない check_* 関数を列挙
- [ ] 配線計画をユーザーに提示・承認（どの check を RST/MD/Excel それぞれで実行するか）
- [ ] TDD: 配線後に特定の既知不正ケース（テスト fixture）で RED を確認
- [ ] run.py に check_* 関数群を配線
- [ ] サブエージェント品質チェック
- [ ] rbkc create 6 → verify 6 FAIL 0件を確認（新たに顕在化する FAIL があれば個別 Phase 化）
- [ ] 設計書 rbkc-verify-quality-design.md のマトリクスを ❌→✅ に更新（配線済みの項目のみ）
- [ ] コミット

---

### Phase 21-C: リリースノート・セキュリティ対応表の粒度が粗い

**問題**: 現状は全シート×全行を1セクションに連結 → 毎回全行ロード、検索で使えない。
行単位（変更1件=1セクション）にすれば個別レコードとして検索可能になる。

**Steps:**
- [ ] 全容把握: v6リリースノート・セキュリティExcelのシート構造・行構造を調査しセクション分割設計を確定
- [ ] ユーザーに設計案提示・承認
- [ ] xlsx_releasenote TDD: 行単位セクション分割テスト（RED → GREEN）
- [ ] xlsx_security TDD: 行単位セクション分割テスト（RED → GREEN）
- [ ] verify 更新: 新粒度に対応したチェック
- [ ] rbkc create 6 → verify 6 FAIL 0件確認
- [ ] コミット

---

### Phase 18: 統合検証 — v6 完了

**前提**: Phase 21-I / 21-J / 21-G 完了後

**Steps:**
- [ ] nabledge-test v6 実行 — ベースライン比で劣化なし確認
- [ ] 問題があればユーザー報告

---

### Phase 19: 統合検証 — v5

**前提**: Phase 18 完了後

**Steps:**
- [ ] `bash rbkc.sh create 5` → `bash rbkc.sh verify 5` — FAIL 0件
  - FAIL が出た場合: 分析 → ユーザー報告 → 承認後修正 → 再 verify
- [ ] nabledge-test v5 — 劣化なし確認
- [ ] コミット

---

### Phase 20: 統合検証 — v1.4 / v1.3 / v1.2

**前提**: Phase 19 完了後

**Steps:**
- [ ] `bash rbkc.sh create 1.4` → `bash rbkc.sh verify 1.4` — FAIL 0件
- [ ] `bash rbkc.sh create 1.3` → `bash rbkc.sh verify 1.3` — FAIL 0件
- [ ] `bash rbkc.sh create 1.2` → `bash rbkc.sh verify 1.2` — FAIL 0件
  - 各バージョンで FAIL が出た場合: 分析 → 報告 → 承認 → 修正 → 再 verify
- [ ] nabledge-test v1.4 / v1.3 / v1.2 — 劣化なし確認
- [ ] コミット（全3バージョン）

---

## Done

- [x] Phase 21-A: docs/README.md 未生成 — committed `c238dc8f`
- [x] Phase 21-B: hints 永続化と完全一致チェック — verify check 実装 / `build_hints_index` file_id 正規化 / `catalog_index` last-wins バグ修正 / `extract_hints.py` 作成 / v6.json 初版生成。残 FAIL の分析は 21-D/21-I/21-J に分割
- [x] Phase 21-D: JSON スキーマゼロベース見直し（ソース忠実）— session 31〜37 で `_PREAMBLE_TITLE` 廃止、top-level content + hints 導入、converter/docs/index/verify 同時改修、read-sections.sh 5版同時修正 — commits `603c5ade` / `23bb7e5f` / `4b6531fe` / `49e467e2` / `3154264e`
- [x] Phase 21-E（旧 file=[] 46件）: Phase 21-D で大半解消。残存は Phase 21-J に統合してクローズ
- [x] Phase 21-F（旧値不一致 4件）: Phase 21-D で解消。Phase 21-J に統合してクローズ
- [x] Phase 21-H: hints file 生成ロジックの再設計（R1〜R6 ルールで 5 版 hints/v{V}.json を ゼロベース再生成、同名見出し対応の配列スキーマ化）— commits `9ffefa08` / `5adf4404` / `60b16f98` / `ca7a924f` / `f7a4db40` / `fbd2b52f` / `8ed9aa0c` / `c286de77` / `83031d95` / `d015c03e` / `80a3ed48`（verify GREEN 確認は 21-J にバトン）
- [x] Phase 21-I: QL1 回帰 314件解消 — `_json_text()` に top-level content 追加（設計書 `rbkc-verify-quality-design.md:170` 通りに修正、false-positive fix）。TDD: RED 3件 → GREEN、regression/MD top-level/`_json_text()` 直接テスト 5件追加（合計244 PASS）。SE 5/5 / QA 5/5（追試対応後）

- [x] Phase V-skip: verify() FAIL on missing JSON/docs MD — committed `86dd660e`
- [x] Phase V-hints: KC-format files deleted from nabledge-6 — committed `c92accc4`
- [x] Phase V2-4-post: converter fixes (QC1, QL1) + tests — committed `6ce09683` / `21ca2783`
- [x] Phase V4: rbkc create 6 + verify 6 FAIL 0件 — committed `dbfc0582`
- [x] Phase V0: hints carry-over 実装 — committed `d155c92e`
- [x] Phase V1: 旧 verify 削除・スタブ化 — committed `2727facc`
- [x] Phase V2-1/V2-2/V2-3: QO5 / QC5 / QC6 verify 実装 — committed `a0c7abf1`
- [x] Phase V2: verify 実装計画確定
- [x] Phase 17-R: verify 品質保証設計ドキュメント作成・レビュー — commits `d020efd2`〜`2464a55c`
- [x] Phase 1: KC cache → hints mapping — committed `f78304b4`
- [x] Phase 2: RST converter with full directive support — commits `5913ff6e` / `1b62c4c4` / `9cbbc729`
- [x] Phase 3: Hints extraction Stage 1 + Stage 2 merge — committed `ac294cdb`
- [x] Gap fill: Phase 2 test修正 + Phase 1/3 E2Eテスト追加 — committed `010d0c2f`
- [x] Phase 4: Cross-reference resolution + asset copying — commits `9336f900` / `87654126`
- [x] Phase 5: MD converter — committed `232df686`
- [x] Phase 6: Excel converters — committed `edce71eb`
- [x] Phase 7: Index + browsable docs generation — committed `dc019759`
- [x] Phase 8: CLI + create/update/delete/verify operations — committed `5baf7a6d`
- [x] Phase 9: v1.x固有ディレクティブ対応 — committed `bc632d0f`
- [x] Phase 10: コンバータ修正 (10-1〜10-6) — commits `54fe3ef8` / `d5a6961d` / `cd856500` / `d2303716` / `7eac70f6` / `10b239b1`
- [x] Phase 11: verify 完全チェック化 — committed `6c664a59`（Phase 12 で書き直し済み）
- [x] Phase 12: verify 完全書き直し — committed `1eff2740`
- [x] Phase 13: create pipeline 完全修正 — committed `e85488cb`
- [x] Phase 14: classify 出力パス衝突修正 — committed `b6a4a630`
- [x] Phase 15: converter/verify URL バグ修正 — committed `63ac0ec9`
- [x] Phase 16: toctree-only index.rst token coverage 修正 — committed `37d6e547`
- [x] docs.py: assets/ リンクを docs MD の位置から相対解決 — committed `008e8420`
- [x] Rules整理: development.md追加、work-log/rbkc/pr.md更新 — committed `aa08f489`
