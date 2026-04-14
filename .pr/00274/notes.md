# 作業記録 PR #274 - Per-section fix improvements

## 2026-04-08 検証準備

### 概要
Phase E の per-section fix 改善後、3つのターゲットファイルで動作確認を実施予定。

### 検証対象ファイル
1. libraries-04_Permission
2. libraries-07_TagReference
3. libraries-thread_context

### 対象ソースファイル
- `.lw/nab-official/v1.4/document/fw/02_FunctionDemandSpecifications/03_Common/04_Permission.rst`
- `.lw/nab-official/v1.4/document/fw/02_FunctionDemandSpecifications/03_Common/07/07_TagReference.rst`
- `.lw/nab-official/v1.4/document/fw/core_library/thread_context.rst`

### 実行予定コマンド
```bash
./tools/knowledge-creator/kc.sh fix 1.4 \
  --target libraries-04_Permission \
  --target libraries-07_TagReference \
  --target libraries-thread_context
```

### 環境セットアップ状況
- ✅ `.lw/` SVN チェックアウト完了（2026-04-08 16:43）
- ✅ 対象 RST ファイル確認済み
- ✅ work1 ワークツリーで実行可能な状態

### 次のステップ
1. `kc.sh fix 1.4` コマンドを実行
2. 実行ログ確認
3. 修正結果を検証
4. 必要に応じて PR 作成

### 注記
- 前回の試行で `.lw/` がないために削除されるバグが発生
- SVN update 後、ファイルが正常に揃った
- 今回は正常に修正が実行されるはず

---

## 2026-04-14 動作確認と副作用調査

### キャッシュ不整合の修正（完了）

v1.4・v1.2 のキャッシュとknowledge_dirの不整合を修正した（コミット済み）。

**v1.4:** 旧IDの孤立ファイル2件を削除（`51e08a57`）
- `testing-framework-02_RequestUnitTest-06_TestFWGuide.json`
- `testing-framework-batch-02_RequestUnitTest.json`
- 対応するassetsディレクトリ
- これらはPR #224でID整理後に残存した古いファイル。内容は新IDのファイルに引き継がれている

**v1.2:** catalog不整合修正 + FormTag.json生成（`a2449b51`）
- `libraries-07_FormTag--s1` カタログエントリ削除（キャッシュが一度も存在しなかった stale エントリ）
- `libraries-07_FormTag--s16` を single-part（part=1, total_parts=1）に変更
- `libraries-07_FormTag.json` を `--s16` キャッシュから手動生成

### section_add 動作確認：未完了

PR #295 の残タスク「`libraries-02_SqlLog` で section_add が発動することを確認する」を試みたが確認できず。

```bash
cd tools/knowledge-creator && ./kc.sh fix 1.4 --target libraries-02_SqlLog
```

結果：Phase D の findings が missing sections ではなかったため section_add はトリガーされなかった。
- `libraries-02_SqlLog--s1` → `omission @ s1`（per-section fix）
- `libraries-02_SqlLog--s17` → `hints_missing @ sections.s7`（hints fix）
- Round 2 でどちらも clean → 正常収束

section_add のトリガー条件は `"sections sN (missing)"` パターンの finding。
別のターゲットで再確認が必要。

### 問題1：glossary のリンクが破壊された（要調査）

上記の `kc.sh fix 1.4 --target libraries-02_SqlLog` 実行後、**ターゲット外**の `about-nablarch-glossary.json` が変更された。

**変更内容（`s10` セクション）：**
```diff
- 詳細: [request-util-test-online](../../development-tools/testing-framework/testing-framework-02_RequestUnitTest.json)
+ 詳細: :ref:`request-util-test-online`
```

`testing-framework-02_RequestUnitTest.json` は現在 knowledge_dir に存在するにもかかわらず、Phase M のリンク解決がリンクを `:ref:` 形式に変換した。

**現在の状態：** git でコミットされておらず、変更が working tree に残っている。

**調査が必要な点：**
- Phase M のリンク解決ロジック（`phase_m_finalize.py` → `phase_f_finalize.py`）が、なぜ存在するファイルへのリンクを解決できなかったのか
- `testing-framework-02_RequestUnitTest.json` は `--s12` single-part のマージ結果。リンク解決が参照するファイルパスやIDの照合ロジックに問題がある可能性
- このリンク破壊はカタログ整理（旧ファイル削除）の副作用か、それとも別の原因か

**調査の開始点：**
```
tools/knowledge-creator/scripts/phase_f_finalize.py  # リンク解決ロジック
tools/knowledge-creator/scripts/phase_m_finalize.py  # Phase M → Phase F 呼び出し
```

### 問題2：testing-framework-02_RequestUnitTest assets が削除された（副作用）

Phase M 実行後、`assets/testing-framework-02_RequestUnitTest/` の PNG 5件が削除された。

```
alternate_jre.png
edit_jre.png
installed_jre.png
skip_resource_copy.png
vmoptions.png
```

**原因：** これらは旧 split parts のキャッシュに含まれていたが、カタログ整理後は `--s12` のみが残存。`--s12` のキャッシュには `assert_entity.png`, `expected_download_csv.png`, `htmlDumpDir.png` の3件しかない。Phase M は knowledge_dir を削除後にキャッシュから再構築するため、`--s12` に存在しないassetsは復元されない。

**現在の状態：** git でコミットされておらず、削除が working tree に残っている。

**判断が必要な点：**
- `testing-framework-02_RequestUnitTest.json` の本文がこれら5件を参照していないなら削除で問題ない
- 参照していれば broken link になるため、キャッシュへの追加またはknowledge_dirへの手動コピーが必要

### 現在の working tree 状態

```
M  .claude/skills/nabledge-1.4/docs/README.md
M  .claude/skills/nabledge-1.4/docs/about/about-nablarch/about-nablarch-glossary.md
M  .claude/skills/nabledge-1.4/docs/component/libraries/libraries-02_SqlLog.md
D  .claude/skills/nabledge-1.4/docs/development-tools/testing-framework/testing-framework-02_RequestUnitTest-06_TestFWGuide.md
D  .claude/skills/nabledge-1.4/docs/development-tools/testing-framework/testing-framework-batch-02_RequestUnitTest.md
M  .claude/skills/nabledge-1.4/knowledge/about/about-nablarch/about-nablarch-glossary.json  ← 問題1
D  .claude/skills/nabledge-1.4/knowledge/development-tools/testing-framework/assets/testing-framework-02_RequestUnitTest/{5 PNGs}  ← 問題2
M  .claude/skills/nabledge-1.4/knowledge/component/libraries/libraries-02_SqlLog.json
M  .claude/skills/nabledge-1.4/knowledge/index.toon
M  tools/knowledge-creator/.cache/v1.4/catalog.json
M  tools/knowledge-creator/.cache/v1.4/knowledge/component/libraries/libraries-02_SqlLog--s1.json
M  tools/knowledge-creator/.cache/v1.4/knowledge/component/libraries/libraries-02_SqlLog--s17.json
?? tools/knowledge-creator/reports/20260414T112732{.md,-files.md,.json}
```

docs/ の変更・削除はいずれも Phase M による正常な再生成。
`libraries-02_SqlLog` 関連の変更は Phase D/E の正常な修正結果。
