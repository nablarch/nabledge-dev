# Judge v2 Re-scoring

- scenarios scored: 30
- mean level: 1.43
- distribution: {'0': 1, '1': 16, '2': 12, '3': 1}
- total cost (USD): 6.3796

| id | level | over_reach | facts covered / total | reasoning (excerpt) |
|----|-------|------------|-----------------------|---------------------|
| review-01 | 1 | 2 | 8/15 | 生成回答は都度起動バッチの選択、DB接続ありのハンドラキュー構成（主要ハンドラ名すべて列挙）、3層クラス設計、CSVデータリーダの実装（FilePathSetting/ObjectMapperI... |
| review-02 | 1 | 0 | 8/10 | 生成回答はコンポーネント構成（NablarchServletContextListener・WebFrontController）と最小ハンドラ構成13本（正しい順序）をほぼ完全にカバーしており... |
| review-03 | 2 | 1 | 8/11 | 必須ファクトはすべてCOVEREDまたはPARTIALであり、MISSINGやCONTRADICTEDはない。PARTIALの箇所は①WebFrontController/DispatchHan... |
| review-04 | 2 | 2 | 9/11 | 生成回答はBean Validationの推奨・BeanValidationStrategyの登録・String型プロパティ・アノテーション設定場所・ドメインバリデーション推奨・相関バリデーショ... |
| review-05 | 1 | 2 | 5/7 | 主要な必須ファクト（Bean Validation 推奨、JaxRsResponseHandler によるエラー応答生成、ErrorResponseBuilder 継承によるメッセージ返却）はほ... |
| review-06 | 2 | 2 | 13/14 | 生成回答は必須ファクトをほぼ網羅している。ハンドラ配置順序・デフォルト動作・XML設定例・RESTful利用の注意点など参照回答の主要項目はすべてCOVERED。唯一のPARTIALは「カスタマ... |
| review-07 | 2 | 1 | 8/10 | 生成回答はgenerateCspNonce=true設定、ContentSecurityPolicyHeader追加、$cspNonceSource$プレースホルダー、カスタムタグのnonce自... |
| review-08 | 1 | 5 | 4/12 | 生成回答は MultiThreadExecutionHandler の concurrentNumber 設定、スレッドセーフ要件、サブスレッド側への DB 接続・トランザクション管理ハンドラ配... |
| review-09 | 2 | 1 | 5/5 | 必須ファクト5件すべてCOVERED。batchInsert/batchUpdate/batchDeleteの提供、ラウンドトリップ削減によるパフォーマンス向上、batchUpdateの排他制御... |
| review-10 | 2 | 3 | 10/11 | 必須ファクトはほぼすべてCOVEREDされており、Nablarch 6変更の具体的な理由（Javadoc生成仕組みの変更）のみPARTIAL（補足情報として扱える程度）。ツールの詳細（nabla... |
| impact-01 | 0 | 4 | 0/8 | 生成回答の中心的主張は「Nablarchバッチのトランザクション境界は `LoopHandler`（commitInterval）と Jakarta EE リスナーが決定する」というものだが、参... |
| impact-02 | 1 | 1 | 8/11 | 生成回答はCsrfTokenVerificationHandlerの追加・セッションストア必須・session_store_handler後配置・nablarch_tag_handler後配置・... |
| impact-03 | 1 | 3 | 12/14 | 必須ファクトのうち「親スレッドでDB接続が必要な場合は MultiThreadExecutionHandler より前に DatabaseConnectionManagementHandler ... |
| impact-04 | 2 | 3 | 7/8 | 必須ファクト8件はすべてCOVEREDまたはPARTIAL（CONTRADICTEDなし）。PARTIALは「リトライ対象例外を送出するハンドラはRetryHandlerより後に配置」という一般... |
| impact-05 | 2 | 1 | 7/10 | 核心的な要求事実（HiddenStoreによるHIDDENフィールド保持、複数APサーバ構成でのデフォルトキー不一致問題、encryptorプロパティによる明示的キー設定、AESアルゴリズム、b... |
| impact-06 | 2 | 2 | 10/12 | 主要な必須ファクトはほぼすべてカバーされている。カスタムタグ使用時のJSP書き換え不要という核心、SecureHandler設定手順、tag-form_tagによる自動script要素化、手動対... |
| impact-07 | 1 | 3 | 9/12 | 内部フォワード先の認可チェックに必要なコア情報（PermissionCheckHandler、setUsesInternalRequestId=true、InternalRequestIdAtt... |
| impact-08 | 1 | 1 | 4/6 | 生成回答はコア部分（Bean ValidationでのDBアクセスがセキュリティ上問題であること、SQLインジェクションリスク、ビジネスアクション内での実装が正しい）を正確にカバーしており、その... |
| impact-09 | 1 | 4 | 6/8 | 必須ファクトのうち「Bean Validation のフォームプロパティはすべて String で定義する（Bean 変換失敗による予期せぬ例外を避けるため）」が MISSING。この注意点はリ... |
| impact-10 | 1 | 3 | 5/12 | 生成回答はDBストアへの保存（SessionUtil.put/changeId/invalidate、CsrfTokenUtil再生成）については概ねカバーしているが、以下の重大な欠落と逸脱があ... |
| req-01 | 1 | 5 | 9/9 | 必須事実はすべてCOVERED（認証ロジック非提供・DBストアによる認証情報保持・SessionUtil.changeId / CsrfTokenUtil.regenerateCsrfToken... |
| req-02 | 1 | 3 | 7/11 | 2種類の認可機能の概要（permission_check と role_check）とその使い分け、PermissionCheckHandler の基本動作（403送出、ThreadContex... |
| req-03 | 1 | 1 | 10/11 | 生成回答は楽観的ロックの実装詳細（@Version、OptimisticLockException、@OnError、数値型制約、batchUpdate制限、バージョンカラム設計指針）を網羅的か... |
| req-04 | 1 | 3 | 4/8 | 生成回答はJSPのuseToken属性と@OnDoubleSubmissionの組み合わせを正しく説明しているが、参照回答の重要な要素である「JSP以外のテンプレートエンジン向けの@UseTok... |
| req-05 | 2 | 2 | 10/10 | 必須ファクト10件はすべて COVERED。参照回答が示すメッセージ多言語化・コード名称多言語化・2通りの言語切り替え・レイアウト崩れ警告・defaultLocale 必須設定など、核心的な内容... |
| req-06 | 1 | 1 | 6/9 | 生成回答はスケールアウトの基本概念（HTTPセッションの問題、Twelve-Factor App、ステートレス化推奨）を正確にカバーしており、冗長でありながら実用的な情報を多く含む。しかし致命的... |
| req-07 | 3 | 0 | 5/5 | 必須ファクトはすべて COVERED。生成回答はリファレンスが引用した s1/s14 に加え、同一ナレッジファイルの s2〜s4 も参照し、BasicCors の設定方法・デフォルト動作・モジュ... |
| req-08 | 2 | 1 | 10/10 | 必須事実10件すべてがCOVERED。contentLengthLimitの説明、413レスポンス、無制限デフォルト、DoS防止推奨、リクエスト全体チェックの補足、アクション側実装の言及、max... |
| req-09 | 2 | 1 | 4/6 | 主要な必須事実はすべて COVERED または PARTIAL でカバーされている。「Nablarch にレート制限機能がない」「カスタムハンドラで対応する」「インフラレイヤでの対応も選択肢」と... |
| req-10 | 1 | 3 | 3/10 | 生成回答の中心的な主張「Nablarch には HTTPアクセスログ（証跡ログ兼用）という形で監査ログに相当するビルトイン機能がある」は、参照回答の中心的な結論「Nablarch は『操作監査ロ... |
