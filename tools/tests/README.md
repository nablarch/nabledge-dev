# test-setup.sh — セットアップテスト手順

## 概要

`test-setup.sh` は Nabledge スキルのセットアップ状態を検証するスクリプトです。`.tmp/nabledge-test/` に環境を構築し、静的チェックと動的チェックを実行します。

## 手順

### Step 1: スクリプトを実行する

```bash
# 全バージョン（v6 / v5 / v1.4 / v1.3 / v1.2 / upgrade）
bash tools/tests/test-setup.sh

# バージョン指定
bash tools/tests/test-setup.sh v6
```

デフォルトは `nablarch/nabledge:develop` ブランチをテストします。ブランチを変えるには:

```bash
NABLEDGE_BRANCH=main bash tools/tests/test-setup.sh
```

### Step 2: 結果を確認する

スクリプトの標準出力に各チェックの結果が表示されます。

```
[OK]   v6/test-cc nabledge-6: SKILL.md read, answered: yes; keywords: 1/1
[WARN] v6/test-ghc nabledge-6: sections detected but out of order; keywords: 1/1
[FAIL] v5/test-cc nabledge-5: SKILL.md read: no, answered: no; keywords: 0/1
```

#### [OK] の場合

問題なし。次の環境の結果を確認してください。

#### [WARN] の場合 — sections out of order

4つのセクション（結論／根拠／注意点／参照）がすべて検出されたが、順序が「結論 → 根拠 → 注意点 → 参照」でなかった場合に発生します。

**事実確認:**

1. ログファイルを開く: `.tmp/nabledge-test/dynamic-check-{label}-nabledge-{v}.log`
   - 例: `.tmp/nabledge-test/dynamic-check-v6-test-ghc-nabledge-6.log`
2. CCの場合 — `"type":"result"` の行を抽出し、`.result` フィールドの内容を確認する:
   ```bash
   grep '"type":"result"' <log_file> | tail -1 | jq -r '.result'
   ```
3. GHCの場合 — `assistant.message_delta` の最後のメッセージIDの `deltaContent` を結合して確認する:
   ```bash
   last_id=$(grep '"type":"assistant.message_delta"' <log_file> | jq -r '.data.messageId' | tail -1)
   grep '"type":"assistant.message_delta"' <log_file> \
     | jq -r --arg id "$last_id" 'select(.data.messageId == $id) | .data.deltaContent // ""' \
     | paste -sd ''
   ```
4. 回答テキストに「結論」「根拠」「注意点」「参照」が**すべて含まれているがこの順でない**ことを確認する。

**判断:**

- 4セクション全部あって順序だけ違う → フォーマット上の差異。機能上の問題なし。レポートには WARN が記録される
- セクションが1つでも欠けていた → スクリプトのバグ（WARNにならずFAILになるはずなので、その場合はFAILの手順へ）

#### [FAIL] の場合 — SKILL.md not read

動的チェック中に SKILL.md が参照されなかった場合に発生します。スキルの知識検索が機能していないことを意味します。

**事実確認:**

1. ログファイルを開く: `.tmp/nabledge-test/dynamic-check-{label}-nabledge-{v}.log`
2. ログ内に `SKILL.md` という文字列があるか確認する:
   ```bash
   grep 'SKILL\.md' <log_file>
   ```
   → 出力なし = SKILL.md が読まれていない（FAILの原因確定）

3. 静的チェックの結果を確認する（スクリプト出力の Static Checks セクション）:
   - `[FAIL]` がある場合: SKILL.md またはコマンドファイルが正しく配置されていない
   - 確認対象: `SKILL.md` の存在、`/n{v}` コマンドファイルのパス（CC）、`n{v}.prompt.md` のパス（GHC）

4. セットアップを修正して再実行する。

#### [FAIL] の場合 — missing sections: {セクション名}

AI の回答に必須セクション（結論／根拠／注意点／参照）の1つ以上が欠けている場合に発生します。

**事実確認:**

1. ログファイルを開く: `.tmp/nabledge-test/dynamic-check-{label}-nabledge-{v}.log`
2. 回答テキストを取り出す（上記 WARN の手順 2〜3 と同じコマンド）
3. どのセクションが欠けているかを確認する（スクリプト出力の `[FAIL]` 行の `notes` 欄に列挙されている）
4. ログ内にエラーメッセージがないか確認する:
   ```bash
   grep -i 'error\|timeout\|fail' <log_file> | head -20
   ```
   - `timeout` が見つかった場合: AI の応答が 240 秒を超えた。再実行して再現するか確認する
   - エラーなしで回答が不完全な場合: スキルのワークフローが正常に完了していない可能性がある。`SKILL.md` の読み込みは成功しているかを確認する（上記 SKILL.md not read の手順 2）

### Step 3: レポートを確認する

スクリプト完了後、`tools/tests/reports/` にレポートが生成されます（例: `develop-20260527-143012.md`）。

レポートには静的チェック・動的チェックの全結果が表形式で記録されています。Step 2 で確認した事実（WARN/FAIL の内容）を踏まえ、以下を判断してください:

- **すべて PASS** → セットアップ正常。PR マージ可能
- **WARN のみ** → 機能上の問題なし。フォーマット差異として記録される
- **FAIL あり** → セットアップに問題あり。修正後に再実行してすべて PASS / WARN になることを確認する

## PR マージ前後の比較

PR マージによる影響を確認するには、main と develop の両ブランチで実行してレポートを比較します:

```bash
NABLEDGE_BRANCH=main bash tools/tests/test-setup.sh
NABLEDGE_BRANCH=develop bash tools/tests/test-setup.sh
```

生成されたレポート（`main-{datetime}.md` と `develop-{datetime}.md`）を並べて確認します。
