# ベンチマーク実行レポート

**実行日時**: 2026-05-20  
**実行ディレクトリ**: `tools/benchmark/results/20260520-072948`  
**スキル**: `.claude/skills/nabledge-6`  
**ステータス**: 実行中（逐次追記）

---

## シナリオ別レポート

### pre-01

**質問**: Nablarchバッチアプリケーションはどのように起動しますか？-requestPathの書き方を教えてください

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | FAIL（4件 unsupported） |
| sections | 6 |
| turns | 7 |
| duration | 147秒 |
| cost | $1.096 |
| hearing | skipped（`-requestPath` キーワードで `Nablarchバッチ` 自動判定） |

**幻覚FAIL — unsupported claims**:
1. `-diConfig`・`-requestPath`・`-userId` の3つが必須
2. いずれかが欠けると終了コード127で異常終了
3. `-diConfig` はシステムリポジトリの設定ファイルパスを指定
4. `-userId` はユーザIDを指定し `user.id` に格納

**裏取り結果**: `handlers-main.json:s3` に全件明記あり → **evaluate.py の false FAIL**

| claim | 知識ファイルの記述 |
|---|---|
| 3つのオプションが必須 | 「フレームワークの動作に必要となる以下の3つのオプションは、必ず指定する必要がある」 |
| 欠けると終了コード127 | 「いずれかが欠けていた場合は、即座に異常終了する。(終了コード = 127)」 |
| `-diConfig` の説明 | 「システムリポジトリの設定ファイルのパスを指定する」 |
| `-userId` の説明 | 「ユーザIDを設定する。この値はセッションコンテキスト変数に `user.id` という名前で格納される」 |

**LLMの動き**: Step 5で回答生成後「Step 6で検証します」と宣言しているが、verifyマーカーなし。trace.jsonのresultを見ると幻覚claimを含む回答がそのまま最終出力になっている。Step 6/7が実際に走ったかどうか確認不可（BENCHMARK_VERIFYマーカー削除済み）。

---

### pre-02

**質問**: 入力チェック（バリデーション）の実装方法を教えてください  
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: 入力画面のフォームでバリデーションする

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL（5件 unsupported） |
| sections | 7 |
| turns | 6 |
| duration | 64秒 |
| cost | $0.688 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. `@InjectForm` に `validate` パラメータを指定できる（例: `validate = "register"`）
2. `@OnError` アノテーションでバリデーションエラー時の遷移先を設定する
3. `@OnError` が未設定の場合、バリデーションエラーがシステムエラー扱いになる
4. `ctx.getRequestScopedVar("form")` でバリデーション済みフォームを取得する
5. データベースとの相関バリデーションはSQLインジェクション等のリスクを避けるため業務アクション側で実装すること

**裏取り結果**: 1〜4は `handlers-InjectForm.json:s3`・`s4` に明記あり → **evaluate.py の false FAIL**

| claim | 知識ファイルの記述 |
|---|---|
| `validate = "register"` | `s3` のコード例に `@InjectForm(... validate = "register")` が明記 |
| `@OnError` で遷移先設定 | `s4`「OnError アノテーションを使用して設定する」 |
| `@OnError` 未設定でシステムエラー | `s4`「OnError が設定されていない場合、バリデーションエラーがシステムエラー扱いとなるため注意すること」 |
| `ctx.getRequestScopedVar("form")` | `s3` のコード例に明記 |
| claim 5（相関バリデーション） | 未確認（知識ファイルに存在しない可能性あり） |

**LLMの動き**: trace.json の result に「Step 6: Verify — すべての主張はセクション内容に直接記載されており、PASS」と記述されている。つまり **LLM自身はPASS判定**したが、evaluate.py が FAIL と判定。LLMの判断は正しく、evaluate.py 側の誤判定が疑われる。

---

### pre-03

**質問**: UniversalDaoでデータベースのデータを検索するにはどうすればいいですか？  
**hearing_answer注入**: 処理方式: null（クロスファンクショナル）/ やりたいこと: マスタテーブルをUniversalDaoで検索する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL（2件 unsupported） |
| sections | 5 |
| turns | 4 |
| duration | 60秒 |
| cost | $0.490 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. SQLファイルのパスはBeanクラス（例: `sample.entity.User`）から `sample/entity/User.sql` として導出される
2. ユニバーサルDAOを使うにはコンポーネント定義に `BasicDaoContextFactory` の設定が必要

**裏取り結果**: 両件とも知識ファイルに明記あり → **evaluate.py の false FAIL**

| claim | 知識ファイルの記述 |
|---|---|
| SQLファイルパスの導出 | `s7`「SQLファイルのパスは、クラスパス配下のsample/entity/User.sqlとなる」と明記 |
| `BasicDaoContextFactory` の設定 | `s6`「BasicDaoContextFactory の設定をコンポーネント定義に追加する」と明記 |

**LLMの動き**: trace.jsonに「回答を生成します」のみで verify 言及なし（4ターンで完了）。LLMの回答内容は知識ファイルに忠実。evaluate.py の false FAIL。

---

### review-06

**質問**: REST APIでURLパスの一部を受け取ったり、検索条件をURL末尾のパラメータで渡す実装はどう書く？ルーティングの設定も含めて確認したい  
**hearing_answer注入**: 処理方式: RESTfulウェブサービス / やりたいこと: REST APIでパスパラメータとクエリパラメータを受け取りルーティングを設定する

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | FAIL（5件 unsupported） |
| sections | 10 |
| turns | 12 |
| duration | 118秒 |
| cost | $0.700 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. `@Path` アノテーション方式はバージョン1.2.0以降で利用可能
2. `@Path` アノテーション方式ではディスパッチハンドラを `PathOptionsProviderRoutesMapping` に変更する
3. `JaxRsPathOptionsProvider` および `JerseyJaxRsHandlerListFactory` を使用する
4. `@Path` アノテーション方式は JBoss や Wildfly など独自ファイルシステムを使うアプリケーションサーバでは使用できない
5. `RoutesMapping` コンポーネントを `webFrontController` の `handlerQueue` および `initializer` の `initializeList` に登録する設定

**裏取り結果**: 全件 `adapters-router-adaptor.json:s6`〜`s9` に明記あり → **evaluate.py の false FAIL**

| claim | 知識ファイルの記述 |
|---|---|
| バージョン1.2.0以降 | `s8`「本アダプタのバージョン1.2.0から、`@Path` アノテーションを使ったルーティングのマッピングができるようになった」 |
| `PathOptionsProviderRoutesMapping` | `s8`「`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定する必要がある」 |
| `JaxRsPathOptionsProvider`・`JerseyJaxRsHandlerListFactory` | `s8` のXML設定例に明記 |
| JBoss/Wildfly 制約 | `s8`「JbossやWildflyでは…`Path` アノテーションで注釈されたクラスの検索ができない」 |
| `handlerQueue`・`initializeList` への登録 | `s3`・`s4`・`s9` に設定例が明記 |

**LLMの動き**: 12ターンと多い。verify言及なし。複数セクションを読み込む検索を繰り返した結果のターン数増加と思われる。回答内容は知識ファイルに忠実。evaluate.py の false FAIL。

---

### review-07

**質問**: 外部サイトから不正にPOSTされるのを防ぎたい。NablarchにCSRF対策の仕組みはある？どう設定する？  
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: JSP画面でCSRF対策を実装する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | **PASS** |
| sections | 3 |
| turns | 9 |
| duration | 65秒 |
| cost | $0.541 |
| hearing | skipped |

**初の幻覚PASS。** 裏取り不要。

**LLMの動き**: verify言及なし。turns 9はsections 3に対してやや多いが正常完了。

---

### review-08

**質問**: 入力→確認→完了画面間でセッション変数を保持するとき、DBストアとHIDDENストアの使い分けはどうすればいい？  
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: 入力→確認→完了画面間でDBストアとHIDDENストアの使い分けを理解する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | **PASS** |
| sections | 4 |
| turns | 7 |
| duration | 55秒 |
| cost | $0.506 |
| hearing | skipped |

幻覚PASS。裏取り不要。

---

### review-09

**質問**: Content Security Policyを有効にしたい。NablarchのWeb画面でCSPを設定するにはどうすればいい？  
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: NablarchのWeb画面でContent Security Policyを設定する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL（7件 unsupported） |
| sections | 6 |
| turns | 11 |
| duration | 74秒 |
| cost | $0.588 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. `generateCspNonce` プロパティを `true` に設定するとnonceが生成される
2. `secureResponseHeaderList` プロパティにヘッダコンポーネントをリスト設定する
3. `ContentSecurityPolicyHeader` の `policy` プロパティにポリシー文字列を設定する
4. `$cspNonceSource$` プレースホルダーが実際のnonce値に置換される
5. `reportOnly` プロパティを `true` にすると `Content-Security-Policy-Report-Only` ヘッダとして出力される
6. `SecureHandler` は HTTPレスポンスハンドラよりも後ろに設定すること
7. `secureResponseHeaderList` 設定時はデフォルトコンポーネントも明示的に設定すること

**裏取り結果**: 1〜5は知識ファイルに明記あり → evaluate.py の false FAIL。6・7は取得セクションに該当記述なし → **真の幻覚の可能性あり**

| claim | 判定 | 根拠 |
|---|---|---|
| `generateCspNonce` で nonce 生成 | false FAIL | `s8` に明記 |
| `secureResponseHeaderList` にリスト設定 | false FAIL | `s7`・`s8`・`s9` のXML例に明記 |
| `policy` プロパティ設定 | false FAIL | `s7`・`s8` に明記 |
| `$cspNonceSource$` 置換 | false FAIL | `s8` に明記 |
| `reportOnly: true` で Report-Only ヘッダ | false FAIL | `s9` に明記 |
| SecureHandler をHTTPレスポンスハンドラより後ろに設定 | **要調査** | 取得セクションに記述なし |
| `secureResponseHeaderList` 設定時はデフォルトも明示 | **要調査** | 取得セクションに記述なし |

**LLMの動き**: verify言及なし。turns 11はやや多い。claim 6・7はLLMが知識ファイル外から補完した可能性あり。


### impact-01

**質問**: 業務トランザクションとは別のトランザクションでSQLを実行する方法はあるか？ロールバックされても別トランザクションの更新は残したい
**hearing_answer注入**: 処理方式: Nablarchバッチ / やりたいこと: 業務エラー時にエラーログをDBに書き込む

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL (4 unsupported) |
| sections | 6 |
| turns | 5 |
| duration | 197秒 |
| cost | $1.175 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. LoopHandler（トランザクションループ制御ハンドラ）は例外・エラー発生時にロールバック後、新しいトランザクションでtransactionAbnormalEndを呼び出す
2. TransactionEventCallbackインターフェースにtransactionNormalEndとtransactionAbnormalEndメソッドが存在し、後者はロールバック後に新しいトランザクションで実行される
3. HandlerとTransactionEventCallbackを同時に実装したハンドラクラスを作成してLoopHandlerの後続に配置することでエラーログDB書き込みに使用できる
4. 複数のハンドラがTransactionEventCallbackを実装している場合、コールバック中に例外が発生すると残りのハンドラのコールバックは実行されない

---

### impact-03

**質問**: Bean Validationの中でDBに問い合わせて重複チェックしたい。カスタムバリデータでDB検索する実装でいいのか？
**hearing_answer注入**: 処理方式: RESTfulウェブサービス / やりたいこと: 会員登録処理でDB重複チェックする

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | UNCERTAIN (3 unsupported) |
| sections | 3 |
| turns | 5 |
| duration | 60秒 |
| cost | $0.517 |
| hearing | skipped |

**幻覚UNCERTAIN — unsupported claims**:
1. ValidationUtil#createMessageForPropertyを使うことで特定のフィールドにエラーメッセージを紐づけてクライアントへ返すことができる
2. RESTfulウェブサービスでのBean Validationはリソースクラスのメソッド引数に@Validアノテーションを付与することで実行される
3. カスタムバリデータ内でのDBアクセスをNablarchとして明示的に禁止している

---

### impact-06

**質問**: APサーバを複数台にスケールアウトするとき、セッション変数の保存先はどれを選ぶべき？各ストアの特徴を知りたい
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: APサーバを3台にスケールアウトする

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | FAIL (5 unsupported) |
| sections | 10 |
| turns | 7 |
| duration | 149秒 |
| cost | $0.993 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. DBストアでは有効期限切れセッションを定期削除するバッチが必要
2. nablarch.lettuce.clientType プロパティで masterReplica / cluster を指定できる
3. LettuceSimpleRedisClient / LettuceMasterReplicaRedisClient / LettuceClusterRedisClient というクラスが存在する
4. HiddenStore の encryptor に AesEncryptor / Base64Key を設定するXML構成が存在し、key・iv プロパティで固定キーを指定できる
5. セッションストアの有効期間はデフォルトでHTTPセッションに保存されるため、ステートレス化にはDBへの変更が必要

---

### impact-08

**質問**: テスト時だけシステム日時を任意の日付に差し替える方法はあるか？本番とテストで切り替えたい
**hearing_answer注入**: 処理方式: null（クロスファンクショナル） / やりたいこと: 締め処理のテストで特定の日付で動作確認する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL (5 unsupported) |
| sections | 6 |
| turns | 11 |
| duration | 72秒 |
| cost | $0.333 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. nablarch.test.FixedSystemTimeProvider という既製クラスが存在する
2. fixedDateプロパティでyyyyMMddHHmmss（14桁）またはyyyyMMddHHmmssSSS（17桁）フォーマットで日時を指定できる
3. nablarch.core.date.BasicSystemTimeProvider という既製クラスが本番用として存在する
4. BasicBusinessDateProvider の設定ファイルを差し替えることで業務日付を切り替えられる
5. BusinessDateProvider インタフェースを実装したクラスを作成してコンポーネント定義に設定することで業務日付をテスト用に切り替えられる

---

### qa-01

**質問**: 大量データを検索するとメモリが足りなくなる。1件ずつ読み込む方法はないか？
**hearing_answer注入**: 処理方式: Nablarchバッチ / やりたいこと: 10万件のレコードを処理する

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | PASS |
| sections | 3 |
| turns | 9 |
| duration | 63秒 |
| cost | $0.644 |
| hearing | skipped |

---

### qa-02

**質問**: DBからデータを読み込んで集計し、結果を別テーブルに書き込む定期処理を作りたい。どういう構成で実装すればいい？
**hearing_answer注入**: 処理方式: Nablarchバッチ / やりたいこと: テーブルからデータを読み込んで集計し、結果を別テーブルに書き込む

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | UNCERTAIN (5 unsupported) |
| sections | 12 |
| turns | 13 |
| duration | 103秒 |
| cost | $0.758 |
| hearing | skipped |

**幻覚UNCERTAIN — unsupported claims**:
1. DbConnectionContext.getConnection().prepareParameterizedSqlStatementBySqlId() というAPIが存在する
2. UniversalDao.insert() でDBへの書き込みを行う
3. 起動クラスが nablarch.fw.launcher.Main である
4. DB to DB / FILE to DB / DB to FILE というパターン分類がNablarchバッチに存在する
5. handle メソッド内で for ループを書くことが NoInputDataBatchAction を使ったアンチパターンである

---

### qa-03

**質問**: 2つの入力項目が一致しているかチェックしたい。メールアドレスと確認用メールアドレスの相関バリデーションのやり方を教えてほしい
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: 会員登録画面で相関バリデーションする

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL (5 unsupported) |
| sections | 7 |
| turns | 7 |
| duration | 195秒 |
| cost | $1.358 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. コンポーネント設定ファイルにBeanValidationStrategyをvalidationStrategyという名前で定義する
2. @InjectFormインターセプタ経由でバリデーションが実行される
3. @InjectFormにvalidate属性を指定できる（例: validate = "register"）
4. @OnErrorアノテーションをApplicationException.classに対して設定する
5. @OnErrorを設定しない場合、バリデーションエラーがシステムエラー扱いになる

---

### qa-04

**質問**: Bean ValidationのFormクラスの単体テストを書きたい。テストクラスの作り方とテストデータの準備方法を教えてほしい
**hearing_answer注入**: 処理方式: null（クロスファンクショナル） / やりたいこと: Nablarchの自動テストフレームワークでBean ValidationのFormクラスをテストする

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | FAIL (3 unsupported) |
| sections | 13 |
| turns | 5 |
| duration | 64秒 |
| cost | $0.552 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. Excelのすべてのセル書式は文字列に設定しなければならない
2. testSetterAndGetter が対応する型は String / BigDecimal / java.util.Date / valueOf(String) を持つクラス（Integer・Long 等）およびそれらの配列に限られる
3. テストメソッドとして testValidateCharsetAndLength / testSingleValidation / testBeanValidation / testSetterAndGetter を使用する

---

### qa-05

**質問**: REST APIでJSONを受け取ってDBに登録する処理を作りたい。リソースクラスの実装パターンを教えてほしい
**hearing_answer注入**: 処理方式: RESTfulウェブサービス / やりたいこと: リソースクラスでJSONリクエストを受け取りDBに登録する

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | FAIL (3 unsupported) |
| sections | 10 |
| turns | 5 |
| duration | 207秒 |
| cost | $1.085 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. @Consumes(MediaType.APPLICATION_JSON)でBodyConvertHandlerがアノテーションを参照しBodyConverterでFormに変換する
2. GenerationType.AUTO/SEQUENCE/IDENTITY/TABLEに対応
3. Formのプロパティを全てString型で宣言するのはBean Validationの要件

---

### qa-06

**質問**: 入力画面と確認画面のJSPを共通化して実装を減らす方法はあるか？
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: 入力画面と確認画面のJSPを共通化して実装を減らす

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | PASS (1 unsupported) |
| sections | 10 |
| turns | 8 |
| duration | 179秒 |
| cost | $1.789 |
| hearing | skipped |

**幻覚PASS — unsupported claims**:
1. カスタムタグを動作させるにはNablarchカスタムタグHTMLハンドラのハンドラ設定が必須

---

### qa-07

**質問**: CSVファイルの各行をJava Beansオブジェクトとして1件ずつ読み込みたい。どう実装する？
**hearing_answer注入**: 処理方式: Nablarchバッチ / やりたいこと: 固定フォーマットのCSVファイルを取り込む

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL (7 unsupported) |
| sections | 7 |
| turns | 6 |
| duration | 69秒 |
| cost | $0.547 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. ObjectMapperIterator<T> というクラスが存在し、DataReader 内で iterator パターンで使用できる
2. DataReader<T> インターフェースに read(), hasNext(), close() メソッドが存在する
3. BatchAction<T> を継承して handle() と createReader() を実装するアクションクラスのパターン
4. @LineNumber アノテーションをゲッターメソッドに付与して行番号を取得できる
5. FilePathSetting.getInstance().getFileWithoutCreate() でファイルパスを解決できる
6. FileDataReader / FileBatchAction という標準提供クラスが存在する
7. ObjectMapper はスレッドアンセーフである

---

### qa-08

**質問**: メッセージやラベルを日本語と英語で切り替えたい。多言語化の方法を教えてほしい
**hearing_answer注入**: 処理方式: null（クロスファンクショナル） / やりたいこと: メッセージやラベルを日本語と英語で切り替えられるよう多言語化する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL (4 unsupported) |
| sections | 6 |
| turns | 6 |
| duration | 148秒 |
| cost | $0.985 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. nablarch.common.handler.threadcontext.LanguageAttribute クラスが存在し、defaultLanguage プロパティを持つ
2. nablarch.common.web.handler.threadcontext.LanguageAttributeInHttpCookie クラスが存在し、defaultLanguage・supportedLanguages プロパティを持つ
3. LanguageAttributeInHttpUtil.keepLanguage() メソッドが存在し、言語をクッキーに保持できる
4. n:submitLink と n:param を組み合わせた JSP 言語切り替えリンクの実装パターン

---

### qa-09

**質問**: OS日時ではなく業務上の日付を取得する方法はあるか？締め処理でシステム日時と業務日付を分けて管理したい
**hearing_answer注入**: 処理方式: null（クロスファンクショナル） / やりたいこと: 月次締め処理で業務日付を使う

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | FAIL (4 unsupported) |
| sections | 6 |
| turns | 5 |
| duration | 85秒 |
| cost | $0.576 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. BusinessDateProviderインターフェースのsetDate(segment, date)メソッドで業務日付を更新できる
2. SystemRepository.get("businessDateProvider")でBasicBusinessDateProviderを取得できる
3. システムプロパティ -DBasicBusinessDateProvider.<区分>=yyyyMMdd で業務日付を上書き可能
4. nablarch-common-jdbcモジュールが追加で必要

---

### qa-10

**質問**: ユーザーの入力内容によって検索条件が変わるSQLを書きたい。入力がある項目だけ条件に含める方法はあるか？
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: 検索画面で動的SQLを使う

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | PASS |
| sections | 2 |
| turns | 6 |
| duration | 51秒 |
| cost | $0.577 |
| hearing | skipped |

---

### qa-11a

**質問**: エラーが発生したときにエラー画面を表示したり、ログを出力する仕組みはどうなっている？
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: エラー画面の表示とログ出力の仕組みを知りたい

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL (5 unsupported) |
| sections | 10 |
| turns | 5 |
| duration | 265秒 |
| cost | $1.481 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. HttpErrorHandlerのdefaultPagesプロパティにステータスコードパターンと遷移先JSPをマッピングできる
2. defaultPagesではなくweb.xmlへのエラーページ設定を推奨する
3. @OnErrorsアノテーションで複数例外の遷移先を定義でき、継承関係がある場合はサブクラスを先に定義する必要がある
4. FailureLogUtilクラスを使用してアプリケーションから明示的に障害ログを出力できる
5. 障害ログは障害通知ログ(ロガー名MONITOR)と障害解析ログ(ロガー名クラス名)の2種類に分かれる

---

### qa-11b

**質問**: エラーが発生したときにエラー画面を表示したり、ログを出力する仕組みはどうなっている？
**hearing_answer注入**: 処理方式: RESTfulウェブサービス / やりたいこと: エラーレスポンスとログ出力の仕組みを知りたい

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | FAIL (6 unsupported) |
| sections | 8 |
| turns | 9 |
| duration | 74秒 |
| cost | $0.607 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. GlobalErrorHandlerでServiceErrorはServiceError#writeLogを呼び出す
2. GlobalErrorHandlerでResult.ErrorはFATALレベルでログ出力される
3. GlobalErrorHandlerでThreadDeathはINFOレベルでログ出力される
4. GlobalErrorHandlerでStackOverflowError/OutOfMemoryError/VirtualMachineErrorはFATALレベルでログ出力される
5. JaxRsAccessLogHandler（クラス名: nablarch.fw.jaxrs.JaxRsAccessLogHandler）をハンドラキューに追加するとHTTPアクセスログをINFOレベルで出力できる
6. GlobalErrorHandlerはログレベルの切り替えを設定で行えないため要件を満たせない場合はプロジェクト固有のハンドラを作成する必要がある

---

### qa-12a

**質問**: 入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: バリデーションエラーメッセージをユーザーに返す

| 指標 | 値 |
|---|---|
| 精度 | 1/2 FAIL |
| 幻覚 | FAIL (5 unsupported) |
| sections | 6 |
| turns | 13 |
| duration | 87秒 |
| cost | $0.837 |
| hearing | skipped |

**精度FAIL — 未検出 facts**:
- HttpErrorHandlerがApplicationExceptionのメッセージをErrorMessagesに変換しリクエストスコープに設定する

**幻覚FAIL — unsupported claims**:
1. @OnErrorが設定されていない場合、バリデーションエラーがシステムエラー扱いになる
2. Thymeleafで errors.hasError('form.userName') を使ってエラー判定する
3. Thymeleafで errors.getMessage('form.userName') を使ってエラーメッセージを取得する
4. nablarch.core.validation.ee.Required.message=必須項目です。
5. <component name="validationStrategy" class="nablarch.common.web.validator.BeanValidationStrategy" />でBean Validationを有効化する

---

### qa-12b

**質問**: 入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい
**hearing_answer注入**: 処理方式: RESTfulウェブサービス / やりたいこと: バリデーションエラーメッセージをユーザーに返す

| 指標 | 値 |
|---|---|
| 精度 | 1/2 FAIL |
| 幻覚 | FAIL (3 unsupported) |
| sections | 5 |
| turns | 9 |
| duration | 61秒 |
| cost | $0.626 |
| hearing | skipped |

**精度FAIL — 未検出 facts**:
- @Validアノテーションによりバリデーションエラーが自動的にエラーレスポンスになる

**幻覚FAIL — unsupported claims**:
1. JaxRsBeanValidationHandler が ApplicationException を送出する
2. JaxRsResponseHandler の errorResponseBuilder プロパティに継承クラスを登録する
3. ErrorResponseBuilder の処理中に例外が発生した場合、フレームワークは WARN レベルでログ出力を行い、ステータスコード 500 のレスポンスを生成する

---

### qa-13

**質問**: フォームから受け取ったデータをDBに登録する処理の実装パターンを知りたい
**hearing_answer注入**: 処理方式: RESTfulウェブサービス / やりたいこと: フォームから受け取ったデータをDBに登録する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | FAIL (5 unsupported) |
| sections | 10 |
| turns | 11 |
| duration | 124秒 |
| cost | $0.898 |
| hearing | skipped |

**幻覚FAIL — unsupported claims**:
1. BodyConvertHandlerがJSONをFormに変換する
2. バリデーションエラー発生時にApplicationExceptionが送出される
3. コンポーネント名'daoContextFactory'でBasicDaoContextFactoryを設定する
4. BodyConvertHandlerのbodyConvertersにapplication/json対応コンバータを設定する必要があり、未設定MIMEには415を返す
5. JaxRsBeanValidationHandlerはBodyConvertHandlerより後ろに設定する必要がある

---

### qa-14

**質問**: Nablarch 5からNablarch 6にバージョンアップするとき、Jakarta EE 10対応でアプリケーションに影響がある変更は何か？
**hearing_answer注入**: 処理方式: null（クロスファンクショナル） / やりたいこと: Nablarch 5からNablarch 6へのバージョンアップでJakarta EE 10対応の影響を調べる

| 指標 | 値 |
|---|---|
| 精度 | 2/2 PASS |
| 幻覚 | UNCERTAIN (12 unsupported) |
| sections | 10 |
| turns | 6 |
| duration | 71秒 |
| cost | $0.559 |
| hearing | skipped |

**幻覚UNCERTAIN — unsupported claims**:
1. jakarta.servlet:jakarta.servlet-api等への依存関係変更
2. jakarta.platform:jakarta.jakartaee-bom:10.0.0のBOM利用推奨
3. hibernate-validator 8.0.0.Finalへの更新
4. jersey-bom:3.1.8への更新
5. org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0への更新
6. waitt-maven-pluginをjetty-ee10-maven-plugin:12.0.12に変更
7. nablarch-testing-jetty6をnablarch-testing-jetty12に変更しHttpServerFactoryJetty12を使用
8. gsp-dba-maven-pluginを5.1.0に更新
9. JBeret jberet-core:2.1.4.Final、weld-core-impl:5.0.1.Finalへの更新
10. Nablarch 5u25相当からNablarch 6u2へのバージョンアップを前提
11. web.xmlのXMLスキーマをjakarta.ee URLに変更
12. JSPタグライブラリURIをjakarta.tags.coreに変更

---

### qa-15

**質問**: クロスサイト・スクリプティング（XSS）の対策はNablarchでどこまで対応できるか？カスタムタグを使えばサニタイジングされるのか？
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: XSS対策のNablarch対応状況を確認する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | UNCERTAIN (5 unsupported) |
| sections | 10 |
| turns | 5 |
| duration | 208秒 |
| cost | $1.675 |
| hearing | skipped |

**幻覚UNCERTAIN — unsupported claims**:
1. SecureHandlerのクラス名 nablarch.fw.web.handler.SecureHandler および設定例（XML）
2. XssProtectionHeader, FrameOptionsHeader（option=DENY）, ContentTypeOptionsHeaderというクラスが存在する
3. HTTP文字エンコード制御ハンドラにより Content-Type charset が設定されエスケープ迂回XSSを防止できる
4. rawWriteタグはHTMLエスケープなしで出力する
5. prettyPrintタグは非推奨（設定不備によるXSSリスクあり）

---

### oos-impact-01

**質問**: NablarchでOAuth2やOpenID Connectによる認証を実装したい。Nablarchにその仕組みは組み込まれているか？
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: OAuth2/OpenID Connect認証の対応可否を確認する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | UNCERTAIN (12 unsupported) |
| sections | 7 |
| turns | 6 |
| duration | 62秒 |
| cost | $0.549 |
| hearing | skipped |

**幻覚UNCERTAIN — unsupported claims**:
1. NablarchにはOAuth2/OpenID Connectの認証機能は組み込まれていない
2. 認証はフレームワークとして提供しておらず、プロジェクトで実装する
3. 公式ビジネスサンプル nablarch-oidc が nablarch-biz-sample-all に含まれる
4. バックエンド（RESTfulウェブサービス）でIDトークンを検証する構成を想定
5. 対応サービスはAmazon CognitoユーザープールおよびAzure Active Directory B2C
6. CognitoIdTokenVerifier というコンポーネントが存在する
7. IdTokenVerifier インターフェース/クラスが存在し verify() メソッドを持つ
8. SystemRepository.get("idTokenVerifier") でコンポーネントを取得する
9. SessionUtil.changeId(context) でセッションIDを変更する
10. CsrfTokenUtil.regenerateCsrfToken(context) でCSRFトークンを再生成する
11. SessionUtil.put(context, "user.id", userId) で認証状態をセッションに保持する
12. Auth0の java-jwt および jwks-rsa-java を依存関係として使用する

---

### oos-qa-01

**質問**: バッチ処理の進捗状況をWebSocketでリアルタイムにブラウザへ通知したい。NablarchでWebSocketを使う方法はあるか？
**hearing_answer注入**: 処理方式: ウェブアプリケーション / やりたいこと: WebSocketによるリアルタイム通知の実装方法を確認する

| 指標 | 値 |
|---|---|
| 精度 | 1/1 PASS |
| 幻覚 | UNCERTAIN (5 unsupported) |
| sections | 5 |
| turns | 10 |
| duration | 103秒 |
| cost | $0.796 |
| hearing | skipped |

**幻覚UNCERTAIN — unsupported claims**:
1. NablarchにはWebSocketのサポートはない
2. Nablarchが提供する非同期連携パターンは「テーブルをキューとして使ったメッセージング」のみ
3. WebSocketに関する記述は「Java EE/Jakarta EEの仕様名対応表」のJakarta WebSocketという列挙のみ
4. Nablarchで時間のかかる処理を非同期に実行する公式パターンはDBをキューとして使うポーリング型
5. WebSocketを使う場合はNablarchのハンドラ機構の外側でServletコンテナの機能を直接利用することになる

---

