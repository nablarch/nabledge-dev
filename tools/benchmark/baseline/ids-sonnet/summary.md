# Stage 3 — 30 scenarios

- mean judge level:       2.90
- judge distribution:     {'0': 1, '1': 0, '2': 0, '3': 29}
- mean candidate count:   4.9
- mean cost (USD):        0.5106
- mean wall (s):          62.7

| id | facets | filter | picks | judge | reason | cost | wall |
|----|--------|--------|-------|-------|--------|------|------|
| review-01 | ∅/∅ | 8 (ids-direct) | 8 | 3 | Asked: ファイル取り込み夜間バッチの推奨構成。Expected core: フレームワーク選択（Nablarchバッチ）、都度起動バッチの選択理由、... | 0.6023 | 94.2 |
| review-02 | ∅/∅ | 5 (ids-direct) | 5 | 3 | Asked: Nablarchウェブアプリの基本処理構成の推奨方法。Expected core: 必須コンポーネント2つ(NablarchServletC... | 0.5068 | 67.4 |
| review-03 | ∅/∅ | 6 (ids-direct) | 6 | 3 | Asked: REST APIの推奨構成パターン。Expected core: restful_web_service選択理由、ハンドラキュー処理フロー、... | 0.5678 | 60.7 |
| review-04 | ∅/∅ | 7 (ids-direct) | 7 | 3 | 必須・桁数・形式チェックの書き方を質問。期待コア: Bean Validation推奨、@Required/@Length/@SystemCharアノテー... | 0.5710 | 72.9 |
| review-05 | ∅/∅ | 5 (ids-direct) | 5 | 3 | Asked: REST APIでJSON入力検証とエラー返却の推奨方法。Expected core: `@Valid`でBean Validation、`... | 0.5277 | 62.5 |
| review-06 | ∅/∅ | 3 (ids-direct) | 3 | 3 | 外部サイトからの不正POST防止方法を聞いている。期待コア: CsrfTokenVerificationHandlerの存在・ハンドラキュー設定・ハンドラ... | 0.4894 | 59.0 |
| review-07 | ∅/∅ | 6 (ids-direct) | 6 | 3 | Asked: NablarchウェブでCSPを有効にする標準方法。Expected core: SecureHandler + ContentSecuri... | 0.7009 | 60.3 |
| review-08 | ∅/∅ | 9 (ids-direct) | 9 | 3 | Asked: 常駐バッチ並列化でのDB接続・排他の注意点。Expected core: スレッド別コネクション確保、ハンドラ配置順、スレッドセーフ要件、悲... | 0.5249 | 83.2 |
| review-09 | ∅/∅ | 1 (ids-direct) | 1 | 3 | Asked: Nablarchに一括更新の仕組みはあるか。Expected core: Universal DAOのbatchUpdate、パフォーマンス... | 0.4616 | 47.8 |
| review-10 | ∅/∅ | 6 (ids-direct) | 6 | 3 | Asked: 非公開APIを使っていないかチェックする方法。Expected core: Publishedアノテーションの仕組み＋2種のツール（nabl... | 0.4945 | 60.1 |
| impact-01 | ∅/∅ | 5 (ids-direct) | 5 | 3 | Asked: バッチのトランザクション境界とコミットタイミングの決まり方。Expected core: LoopHandlerのcommitInterva... | 0.4901 | 61.9 |
| impact-02 | ∅/∅ | 5 (ids-direct) | 5 | 3 | Asked: WebアプリでCSRF対策に何を追加し、セッション・カスタムタグとの相性で何に注意すべきか。Expected core: CsrfToken... | 0.5066 | 70.9 |
| impact-03 | ∅/∅ | 4 (ids-direct) | 4 | 3 | Asked: 並列バッチのDB接続管理と例外時の挙動。Expected core: MultiThreadExecutionHandler、サブスレッドに... | 0.4892 | 60.1 |
| impact-04 | ∅/∅ | 2 (ids-direct) | 2 | 3 | Asked: 一時的なDB断でのリトライ機構と注意点。Expected core: RetryHandlerの存在、上限設定（回数/時間）、ハンドラ順序の... | 0.5689 | 51.5 |
| impact-05 | ∅/∅ | 7 (ids-direct) | 7 | 3 | Asked: HIDDENストアの使い方とAPサーバ複数台でのハマりどころ。Expected core: HiddenStore／<n:hiddenSto... | 0.5004 | 68.9 |
| impact-06 | ∅/∅ | 5 (ids-direct) | 5 | 3 | Asked: CSP有効化でonclick=が動かなくなった場合JSP書き換えは必要か。Expected core: nonce設定方法、カスタムタグの自... | 0.4956 | 68.0 |
| impact-07 | ∅/∅ | 6 (ids-direct) | 6 | 3 | Asked: 内部フォワード先のアクションも認可対象にできるか。Expected core: PermissionCheckHandler + setUs... | 0.4885 | 65.7 |
| impact-08 | ∅/∅ | 4 (ids-direct) | 4 | 3 | Asked: Bean ValidationでDBメールアドレス重複チェックを行うのはセキュリティ上問題か。Expected core: 未検証値がDBク... | 0.5076 | 64.3 |
| impact-09 | ∅/∅ | 4 (ids-direct) | 4 | 3 | Asked: マスタ管理の仕組みと入力チェックを連携できるか。Expected core: BasicCodeManager登録＋@CodeValueアノ... | 0.5005 | 66.0 |
| impact-10 | ∅/∅ | 7 (ids-direct) | 7 | 3 | Asked: 画面遷移中のユーザー情報保持と認可参照の推奨場所。Expected core: セッションストア(DBストア推奨)、SessionUtil.... | 0.5180 | 71.3 |
| req-01 | ∅/∅ | 6 (ids-direct) | 6 | 3 | Asked: Nablarchにビルトインのログイン認証機能があるか。Expected core: ビルトイン機能なし＋代替手段（ビジネスサンプル/Sys... | 0.5010 | 62.9 |
| req-02 | ∅/∅ | 7 (ids-direct) | 7 | 3 | Asked: Nablarchの権限チェック機能の有無と使い方。Expected core: permission_check/role_checkの存在... | 0.5075 | 65.1 |
| req-03 | ∅/∅ | 4 (ids-direct) | 4 | 3 | Asked: 後勝ち上書き防止の仕組みの有無と方法。Expected core: UniversalDao + `@Version` による楽観的ロック、... | 0.4953 | 63.6 |
| req-04 | ∅/∅ | 4 (ids-direct) | 4 | 3 | Asked: 二重サブミット防止機能があるか。Expected core: @OnDoubleSubmissionアノテーション、path属性での遷移先指... | 0.4834 | 55.8 |
| req-05 | ∅/∅ | 4 (ids-direct) | 4 | 3 | Asked: NablarchでJP/EN多言語切り替えができるか。Expected core: PropertiesStringResourceLoad... | 0.4869 | 56.2 |
| req-06 | ∅/∅ | 7 (ids-direct) | 7 | 3 | Asked: スケールアウト時のセッション管理と注意点。Expected core: HTTPセッション依存機能の特定とステートレス化手順（DBストア・d... | 0.4933 | 57.3 |
| req-07 | ∅/∅ | 2 (ids-direct) | 2 | 3 | Asked: Nablarch に CORS 対応の仕組みはあるか。Expected core: CorsPreflightRequestHandler ... | 0.4764 | 47.8 |
| req-08 | ∅/∅ | 3 (ids-direct) | 3 | 3 | アップロードサイズ上限機能の有無を質問。Expected core: MultipartHandler/UploadSettings/contentLen... | 0.4769 | 46.6 |
| req-09 | ∅/∅ | 0 (ids-direct) | 0 | 0 | Asked: NablarchにREST APIのレート制限機能があるか。Expected core: 標準機能の有無の明示＋最も近い代替機構（ハンドラ等... | 0.3577 | 34.5 |
| req-10 | ∅/∅ | 5 (ids-direct) | 5 | 3 | Asked: 監査ログのビルトイン有無と仕組み。Expected core: 専用機能なし＋代替としてHTTPアクセスログハンドラ（$userId$/$s... | 0.5269 | 74.9 |
