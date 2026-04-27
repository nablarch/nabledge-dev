# Stage 3 — 30 scenarios

- mean judge level:       3.00
- judge distribution:     {'0': 0, '1': 0, '2': 0, '3': 30}
- mean candidate count:   6.1
- mean cost (USD):        0.4270
- mean wall (s):          86.6

| id | facets | filter | picks | judge | reason | cost | wall |
|----|--------|--------|-------|-------|--------|------|------|
| review-01 | ∅/∅ | 9 (current-flow) | 0 | 3 | Asked: ファイル→DBバッチの推奨構成。Expected core: 都度起動バッチ選択、FILE to DBパターン（テンポラリテーブル）、Dat... | 0.3268 | 91.1 |
| review-02 | ∅/∅ | 9 (current-flow) | 0 | 3 | Asked: ウェブアプリの基本処理構成の組み方。Expected core: NablarchServletContextListener＋Reposi... | 0.5050 | 120.7 |
| review-03 | ∅/∅ | 5 (current-flow) | 0 | 3 | Asked: NablarchでREST APIの処理構成パターン。Expected core: ハンドラキュー推奨順序、リソースクラス(@Path/@G... | 0.3790 | 83.6 |
| review-04 | ∅/∅ | 6 (current-flow) | 0 | 3 | Asked: 必須・桁数・形式チェックのNablarch流の書き方。Expected core: Bean Validation (@Required/@... | 0.4780 | 103.1 |
| review-05 | ∅/∅ | 7 (current-flow) | 0 | 3 | Asked: REST APIのJSON入力値検証とエラーレスポンスの推奨方法。Expected core: JaxRsBeanValidationHan... | 0.3954 | 77.2 |
| review-06 | ∅/∅ | 5 (current-flow) | 0 | 3 | Asked: CSRF対策の仕組みと設定方法。Expected core: CsrfTokenVerificationHandlerの存在、ハンドラキュー... | 0.3639 | 75.3 |
| review-07 | ∅/∅ | 7 (current-flow) | 0 | 3 | Asked: NablarchのWeb画面でCSPを有効にする標準手順。Expected core: SecureHandler+ContentSecur... | 0.3246 | 64.2 |
| review-08 | ∅/∅ | 6 (current-flow) | 0 | 3 | Asked: 常駐バッチの並列DB更新における接続・排他の注意点。Expected core: DbConnectionManagementHandler... | 0.4890 | 97.7 |
| review-09 | ∅/∅ | 3 (current-flow) | 0 | 3 | Asked: 1万件を1件ずつ更新する for ループの代替一括手段。Expected core: UniversalDao.batchUpdate、ラウ... | 0.3594 | 66.4 |
| review-10 | ∅/∅ | 7 (current-flow) | 0 | 3 | Asked: バージョンアップで壊れにくいコードにするチェック方法。Expected core: @Published公開APIのみ使う方針＋非公開API... | 0.3550 | 75.9 |
| impact-01 | ∅/∅ | 8 (current-flow) | 0 | 3 | Asked: Nablarchバッチのトランザクション境界の決定主体と仕組み。Expected core: LoopHandler+commitInter... | 0.4674 | 94.9 |
| impact-02 | ∅/∅ | 5 (current-flow) | 0 | 3 | Asked: WebアプリでCSRF対策に何を追加し、セッション・JSPカスタムタグとの相性は。Expected core: CsrfTokenVerif... | 0.3721 | 74.2 |
| impact-03 | ∅/∅ | 6 (current-flow) | 0 | 3 | Asked: マルチスレッド常駐バッチのDB接続管理と例外時の他スレッド挙動。Expected core: ①MultiThreadExecutionHa... | 0.5611 | 104.8 |
| impact-04 | ∅/∅ | 7 (current-flow) | 0 | 3 | Asked: DB一時障害の自動リトライ仕組みと注意点。Expected core: RetryHandler存在・Retryableインタフェース・適用... | 0.5383 | 108.8 |
| impact-05 | ∅/∅ | 9 (current-flow) | 0 | 3 | Asked: HIDDENフィールドで画面遷移入力を保持する方法と複数台構成のハマりどころ。Expected core: HIDDENストア機能、AES暗... | 0.5085 | 106.7 |
| impact-06 | ∅/∅ | 6 (current-flow) | 0 | 3 | Asked: CSP有効化でonclick属性が動かなくなった場合JSP修正は必要か。Expected core: SecureHandlerのgener... | 0.3822 | 76.8 |
| impact-07 | ∅/∅ | 7 (current-flow) | 0 | 3 | Asked: 内部フォワード先を含む画面アクセス認可。Expected core: PermissionCheckHandler + setUsesInt... | 0.4645 | 91.3 |
| impact-08 | ∅/∅ | 3 (current-flow) | 0 | 3 | Asked: Bean ValidationでDB重複チェックを実装してよいか（セキュリティ的に）。Expected core: BV内DBアクセスは未検... | 0.3927 | 77.3 |
| impact-09 | ∅/∅ | 3 (current-flow) | 0 | 3 | Asked: マスタ管理とバリデーションの連携方法。Expected core: コード管理機能（nablarch-common-code）＋@CodeV... | 0.3697 | 70.7 |
| impact-10 | ∅/∅ | 5 (current-flow) | 0 | 3 | Asked: 画面遷移中のユーザー情報保持と認可チェックの推奨場所。Expected core: セッションストア(DBストア推奨)で永続保持＋Threa... | 0.4138 | 81.0 |
| req-01 | ∅/∅ | 8 (current-flow) | 0 | 3 | Asked: Nablarchにビルトインのログイン機能はあるか。Expected core: ビルトイン無し・業務サンプル`nablarch-passw... | 0.4368 | 87.8 |
| req-02 | ∅/∅ | 10 (current-flow) | 0 | 3 | Asked: Nablarchに権限チェックの仕組みはあるか。Expected core: role_check（@CheckRole）とpermissi... | 0.5351 | 102.9 |
| req-03 | ∅/∅ | 5 (current-flow) | 0 | 3 | Asked: 複数人同時編集の後勝ち問題防止の仕組みの有無。Expected core: @Versionアノテーション・UniversalDao.upd... | 0.3538 | 71.1 |
| req-04 | ∅/∅ | 6 (current-flow) | 0 | 3 | Asked: Nablarchに二重サブミット防止の仕組みがあるか。Expected core: @OnDoubleSubmission+useToken... | 0.3982 | 78.0 |
| req-05 | ∅/∅ | 7 (current-flow) | 0 | 3 | Asked: Nablarchで画面の多言語対応（メッセージ・ラベル）ができるか。Expected core: PropertiesStringResou... | 0.5534 | 93.0 |
| req-06 | ∅/∅ | 7 (current-flow) | 0 | 3 | Asked: スケールアウト時の注意点（特にセッション）。Expected core: ステートレス化推奨、HTTPセッション依存機能の代替一覧、セッショ... | 0.4004 | 90.4 |
| req-07 | ∅/∅ | 4 (current-flow) | 0 | 3 | CORSの仕組みが存在するか問う質問。Expected core: CorsPreflightRequestHandler/CorsResponseFin... | 0.3308 | 60.0 |
| req-08 | ∅/∅ | 4 (current-flow) | 0 | 3 | Asked: アップロードサイズ上限の仕組みがあるか。Expected core: MultipartHandlerのcontentLengthLimit... | 0.3913 | 71.1 |
| req-09 | ∅/∅ | 6 (current-flow) | 0 | 3 | Asked: NablarchにRESTレート制限の標準機能があるか。Expected core: 標準機能の有無＋最も近い代替機能の名称と限界＋推奨対処... | 0.5903 | 123.4 |
| req-10 | ∅/∅ | 3 (current-flow) | 0 | 3 | 「監査ログのビルトイン有無」を質問。期待コア: http_access_log_handler/jaxrs_access_log_handlerが証跡ログ... | 0.3743 | 77.3 |
