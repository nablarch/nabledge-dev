# ids L1 以下 14件 根本原因分析

**方法**: 各 scenario で `retrieved` (search.json `sections_read`) / `answer.md` / `judge.json` / 元の知識ファイル を突き合わせ、症状ではなく原因を確定する。

**原因カテゴリ**:
1. **AI-1 検索漏れ** — 根拠が retrieved にないが、知識ファイル内の別セクションに実在
2. **AI-3 回答ミス** — 根拠が retrieved にあるのに answer が反映していない
3. **知識ファイル不備** — v6 知識ファイル全体に根拠が存在しない
4. **A-fact 過剰/狭すぎ** — a_facts または expected_sections の設計不備

---

## per-scenario

### impact-01 (L1) — AI-1 検索漏れ
- 症状: A1/A2/A3 MISSING or CONTRADICTED (TMH 境界/往路復路/配置制約)
- 原因: TMH s1 (概要 + 境界定義) / s3 (配置制約) が retrieved に入らず、AI-3 は LoopHandler s5/s6 を主役に推論 → LoopHandler と TMH の主役取り違え
- レバー: TMH s1/s3 の hints に「トランザクション境界 / バッチ / コミット / ロールバック」追加

### impact-03 (L1) — AI-3 + AI-1
- 症状: 並列バッチ DB 接続の MISSING/HALLUCINATION
- 原因: (a) MTH s7 に「親スレッドで DB 必要なら本ハンドラより前に DbConnectionManagementHandler」とあるのに answer が省略 (AI-3), (b) TMH s3 未検索 + LoopHandler s5 を無関係に混入 (AI-1)
- レバー: (a) AI-1 が LoopHandler を並列 DB 問題で除外, (b) TMH s3 hints に「並列実行/MultiThread/配置順序」, (c) MTH s7 hints に「親スレッド側配置」

### impact-06 (L2 — ボーダー、AI-3)
- 症状: script 要素に `tag-csp_nonce_tag` を誤例示
- 原因: libraries-tag s10 末尾の「script は `tag-script_tag` 推奨」補足を AI-3 が読み落とし
- レバー: s10 の補足を独立セクションに切り出すか hints 強化

### impact-07 (L1) — AI-1 検索漏れ
- 症状: InternalRequestIdAttribute / ハンドラ配置順 3件 MISSING
- 原因: permission_check_handler s3 (制約) が retrieved に含まれていない。s3 に配置順序のすべてが書かれている
- レバー: permission_check_handler s3 の hints に「フォワード/内部フォワード/認可/InternalRequestIdAttribute」追加

### impact-08 (L1) — AI-1 検索漏れ
- 症状: @AssertTrue 相関OK / null スキップ が MISSING
- 原因: bean_validation s8 (フィールド間相関) が未検索。retrieved は s9/s13 のみ
- レバー: bean_validation s8 の hints に「相関チェック/重複/同一性確認/@AssertTrue」追加

### impact-10 (L1) — AI-3 回答ミス
- 症状: PermissionCheckHandler がスレッドローカルに Permission を保持、invalidate 未記述
- 原因: permission_check_handler s4 と session_store s4 の両方が retrieved にあるのに、AI-3 が role_check (s3) に引きずられて @CheckRole 中心の answer を生成 → 主役誤認
- レバー: AI-3 プロンプトで「retrieved 内の主役判定」ルール。session_store s4 hints に「ログアウト/invalidate」

### req-04 (L1) — AI-1 + A-fact
- 症状: JSP useToken 属性 PARTIAL / name 変更 MISSING / db_double_submit HALLUCINATION
- 原因: use_token s1 (JSP useToken 属性) 未選択、db_double_submit s1 を不要に含める。「name 変更可能」は a_fact 側の細部要求
- レバー: use_token s1 の hints に「JSP/useToken 属性/form タグ/二重サブミット」、AI-1 に「基本機能優先、オプションは明示された場合のみ」

### req-05 (L2 — ボーダー、A-fact)
- judge level=2 達成済。thread_context_handler s7 が retrieved にあり正しく使われているが judge が OVER-REACH 判定
- 原因: scenarios の expected_sections が狭い
- レバー: expected_sections に `handlers-thread_context_handler|s7` 追加

### req-09 (L0 / None) — AI-3 + 知識
- 症状: AI-1 が空を返し AI-3 が answer 未生成
- 原因: (a) 「レート制限はビルトインなし」を明示できる知識セクションが無い, (b) AI-3 は retrieved=空で処理を諦めるが「見つからない」と明示すべき
- レバー: AI-3 プロンプトに「retrieved 空時の明示フォールバック」。可能なら「Nablarch 非対象機能」インデックスを検討

### req-10 (L1) — AI-1 検索漏れ
- 症状: HttpAccessLogHandler クラス名 / 配置順 MISSING, jaxrs 系 HALLUCINATION
- 原因: handlers-http_access_log_handler s1 (クラス名) と s3 (配置制約) 未選択、jaxrs_access_log 系を過剰に含めた
- レバー: handlers-http_access_log_handler s3 hints に「配置制約/ThreadContextHandler/HttpErrorHandler/SessionStoreHandler/監査ログ」、AI-1 原則「ハンドラ質問では s1 + 制約系をセット選択」

### review-01 (L2 — ボーダー、A-fact)
- judge level=2 達成済。nablarch-batch-batch.json s1 (フレームワーク選択) が expected 外で OVER-REACH 判定
- レバー: expected_sections に `nablarch-batch-batch|s1` 追加

### review-03 (L2 — ボーダー、A-fact)
- judge level=2 達成済。発展的手動設定 (RoutesMapping + JaxRsMethodBinderFactory) の 1 MISSING のみ
- レバー: a_fact の該当項目を optional 扱いに

### review-08 (L1) — AI-3 + AI-1
- 症状: concurrentNumber デフォルト / shutdownNow / データリーダクローズ が MISSING、排他制御系を OVER-REACH
- 原因: (a) MTH s5/s8 が retrieved にあるのに AI-3 が該当項目を拾えない (主因), (b) AI-1 が排他制御/multiple_process をスコープ外なのに含めた (副因)
- レバー: AI-1 に「主トピック外周辺を絞る」、AI-3 に「retrieved の列挙項目を漏らさず」

---

## 集計

| 主原因 | 件数 (主) | 件数 (副) |
|---|---|---|
| AI-1 検索漏れ | 4 (impact-07, impact-08, req-10, impact-01) | 2 (impact-03, req-04, review-08) |
| AI-3 回答ミス | 4 (impact-06, impact-10, req-09, review-08) | 1 (impact-03) |
| 知識ファイル不備 | 0 | 1 (req-09) |
| A-fact 設計不備 | 3 (req-05, review-01, review-03 — いずれも L2 ボーダー) | 1 (req-04) |

## 改善方針 (優先順)

1. **AI-1 hints 充実 (4〜6 件に効く)** — 下記セクションの hints に配置制約・質問文脈キーワードを追加:
   - `handlers-transaction_management_handler` s1, s3
   - `handlers-permission_check_handler` s3
   - `handlers-http_access_log_handler` s1, s3
   - `bean_validation` s8
   - `use_token` s1
   - `session_store` s4

2. **AI-1 select プロンプト原則追加** — 「ハンドラ質問では対象ハンドラの s1(概要) + 制約系(s3) + 機能セクション をセット選択」「主トピック外の周辺機能 (排他制御/multiple_process/LoopHandler) は質問が明示した場合のみ」

3. **AI-3 プロンプト補強** — (a) retrieved 内列挙項目 (手順・数値付き箇条書き) を省略しないチェックリスト、(b) 主役が複数候補ある場合の優先順 (permission > role_check, TMH > LoopHandler for 境界)、(c) retrieved 空時の「見つからなかった」明示フォールバック

4. **A-fact 側の微調整 (3 件が L2 ボーダー確定)** — req-05/review-01 の expected_sections 拡張、review-03 の a_fact optional 化、req-04 の細部要求 (name 変更) 削除

## 次アクション

- 上記 1 (AI-1 hints) を小さい PR 単位で適用 → 該当 scenario だけ rejudge で効果測定
- hints 変更は knowledge/*.json の編集であり create-side であるため、変更後に該当 scenario を個別 rejudge するだけで検証可能
- hints 追加の前に `.claude/rules/design-decisions.md` / PE レビューを通す (プロンプト変更は PE review 必須ルール)
