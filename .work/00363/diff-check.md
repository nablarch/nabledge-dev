# Diff Check — PR #365 (Issue #363)

**Date**: 2026-06-04 (updated 2026-06-05)
**Branch**: 363-javadoc-knowledge vs main

## Summary

全 4721 ファイル変更（想定外: 0件）。全バージョン verify FAIL=0（Task 6-A で QO3 false positive 修正済み）。

---

## 変更カテゴリ別件数

| カテゴリ | 件数 | 根拠 |
|---------|------|------|
| knowledge JSON 既存更新（v6 javadoc リンク追加） | 316 | `git diff --name-only \| grep 'nabledge-6/knowledge/' \| grep -v '/javadoc/'` = 316 |
| knowledge JSON 既存更新（v5 javadoc リンク追加） | 401 | `git diff --name-only \| grep 'nabledge-5/knowledge/' \| grep -v '/javadoc/' \| grep -v 'index\.toon'` = 401 |
| knowledge JSON javadoc 新規（v6） | 582 | `ls knowledge/javadoc/*.json \| wc -l` = 582 |
| knowledge JSON javadoc 新規（v5） | 595 | `ls knowledge/javadoc/*.json \| wc -l` = 595 |
| docs MD 既存更新（v6 javadoc リンク追加） | 163 | `git diff --name-only \| grep 'nabledge-6/docs/' \| grep -v '/javadoc/'` = 163 |
| docs MD 既存更新（v5 javadoc リンク追加） | 165 | `git diff --name-only \| grep 'nabledge-5/docs/' \| grep -v '/javadoc/'` = 165 |
| docs MD javadoc 新規（v6） | 582 | `ls docs/javadoc/*.md \| wc -l` = 582（JSON と 1:1 対応、missing 0件確認済み） |
| docs MD javadoc 新規（v5） | 595 | `ls docs/javadoc/*.md \| wc -l` = 595（JSON と 1:1 対応、missing 0件確認済み） |
| knowledge JSON 既存更新（v1.4 crossdoc `.md`→`.json` 拡張子変更） | 353 | `git diff --name-only \| grep 'nabledge-1.4/knowledge/'` = 353（うち index.toon 削除 1件含む） |
| knowledge JSON 既存更新（v1.3 crossdoc `.md`→`.json` 拡張子変更） | 232 | `git diff --name-only \| grep 'nabledge-1.3/knowledge/'` = 232（うち index.toon 削除 1件含む） |
| knowledge JSON 既存更新（v1.2 crossdoc `.md`→`.json` 拡張子変更） | 230 | `git diff --name-only \| grep 'nabledge-1.2/knowledge/'` = 230（うち index.toon 削除 1件含む） |
| index.toon 削除（v5/v1.2/v1.3/v1.4） | 4 | `git diff --name-only \| grep 'index\.toon'` = 4件（v5 含む）。v1.x 分は上記 v1.x 行の 353/232/230 に含まれる |
| workflows/semantic-search.md（v6/v5） | 2 | Step 4 Javadoc 拡張追加 |
| tools/rbkc/scripts/（実装） | 10 | `git diff --name-only \| grep 'tools/rbkc/scripts/'` = 10（javadoc.py/linkfmt.py/verify.py 等） |
| tools/rbkc/docs/（設計書） | 2 | rbkc-converter-design.md / rbkc-verify-quality-design.md |
| tools/rbkc/tests/ut/（テスト） | 9 | test_javadoc.py/test_verify.py 等 |
| tools/rbkc/lib/（jar） | 1 | source-to-document-converter-0.0.1.jar |
| tools/benchmark/（Task 4/5 成果物） | 475 | `git diff --name-only \| grep 'tools/benchmark/'` = 475（scenarios/qa.json + run-1〜3 結果） |
| .work/00363/（作業ログ） | 7 | notes.md / tasks.md / verify-baseline.md / diff-check.md / verify-2j-diff.md / review-by-software-engineer.md / review-by-qa-engineer.md |

**合計**: 4721（上記の重複カウントなし: v1.x 行は index.toon を含む。index.toon 行は参考表示のみ）

**v1.x の変更について**: v1.2/v1.3/v1.4 の変更は javadoc 対応ではなく、Task 3-B（crossdoc リンク拡張子 `.md`→`.json` 正規化）の波及。RBKC 再生成時に全件適用された。

---

## 想定外変更

なし。

---

## verify 実行結果（最終）

| バージョン | FAIL 件数 | 内容 |
|-----------|-----------|------|
| v6 | 0 | All OK（Task 6-A で QO3 false positive 修正済み） |
| v5 | 0 | All OK（Task 6-A で QO3 false positive 修正済み） |
| v1.4 | 0 | All OK |
| v1.3 | 0 | All OK |
| v1.2 | 0 | All OK |

**QO3 対処（Task 6-A 完了）**:
- `docs/javadoc/` を QO3 のページ数カウントから除外する false positive fix を実装
- verify は `docs/javadoc/` 配下をカウント対象外とするよう修正（`85cc4aa00`）
- 全バージョン FAIL=0 確認済み（2026-06-04）

---

## knowledge JSON / docs MD → Javadoc リンク整合性

### knowledge JSON 側

埋め込みリンク形式: `[DisplayText](../../javadoc/javadoc-{FQCN}.json)`

**確認済み（全件 リンク元ディレクトリからの相対パス解決検証）:**
- 検証方法: `scripts/verify.py` の `check_ql1_link_targets` が JAVADOC_LINK_RE でリンクを抽出し、リンク元ファイルの階層から `../../javadoc/{file_id}.json` を解決して対象ファイルの実在を確認
- v6 + v5 合計 1741件: パス解決成功、broken link 0件
- 確認完了: わざと存在しない file_id を参照するリンクを挿入すると FAIL になることを実証確認済み（`d646d3465`）

### docs MD 側

埋め込みリンク形式: `[DisplayText](../../javadoc/javadoc-{FQCN}.md)`

- 検証方法: 同上（`check_ql1_link_targets` が docs MD 側も検証。`../../javadoc/{file_id}.md` の実在確認）
- v6: 163件の既存 docs MD に javadoc リンク追加、パス解決全件成功
- v5: 165件の既存 docs MD に javadoc リンク追加、パス解決全件成功
- 確認完了: docs MD 側も存在しない file_id でFAILを確認済み

---

## docs MD（解説書ページ）からの Javadoc MD 遷移

docs MD に対応する Javadoc MD の存在:
- v6: `knowledge/javadoc/*.json` 582件 ↔ `docs/javadoc/*.md` 582件（missing 0件確認済み）
- v5: `knowledge/javadoc/*.json` 595件 ↔ `docs/javadoc/*.md` 595件（missing 0件確認済み）
- 確認方法: `set(json names) - set(md names)` = 空集合

ファイルの存在だけでは遷移可能性の保証にならない。リンク元からの相対パスが実在ファイルに届くことを verify で検証する必要がある（後述「リンク切れ全壊インシデント」参照）。上記の `check_ql1_link_targets` による相対パス解決検証がその保証手段。

---

## 生成内容スポットチェック（現物確認）

Java ソース（`.tmp/javadoc-sources/`）と生成ファイル（knowledge JSON / docs MD）を突き合わせ。

| # | クラス | バージョン | 確認結果 |
|---|--------|-----------|---------|
| 1 | `FailureLogUtil` | v6 | フィールド名・メソッドシグネチャ・説明文すべてソースと一致 |
| 2 | `MessagingAction` | v6 | クラス説明・コンストラクタ・テンプレートメソッド一致 |
| 3 | `DateTimeConfiguration` | v6 | interface として正しく生成、説明文一致 |
| 4 | `PropertiesStringResourceLoader` | v6 | フィールド・`locales`・`setLocales` など全メソッド一致 |
| 5 | `MessagingProvider` | v5 | メソッドシグネチャ・説明文・戻り値記述一致 |
| 6 | `FailureLogUtil` docs MD | v6 | パッケージ名・クラス説明・作成者すべてソースと一致 |
| 7 | `MessagingProvider` docs MD | v5 | パッケージ名・インタフェース説明・作成者すべてソースと一致 |

---

## 備考

- **v1.x の javadoc 対応について（Not Applicable）**: v1.4/v1.3/v1.2 の knowledge ファイルを全件スキャンした結果、javadoc リンク参照は3バージョンとも 0件。RST ソースに `:java:extdoc:` が存在しないため、javadoc リンクという入力自体が存在しない。利用者が辿れず困るリンクは 1本も生成されておらず実害なし。Issue #363 SC「all 5 versions」に対しては、v1.x は javadoc 機能の **Not Applicable（該当なし）** であり、リンクを持つ v6/v5 で正しく機能することで SC の趣旨は満たされる。
- verify は RBKC 実装から独立して動作（`_build_javadoc_map()` が `knowledge/javadoc/` 配下を直接走査）

---

## インシデント履歴

### 2026-06-04: リンク切れ全壊 + verify 検知漏れ

**事象**: PR レビュー中に kiyoさんが knowledge JSON の javadoc リンクをクリックして 404 を確認。全 1741 件がリンク切れだった。

**原因（2点）**:
1. `emit_javadoc_link` が `../javadoc/` (1段) を生成していた。全知識ファイルは深さ2 (`knowledge/{type}/{category}/`) に存在するため、リンク先は `knowledge/{type}/javadoc/` を指し、正しい `knowledge/javadoc/` に届かなかった。正しくは `../../javadoc/` (2段)。
2. `check_ql1_link_targets` が `CROSSDOC_LINK_RE` のみ参照し `JAVADOC_LINK_RE` を未使用だったため、javadoc リンクのターゲット実在チェックが行われず FAIL=0 のまま全壊を見落とした。

**修正** (`d646d3465`, `44f8d8083`):
- `emit_javadoc_link` のパスを `../../javadoc/` に修正（crossdoc リンクと同じ2段に統一）
- `check_ql1_link_targets` に JAVADOC_LINK_RE によるターゲット実在チェックを追加（JSON側・docs MD側両方）
- 修正後: 1741件パス解決 100% 確認、存在しない file_id でFAILすることを実証

**教訓**: ファイルの存在確認だけでは遷移可能性を保証できない。リンク元ディレクトリからの相対パス解決が実在ファイルに届くことを verify で検証する必要がある。また、verify に新たなリンク形式（JAVADOC_LINK_RE）を追加する際は、CROSSDOC_LINK_RE と対称的に全チェックを適用すること。
