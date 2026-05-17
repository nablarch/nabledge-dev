# ベンチマーク結果: baseline-current (2026-05-15)

## 品質サマリー（3 run集計）

| 軸 | 対象件数 | 確定件数 | 未確定 | 平均±SD | 中央値 | 最低 | 全PASS率 |
|---|---|---|---|---|---|---|---|
| 回答精度 | 28 | 24 | 4 | 0.917 ± 0.282 | 1.000 | 0.000 | 22/24 |
| ハルシネーション | 28 | 23 | 5 | 0.130 ± 0.219 | 0.000 | 0.000 | 0/23 |

※ 未確定 = 3 run中いずれかにUNCERTAINを含むシナリオ。平均・PASS率は確定分のみで計算。
※ SDは3 run間のスコアのばらつき（大きいほど結果が不安定）。

## パフォーマンスサマリー（3 run集計、外れ値除外後）

| メトリクス | 平均±SD | 中央値 | P95 | 最大 | 外れ値除外件数 |
|---|---|---|---|---|---|
| 実行時間（総合） | 141.8s ± 57.9s | 130.9s | 254.3s | 290.3s | 0 |
| 実行時間（API） | 140.9s ± 57.5s | 129.3s | 252.3s | 289.6s | 0 |
| 入力トークン | 716,206 ± 261,663 | 659,652 | 1,226,075 | 1,549,619 | 0 |
| 出力トークン | 8,110 ± 3,278 | 7,654 | 14,942 | 17,259 | 0 |
| コスト（1シナリオ） | $0.6186 ± $0.1776 | $0.6068 | $0.9213 | $1.0736 | 0 |
| ターン数 | 7.9 ± 4.6 | 7.0 | 15.8 | 32 | 0 |

## 外れ値リスト

| シナリオID | run | duration_ms | 備考 |
|---|---|---|---|
| （なし） | - | - | - |

## シナリオ別詳細分析

| シナリオID | 品質(精度/幻覚) | ターン数 | 検索件数 | ヒアリング | 想定との差異 |
|---|---|---|---|---|---|
| impact-01 | 1.00 / 未確定 | 5.3 | 2.3 | skipped | ハルシネーション検出 |
| impact-03 | 1.00 / 未確定 | 9.3 | 3.3 | skipped | 幻覚UNCERTAIN含む |
| impact-06 | 1.00 / FAIL | 9.3 | 7.3 | skipped | ハルシネーション検出 |
| impact-08 | 1.00 / FAIL | 6.7 | 5.3 | skipped | ハルシネーション検出 |
| pre-01 | 1.00 / FAIL | 9.0 | 5.0 | skipped | ハルシネーション検出 |
| pre-02 | 1.00 / 未確定 | 11.3 | 9.0 | skipped | 幻覚UNCERTAIN含む |
| pre-03 | 1.00 / 未確定 | 7.3 | 6.3 | skipped | 幻覚UNCERTAIN含む |
| qa-01 | 1.00 / FAIL | 9.3 | 2.7 | skipped | ハルシネーション検出 |
| qa-02 | 0.00 / FAIL | 14.3 | 8.7 | skipped | 精度0.00: ABSENTあり、ハルシネーション検出 |
| qa-03 | 1.00 / 未確定 | 5.3 | 3.0 | skipped | ハルシネーション検出 |
| qa-04 | 1.00 / FAIL | 9.7 | 9.7 | skipped | ハルシネーション検出 |
| qa-05 | 1.00 / 未確定 | 10.3 | 3.7 | skipped | ハルシネーション検出 |
| qa-06 | 1.00 / 未確定 | 9.3 | 4.3 | skipped | ハルシネーション検出 |
| qa-07 | 1.00 / FAIL | 8.3 | 6.0 | skipped | ハルシネーション検出 |
| qa-08 | 1.00 / 未確定 | 6.0 | 3.7 | skipped | 幻覚UNCERTAIN含む |
| qa-09 | 1.00 / 未確定 | 8.3 | 6.0 | skipped | 幻覚UNCERTAIN含む |
| qa-10 | 1.00 / 未確定 | 8.7 | 3.0 | skipped | ハルシネーション検出 |
| qa-11a | 1.00 / FAIL | 12.3 | 8.3 | skipped | ハルシネーション検出 |
| qa-11b | 0.00 / FAIL | 5.3 | 11.0 | skipped | 精度0.00: ABSENTあり、ハルシネーション検出 |
| qa-12a | 未確定 / FAIL | 6.7 | 9.7 | skipped | ハルシネーション検出、精度UNCERTAIN含む |
| qa-12b | 未確定 / FAIL | 6.3 | 8.7 | skipped | ハルシネーション検出、精度UNCERTAIN含む |
| qa-13 | 未確定 / FAIL | 6.0 | 6.0 | skipped | ハルシネーション検出、精度UNCERTAIN含む |
| qa-14 | 未確定 / 未確定 | 6.0 | 14.0 | skipped | ハルシネーション検出、精度UNCERTAIN含む |
| qa-15 | 1.00 / FAIL | 4.0 | 7.0 | skipped | ハルシネーション検出 |
| review-06 | 1.00 / FAIL | 5.0 | 6.7 | skipped | ハルシネーション検出 |
| review-07 | 1.00 / 未確定 | 5.3 | 4.7 | skipped | ハルシネーション検出 |
| review-08 | 1.00 / FAIL | 6.3 | 5.7 | skipped | ハルシネーション検出 |
| review-09 | 1.00 / FAIL | 10.0 | 6.0 | skipped | ハルシネーション検出 |

## 人間レビュー対象

### impact-01
  - [run-3] ハルシネーションFAIL: 方法2のUniversalDao.Transaction使用例において、「生成すると別のトランザクションで実行される」という説明とともにnew FindPers

### impact-03
  - [run-1] ハルシネーションUNCERTAIN
  - [run-3] ハルシネーションFAIL: ValidationUtil#createMessageForProperty および ApplicationException というNablarch固有のA

### impact-06
  - [run-1] ハルシネーションFAIL: Redisストアに関するNablarch固有の設定情報（nablarch.lettuce.clientType プロパティ値、設定ファイル名 redisstor
  - [run-2] ハルシネーションFAIL: 複数のNablarch固有の主張が知識セクションに裏付けられない。具体的には、①Redisストアの「テーブル作成・有効期限バッチが不要」という特徴、②本番環境で
  - [run-3] ハルシネーションFAIL: 複数のNablarch固有の仕様が知識セクションに裏付けられていない。具体的には、(1) DBストアが使用するテーブル名「USER_SESSION」の明示、(2

### impact-08
  - [run-1] ハルシネーションFAIL: 知識セクションでは「SystemTimeProviderを実装したクラスを作成する」という手順が示されており、FixedSystemTimeProviderとい
  - [run-2] ハルシネーションFAIL: 知識セクションには「SystemTimeProviderを実装したクラスを作成する」と記載されており、既存の`FixedSystemTimeProvider`ク
  - [run-3] ハルシネーションFAIL: 知識セクションでは「SystemTimeProviderを実装したクラスを作成する」と明記されており、FixedSystemTimeProviderという既製ク

### pre-01
  - [run-1] ハルシネーションFAIL: 起動時の引数 `-diConfig`（DIコンテナ設定ファイルの指定）および `-userId`（実行ユーザID）はNablarch固有の主張であるが、知識セク
  - [run-2] ハルシネーションFAIL: `-diConfig` および `-userId` オプションの存在・必須性、セッションコンテキスト変数 `user.id` への格納、欠落時の終了コード127
  - [run-3] ハルシネーションFAIL: 複数のNablarch固有の主張が知識セクションに裏付けられていない。具体的には、(1)終了コード127という具体的な値は知識セクションに記載なし、(2)`-u

### pre-02
  - [run-2] ハルシネーションFAIL: 知識セクションで裏付けられない主張が複数含まれる。具体的には、DomainManagerインターフェースの実装パターンおよびコンポーネント登録方法、@Domai
  - [run-3] ハルシネーションUNCERTAIN

### pre-03
  - [run-1] ハルシネーションUNCERTAIN
  - [run-2] ハルシネーションUNCERTAIN
  - [run-3] ハルシネーションFAIL: 知識セクションで裏付けられる主張（主キー検索、SQLファイルによる検索、Beanマッピング）は正確だが、複数のNablarch固有のAPI・仕様に関する主張が知

### qa-01
  - [run-1] ハルシネーションFAIL: UniversalDAO の遅延ロードに関する主要な説明（defer()、DeferredEntityList、サーバサイドカーソル、フェッチサイズ、トランザク
  - [run-2] ハルシネーションFAIL: 回答中のNablarch固有の説明（defer()メソッド、DeferredEntityList、サーバサイドカーソル、フェッチサイズ、トランザクション制御時の
  - [run-3] ハルシネーションFAIL: ページング回避策として言及された UniversalDao#per() および UniversalDao#page() という具体的なメソッド名は知識セクション

### qa-02
  - [run-1] 精度ABSENT: DatabaseRecordReaderでデータベースからデータを読み込む
  - [run-1] 精度ABSENT: BatchActionを継承したアクションクラスを実装する
  - [run-1] ハルシネーションFAIL: 知識セクションに裏付けのないNablarch固有の主張が複数含まれている。具体的には、起動クラス名 nablarch.fw.launcher.Main および起
  - [run-2] 精度ABSENT: DatabaseRecordReaderでデータベースからデータを読み込む
  - [run-2] 精度ABSENT: BatchActionを継承したアクションクラスを実装する
  - [run-2] ハルシネーションFAIL: 知識セクションではNablarchのDBデータリーダとして明示されているのはDatabaseRecordReaderであり、回答が主張するBaseDatabas
  - [run-3] 精度ABSENT: DatabaseRecordReaderでデータベースからデータを読み込む
  - [run-3] 精度ABSENT: BatchActionを継承したアクションクラスを実装する
  - [run-3] ハルシネーションFAIL: 知識セクションが示すNablarch標準バッチフレームワークは、DatabaseRecordReader・BatchAction・ハンドラキュー構成（トランザク

### qa-03
  - [run-1] ハルシネーションFAIL: 知識セクションにはJakarta Bean Validationを使用した@AssertTrueによる相関バリデーションの実装方法のみが記載されている。回答には
  - [run-3] ハルシネーションFAIL: Bean Validationを使った相関バリデーション（@AssertTrue、実行順序の非保証、nullチェック）に関する記述は知識セクションで裏付けられる

### qa-04
  - [run-1] ハルシネーションFAIL: テストメソッド名（testValidateCharsetAndLength・testSingleValidation・testBeanValidation・te
  - [run-2] ハルシネーションFAIL: EntityTestSupportの継承、パッケージ・クラス名規則、Excelファイルの配置ルール、charsetAndLengthシートの主要カラム定義など基
  - [run-3] ハルシネーションFAIL: 複数の裏付けのない主張が含まれるためFAIL。特に、(1) testValidateCharsetAndLength / testSingleValidatio

### qa-05
  - [run-1] ハルシネーションFAIL: コード実装・アノテーション・APIに関する主要な主張は知識セクションで裏付けられているが、「注意点」セクションに3件の裏付けなし主張が含まれる。①PathOpt
  - [run-3] ハルシネーションFAIL: 主要な実装パターン（アノテーション構成、BeanUtil、UniversalDao.insert()、フォームのString型、メソッド引数バリエーション）は知

### qa-06
  - [run-1] ハルシネーションFAIL: 大部分の主張は知識セクションで裏付けられているが、「共通化した場合、確認画面ではuseToken属性のデフォルトがtrueになるため、二重サブミット防止の設定は
  - [run-3] ハルシネーションFAIL: ほとんどの主張は知識セクションで裏付けられているが、「SessionUtilを使ってセッションストアに保存する」および「フォームではなくエンティティに変換してか

### qa-07
  - [run-1] ハルシネーションFAIL: 複数のNablarch固有の主張が知識セクションに裏付けられていない。Csv.CsvTypeのRFC4180・EXCEL・TSVという選択肢、Csv.CsvTy
  - [run-2] ハルシネーションFAIL: 複数のNablarch固有APIが知識セクションに裏付けられていない。具体的には、(1) ObjectMapperIteratorクラスの存在・用途は知識セクシ
  - [run-3] ハルシネーションFAIL: 複数のNablarch固有API・仕様の主張が知識セクションに裏付けられない。①フォーマットセットとして「RFC4180・EXCEL・TSV」が選択可能という記

### qa-08
  - [run-1] ハルシネーションFAIL: PropertiesStringResourceLoader の設定方法・defaultLocale の挙動・プロパティファイルの命名規則・UTF-8対応などの
  - [run-2] ハルシネーションFAIL: Section1（メッセージの多言語化）の記述は知識セクションで概ね裏付けられる。ただしSection2（コード名称の多言語化）のCodeUtil.getNam
  - [run-3] ハルシネーションUNCERTAIN

### qa-09
  - [run-1] ハルシネーションUNCERTAIN
  - [run-2] ハルシネーションFAIL: 主要な設定（BasicBusinessDateProvider、XML設定、テーブルレイアウト、BusinessDateUtil使用）は知識セクションで裏付けら
  - [run-3] ハルシネーションFAIL: SystemTimeUtil.getDate() というクラス・メソッド名、BusinessDateProvider#setDate(segment, newD

### qa-10
  - [run-3] ハルシネーションFAIL: 「ORDER BY句の動的切り替えには$sortを使う」という記述は知識セクションに一切記載がなく、裏付けのないNablarch固有の主張であるためハルシネーシ

### qa-11a
  - [run-1] ハルシネーションFAIL: GlobalErrorHandlerの動作仕様（ServiceError処理、InternalError変換、OOMの標準エラー出力）、FailureLogUt
  - [run-2] ハルシネーションFAIL: 最も重大な矛盾は HttpErrorHandler における ThreadDeath の扱いである。知識セクションでは『java.lang.ThreadDeat
  - [run-3] ハルシネーションFAIL: 複数の重大なハルシネーションが検出された。最も明確な矛盾は「Result.Error → FATAL」という主張で、知識セクションは「設定による（writeFa

### qa-11b
  - [run-1] 精度ABSENT: JaxRsResponseHandlerが例外に応じたエラーレスポンスを生成する
  - [run-1] 精度ABSENT: JaxRsErrorLogWriterが例外に応じたログ出力を行う
  - [run-1] ハルシネーションFAIL: 知識セクションはJaxRsResponseHandler・ErrorResponseBuilder・JaxRsErrorLogWriterに関する内容のみを扱っ
  - [run-2] 精度ABSENT: JaxRsResponseHandlerが例外に応じたエラーレスポンスを生成する
  - [run-2] 精度ABSENT: JaxRsErrorLogWriterが例外に応じたログ出力を行う
  - [run-2] ハルシネーションFAIL: 知識セクションはJAX-RS用のJaxRsResponseHandlerにおけるErrorResponseBuilderおよびJaxRsErrorLogWrit
  - [run-3] 精度ABSENT: JaxRsResponseHandlerが例外に応じたエラーレスポンスを生成する
  - [run-3] 精度ABSENT: JaxRsErrorLogWriterが例外に応じたログ出力を行う
  - [run-3] ハルシネーションFAIL: 知識セクションはJaxRsResponseHandlerのerrorResponseBuilderおよびerrorLogWriterに関する仕様を説明しているが

### qa-12a
  - [run-1] 精度UNCERTAIN: エラー表示タグでリクエストスコープのエラーメッセージを表示する
  - [run-1] ハルシネーションFAIL: 複数のハルシネーションが検出された。(1) 知識セクションではWebアプリケーションのエラー表示にJSPカスタムタグ(<n:errors>/<n:error>)
  - [run-2] 精度ABSENT: HttpErrorHandlerがApplicationExceptionのメッセージをErrorMessagesに変換しリクエストスコープに設定する
  - [run-2] 精度ABSENT: エラー表示タグでリクエストスコープのエラーメッセージを表示する
  - [run-2] ハルシネーションFAIL: 複数のNablarch固有APIおよび設定について知識セクションに裏付けがない。最も明確なハルシネーションは「ValidationUtil#createMess
  - [run-3] 精度ABSENT: エラー表示タグでリクエストスコープのエラーメッセージを表示する
  - [run-3] ハルシネーションFAIL: Thymeleafテンプレートに関する記述（errors.hasError()、errors.getMessage()、errors.allMessages）は

### qa-12b
  - [run-1] 精度UNCERTAIN: @Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる
  - [run-1] ハルシネーションFAIL: RESTfulウェブサービスに関する記述（@Valid、ErrorResponseBuilder継承パターン、メッセージ定義）は知識セクションで裏付けられる。一
  - [run-2] 精度ABSENT: @Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる
  - [run-2] 精度ABSENT: ErrorResponseBuilderの継承クラスでエラーメッセージをレスポンスボディに設定する
  - [run-2] ハルシネーションFAIL: 知識セクションはRESTfulウェブサービスにおけるErrorResponseBuilderを使ったエラーレスポンス構築を説明しているが、回答はWebアプリケー
  - [run-3] 精度UNCERTAIN: @Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる
  - [run-3] ハルシネーションFAIL: 「BeanValidationStrategyをvalidationStrategyという名前で定義する」という主張、および「ValidationUtil.cr

### qa-13
  - [run-1] 精度ABSENT: REST APIではFormクラスで値を受け付け、@Validでバリデーション後にUniversalDao.insertで登録する
  - [run-1] ハルシネーションFAIL: 知識セクションはRESTful Web Servicesパターン（@Valid/@Consumes/@Pathを使った直接insert）とWebアプリの確認画面
  - [run-2] 精度ABSENT: REST APIではFormクラスで値を受け付け、@Validでバリデーション後にUniversalDao.insertで登録する
  - [run-2] ハルシネーションFAIL: 複数のNablarch固有APIおよび仕様について知識セクションに裏付けのない主張が含まれる。特に @OnDoubleSubmission アノテーション、Se
  - [run-3] 精度UNCERTAIN: REST APIではFormクラスで値を受け付け、@Validでバリデーション後にUniversalDao.insertで登録する
  - [run-3] ハルシネーションFAIL: 知識セクションが示す実装パターンは JAX-RS スタイル（@Valid・@Consumes・メソッド引数でフォーム受取）であり、@InjectForm を使っ

### qa-14
  - [run-1] ハルシネーションFAIL: 知識セクションはJakarta EE 10対応・Java 17要件・javax→jakarta名前空間変更の必要性を大枠で裏付けているが、回答中のNablarc
  - [run-2] ハルシネーションFAIL: 知識セクションはJakarta EE 10対応・Java 17要件・アプリケーションサーバ要件・パッケージ名変更の必要性という高レベルの事実を裏付けており、一般
  - [run-3] 精度UNCERTAIN: Java EEの仕様名およびパッケージ名がJakarta EEのものに変更されている

### qa-15
  - [run-1] ハルシネーションFAIL: SecureHandlerに関する具体的なHTTPレスポンスヘッダの設定内容（X-XSS-Protection、X-Frame-Options、X-Conten
  - [run-2] ハルシネーションFAIL: 複数のNablarch固有の主張が知識セクションに裏付けられていない。特に①エスケープ変換の具体的な文字コード（&#034;, &#039;等）、②n:pret
  - [run-3] ハルシネーションFAIL: 知識セクションに裏付けのあるカスタムタグのサニタイジングおよびJSP静的解析ツールに関する記述は正確だが、SecureHandlerクラスの存在・具体的なセキュ

### review-06
  - [run-1] ハルシネーションFAIL: コアとなるAPI（getPathParam, getParamMap）やXMLルーティングの記法はゴールドスタンダードで裏付けられている。しかし、@Pathアノ
  - [run-2] ハルシネーションFAIL: XMLルート定義方式・JaxRsHttpRequest#getPathParam()・BeanUtil・ValidatorUtil等の記述は知識セクションにより
  - [run-3] ハルシネーションFAIL: XMLベースのルーティング・JaxRsHttpRequestによるパラメータ取得・@PathParam/@QueryParam使用不可の説明は知識セクションで裏

### review-07
  - [run-2] ハルシネーションFAIL: 2つの裏付けのないNablarch固有の主張が含まれる。(1) Mavenモジュール名 nablarch-fw-web は知識セクションに記載がなく検証不能。(
  - [run-3] ハルシネーションFAIL: 3つのハルシネーションが検出された。①検証失敗時のレスポンスを「400 BadResponse」と記述しているが、知識セクションでは「BadRequest(40

### review-08
  - [run-1] ハルシネーションFAIL: 3つの主張が知識セクションに裏付けられない。①HIDDENストアの暗号化キーに関する記述（APサーバごとに自動生成・冗長化環境での明示設定必要・サーバまたぎで復
  - [run-2] ハルシネーションFAIL: 3つのハルシネーションが検出された。①DBテーブル名を'USER_SESSION'と具体的に明示しているが、知識セクションには該当テーブル名の記載がなく裏付けが
  - [run-3] ハルシネーションFAIL: DBストアの保存先テーブル名として「USER_SESSION」と明記しているが、知識セクションには「データベース上のテーブル」とあるのみで具体的なテーブル名の記

### review-09
  - [run-1] ハルシネーションFAIL: 知識セクションはContentSecurityPolicyHeader・formタグ・scriptタグ・cspNonceタグのnonce対応を裏付けているが、g
  - [run-2] ハルシネーションFAIL: generateCspNonce プロパティ名、$cspNonceSource$ プレースホルダー、reportOnly プロパティ、および <n:cspNon
  - [run-3] ハルシネーションFAIL: 知識セクションはSecureHandlerによるnonce生成・ContentSecurityPolicyHeader・カスタムタグの動作変化について概念レベル
