# Judge v2 Re-scoring

- scenarios scored: 30
- mean level: 1.53
- distribution: {'0': 1, '1': 16, '2': 9, '3': 4}
- total cost (USD): 5.8044

| id | level | over_reach | facts covered / total | reasoning (excerpt) |
|----|-------|------------|-----------------------|---------------------|
| review-01 | 2 | 1 | 13/15 | 必須ファクトの大部分は COVERED。PARTIAL が2件ある。①常駐バッチの代替として db_messaging が推奨されるという点は「新規開発では使用しないこと」とのみ述べられ、db_... |
| review-02 | 3 | 1 | 11/12 | 必須ファクトはほぼ全て COVERED。2コンポーネント（NablarchServletContextListener / WebFrontController）の役割・処理の流れ7ステップ・最... |
| review-03 | 2 | 0 | 11/12 | 12/13の必須ファクトがCOVERED。欠落しているのはメディアタイプ拡張が必要な場合のRoutesMapping/JaxRsMethodBinderFactory設定という条件付き・発展的な... |
| review-04 | 1 | 2 | 9/12 | 生成回答はBean Validation推奨・推奨理由・BeanValidationStrategy登録・アノテーション使用方法・String型定義・ドメインバリデーション推奨・実行順序未保証の... |
| review-05 | 1 | 1 | 6/8 | 主要な事実（Bean Validation推奨、@Validアノテーション、ErrorResponseBuilder継承によるエラーボディ生成、JaxRsResponseHandlerへの設定）... |
| review-06 | 1 | 1 | 12/14 | 生成回答はCsrfTokenVerificationHandlerの基本動作・ハンドラ配置順・デフォルト動作・設定例・RESTful対応を正確にカバーしており、主要部分の品質は高い。しかし2点の... |
| review-07 | 2 | 2 | 6/10 | コアとなる必須ファクト（generateCspNonce=true、ContentSecurityPolicyHeaderの追加、$cspNonceSource$プレースホルダー、カスタムタグへ... |
| review-08 | 1 | 5 | 10/14 | 参照回答のコアである「DB接続の配置位置」「コネクション数の計算」「スレッドセーフ要件」はカバーされているが、以下の MISSING が存在する: (1) `concurrentNumber` ... |
| review-09 | 3 | 0 | 5/5 | 生成回答はリファレンス回答の全必須事実を正確にカバーしている。①batchInsert/batchUpdate/batchDeleteの3メソッド提供、②ラウンドトリップ削減によるパフォーマンス... |
| review-10 | 2 | 4 | 7/11 | 生成回答は中核となる情報（@Published アノテーションによる公開/非公開 API の区別、2 つのチェックツールの詳細）を正確にカバーしており、実用的な回答になっている。一方で参照回答に... |
| impact-01 | 1 | 2 | 5/9 | 生成回答の核心的な主張「バッチのトランザクション境界は主にLoopHandlerが決定する」は、リファレンス回答の核心的な事実「TransactionManagementHandlerがトランザ... |
| impact-02 | 1 | 1 | 7/11 | 生成回答は CsrfTokenVerificationHandler の追加・順序・デフォルト動作（UUIDv4、HTTP メソッド判定、400 返却）に関するコア事実をすべてカバーしており、設... |
| impact-03 | 1 | 1 | 12/14 | 主要なファクトの大部分はカバーされているが、2つのMISSINGファクトがある。①「親スレッドでDBアクセスが必要な場合は本ハンドラより前にDatabaseConnectionManagemen... |
| impact-04 | 3 | 0 | 11/11 | 生成された回答はリファレンス回答が要求する全ての事実を網羅している。RetryHandlerの存在、retryContextFactory/CountingRetryContextFactory... |
| impact-05 | 1 | 1 | 8/11 | 生成回答はメインの問い（HiddenStoreの使い方・複数APサーバでの暗号化キー問題と対策）を正確かつ詳細に回答しており、AES暗号化・encryptorプロパティ設定・鍵生成方法など主要フ... |
| impact-06 | 2 | 1 | 8/9 | 主要な必須ファクトはほぼすべてカバーされている。「カスタムタグ使用時はJSP書き換え不要、手書きonclickは対応が必要」というコアの結論、SecureHandlerの設定方法、tag-for... |
| impact-07 | 1 | 1 | 8/13 | 主要な回答（PermissionCheckHandler の使用、setUsesInternalRequestId=true によるフォワード先認可、デフォルト false、権限なし時の 403... |
| impact-08 | 1 | 2 | 3/5 | 主要な3つの事実（Bean ValidationでのDBアクセスはセキュリティ上問題がある、未バリデーション値によるSQLインジェクションリスク、ビジネスアクション側で実施すべき）はすべてCOV... |
| impact-09 | 1 | 6 | 6/8 | 必須ファクトのうち「BeanクラスのプロパティはすべてStringとして定義すること」（s5由来の注意点）がMISSING。また「Nablarch Validationはsetterにアノテーシ... |
| impact-10 | 1 | 3 | 4/11 | 生成回答はDBストアへの保存という中核的な推奨先をCOVERしており、SessionUtil.changeId/putのコード例も正確。ただし以下の重大な問題がある。①参照答えが中心的に述べる「... |
| req-01 | 2 | 4 | 9/9 | 必須ファクト（ビルトイン認証なし・PJ実装必須・DBストアによるセッション保持・SessionUtil.changeId / CsrfTokenUtil.regenerateCsrfToken ... |
| req-02 | 1 | 4 | 6/11 | コアファクト（Nablarchにビルトイン認可機能あり、2種類の認可ライブラリの使い分け、PermissionCheckHandlerの権限あり/なし時の動作）は概ねCOVEREDまたはPART... |
| req-03 | 2 | 1 | 14/14 | 全14の必須ファクトがCOVERED。参照ソースに含まれないlibraries-exclusive_control.json:s3の情報（HttpExclusiveControlUtil#che... |
| req-04 | 1 | 3 | 6/8 | 参照回答の核心要素である「JSP の form タグ useToken 属性によるトークン自動生成・hidden 埋め込み」の説明が PARTIAL（「JSP以外」という対比でのみ示唆され、us... |
| req-05 | 2 | 1 | 11/11 | 必須ファクトはすべて COVERED されている。`defaultLocale` 必須設定の警告、JSP タグライブラリの制限、レイアウト崩れ警告、2通りの言語切り替え方法など、リファレンスアン... |
| req-06 | 1 | 3 | 8/10 | 生成された回答は「HTTP セッションがステートフルであるためスケールアウトできない」「3つの一般的な対処法とその欠点」「Twelve-Factor App の廃棄容易性」「セッション依存の5機... |
| req-07 | 2 | 4 | 4/5 | 必須ファクトはすべて COVERED（完全修飾クラス名のみ PARTIAL）。CorsPreflightRequestHandler と CorsResponseFinisher による COR... |
| req-08 | 3 | 0 | 12/12 | 生成された回答はリファレンス回答のすべての必須事実を完全にカバーしている。contentLengthLimitによるサイズ上限設定、413レスポンス、省略時無制限、DoS攻撃防止のための必須設定... |
| req-09 | 0 | 0 | 0/5 | 生成された回答は「（参照可能なセクションがありません。）」のみであり、実質的に非回答である。必須ファクト（Nablarchにビルトインのレート制限機能が存在しないこと、カスタムハンドラによる対応... |
| req-10 | 1 | 4 | 6/10 | 主要な事実（専用機能なし、最も近い機能はHttpAccessLogHandler、リクエスト開始/完了時ログ、ユーザID含む、業務操作はプロジェクト実装）はCOVERED。しかし①クラス名（na... |
