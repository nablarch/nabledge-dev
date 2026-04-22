# Stage 3 — 30 scenarios

- mean judge level:       3.00
- judge distribution:     {'0': 0, '1': 0, '2': 0, '3': 30}
- mean candidate count:   81.8
- mean cost (USD):        0.5276
- mean wall (s):          82.7

| id | facets | filter | picks | judge | reason | cost | wall |
|----|--------|--------|-------|-------|--------|------|------|
| review-01 | processing-pattern,component/nablarch-batch,libraries | 57 (none) | 8 | 3 | Asked: ファイル明細→DBインポートの夜間バッチ推奨構成。Expected core: 都度起動バッチ選択理由・ハンドラキュー構成・BatchAct... | 0.6229 | 92.1 |
| review-02 | processing-pattern,component,setup/web-application,handlers,blank-project | 95 (none) | 6 | 3 | Asked: ウェブアプリの基本処理構成の推奨方法。Expected core: NablarchServletContextListener+WebFr... | 0.5414 | 85.7 |
| review-03 | processing-pattern,component,setup/restful-web-service,handlers,configuration | 67 (none) | 6 | 3 | Asked: REST APIの処理構成パターン。Expected core: restful_web_service推奨・ハンドラキュー構成・処理フロー... | 0.5163 | 81.7 |
| review-04 | component,processing-pattern/libraries,web-application | 68 (none) | 6 | 3 | Asked: 必須・桁数・形式チェックをNablarch流に楽に書く方法。Expected core: Bean Validation推奨、@Requir... | 0.5015 | 71.9 |
| review-05 | processing-pattern,component/restful-web-service,libraries | 56 (none) | 5 | 3 | Asked: REST API JSON検証でエラーをどう返すか。Expected core: Bean Validation推奨理由、@Valid適用方... | 0.4823 | 67.3 |
| review-06 | processing-pattern,component/web-application,handlers,security-check | 78 (none) | 4 | 3 | Asked: WebアプリのCSRF対策の仕組みと設定方法。Expected core: CsrfTokenVerificationHandlerの存在、... | 0.5028 | 71.1 |
| review-07 | processing-pattern,component/web-application,handlers,security-check | 78 (none) | 5 | 3 | Asked: NablarchのWeb画面でCSPを有効にする標準方法。Expected core: SecureHandlerにContentSecur... | 0.5026 | 76.9 |
| review-08 | processing-pattern,component/nablarch-batch,handlers,libraries | 113 (none) | 6 | 3 | Asked: 常駐バッチ並列化時のDB接続と排他制御の注意点。Expected core: concurrentNumber指定・DbConnection... | 0.5402 | 87.0 |
| review-09 | component/libraries | 46 (none) | 4 | 3 | Asked: for文1件ずつ更新を一括化する仕組みは？。Expected core: UniversalDAO の batchUpdate + 排他制御... | 0.4818 | 72.0 |
| review-10 | check,development-tools/security-check,java-static-analysis | 2 (none) | 1 | 3 | Asked: バージョンアップで壊れにくいコードにするため使用不許可APIをチェックする方法。Expected core: 静的解析ツール（Intelli... | 0.4321 | 60.6 |
| impact-01 | component,processing-pattern/handlers,nablarch-batch | 67 (none) | 5 | 3 | Asked: バッチのトランザクション境界の決まり方。Expected core: ハンドラ種別（LoopHandler の commitInterval... | 0.4920 | 69.1 |
| impact-02 | processing-pattern,component/web-application,handlers,libraries | 124 (none) | 6 | 3 | Asked: WebアプリへのCSRF対策追加と相性の注意点。Expected core: CsrfTokenVerificationHandlerの追加... | 0.6390 | 79.2 |
| impact-03 | processing-pattern,component/nablarch-batch,handlers,libraries | 113 (none) | 6 | 3 | Asked: マルチスレッドバッチでのDB接続の持ち方と例外発生時の他スレッドへの影響。Expected core: DbConnectionManage... | 0.5502 | 100.2 |
| impact-04 | component/handlers | 56 (none) | 4 | 3 | DB接続一時切断時の自動リトライ機構と注意点を問う。Expected core: RetryHandler・Retryableインタフェース・ハンドラ順序... | 0.4794 | 70.5 |
| impact-05 | processing-pattern,component/web-application,libraries,handlers | 124 (none) | 7 | 3 | Asked: HIDDENストア利用法と複数APサーバ構成のハマりどころ。Expected core: `<n:hiddenStore>`タグの使い方、サ... | 0.5494 | 99.3 |
| impact-06 | processing-pattern,check/web-application,security-check | 23 (none) | 3 | 3 | Asked: CSP有効化後にonclick=が動かなくなる、JSP書き換えは必要か・避けられないか。Expected core: CSPはインラインイベ... | 0.4928 | 100.8 |
| impact-07 | processing-pattern,component/web-application,handlers,libraries | 124 (none) | 7 | 3 | Asked: 内部フォワード先も含めた画面認可制限の方法。Expected core: PermissionCheckHandler + setUsesI... | 0.5357 | 85.3 |
| impact-08 | component,processing-pattern,check/libraries,web-application,security-check | 69 (none) | 4 | 3 | Asked: Bean ValidationでのDB重複チェックがセキュリティ上安全か。Expected core: 禁止理由（未検証値でのSQLインジェ... | 0.5116 | 77.9 |
| impact-09 | component,processing-pattern/libraries,web-application | 68 (none) | 4 | 3 | Asked: マスタ定義の有効値チェックとバリデーション連携方法。Expected core: コード管理機能の仕組み・@CodeValueアノテーション... | 0.7202 | 86.5 |
| impact-10 | processing-pattern,component/web-application,handlers,libraries | 124 (none) | 6 | 3 | Asked: 画面遷移中のユーザー情報保持先と認可チェック参照方法。Expected core: セッションストア(DBストア)へのSessionUtil... | 0.5455 | 97.6 |
| req-01 | processing-pattern,component/web-application,handlers,libraries | 124 (none) | 6 | 3 | Asked: Nablarchにビルトインのログイン認証機能があるか。Expected core: 認証機能は非提供・プロジェクト実装が必要、セッション管... | 0.5434 | 89.4 |
| req-02 | component,processing-pattern/handlers,libraries,web-application | 124 (none) | 7 | 3 | Asked: Nablarchに画面アクセス制限の権限チェック仕組みはあるか。Expected core: permission_checkハンドラ方式と... | 0.5435 | 87.8 |
| req-03 | component,processing-pattern/libraries,web-application | 68 (none) | 7 | 3 | Asked: 後勝ち上書きを防ぐ排他制御の仕組みの有無。Expected core: UniversalDAO楽観的ロック(@Versionアノテーション... | 0.5059 | 90.3 |
| req-04 | processing-pattern,component/web-application,handlers,libraries | 124 (none) | 7 | 3 | Asked: 連打による二重登録防止の仕組みの有無。Expected core: 標準機能の存在、`@OnDoubleSubmission`と`@UseT... | 0.5379 | 80.3 |
| req-05 | component,processing-pattern/libraries,web-application | 68 (none) | 4 | 3 | Asked: Nablarchで画面の日英多言語対応ができるか。Expected core: 言語別プロパティファイル、XML設定（locales/def... | 0.4856 | 72.1 |
| req-06 | setup,component,processing-pattern/cloud-native,handlers,web-application,configuration | 82 (none) | 7 | 3 | Asked: スケールアウト時の注意点とセッション扱い。Expected core: ステートレス化要件・DBストアによるサーバ間セッション共有・後勝ち問... | 0.5172 | 93.3 |
| req-07 | processing-pattern,component/restful-web-service,handlers | 66 (none) | 4 | 3 | Asked: NablarchにCORS対応の仕組みがあるか。Expected core: CorsPreflightRequestHandler（OPT... | 0.4851 | 65.8 |
| req-08 | processing-pattern,component,check/web-application,handlers,security-check | 79 (none) | 4 | 3 | Asked: アップロードサイズ上限の仕組み。Expected core: MultipartHandlerのcontentLengthLimitプロパテ... | 0.4938 | 82.7 |
| req-09 | component,processing-pattern/handlers,restful-web-service | 66 (none) | 4 | 3 | Asked: NablarchにREST APIのレート制限機能があるか。Expected core: 標準機能なし＋最も近い代替の明示。Answer c... | 0.4930 | 86.0 |
| req-10 | component/handlers,libraries | 102 (none) | 7 | 3 | 監査ログのビルトイン有無を問う。期待コア: 専用機能なし＋最近傍代替(HTTPアクセスログハンドラ)の特定と誰/いつ/何の取得方法。回答は専用機能なしを明... | 0.5816 | 101.1 |
