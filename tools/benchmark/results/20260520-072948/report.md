# ベンチマーク実行レポート

**実行日時**: 2026-05-20  
**実行ディレクトリ**: `tools/benchmark/results/20260520-072948`  
**スキル**: `.claude/skills/nabledge-6`  
**ステータス**: 分析完了（2026-05-20 B-4-1-A）

---

## 幻覚FAIL 全件分析サマリー（B-4-1-A）

幻覚FAIL は19シナリオ。全件の unsupported claims を知識ファイルと突合した結果：

| 分類 | 件数 | 説明 |
|---|---|---|
| **false FAIL（search_sections 内）** | 78件 | search_sections に記述があるが evaluate.py が must/acceptable しか渡さないため FAIL |
| **false FAIL（search_sections 外、KB 内）** | 4件 | 知識ファイルに記述はあるが LLM の search_sections に含まれなかったセクション |
| **真の幻覚** | 5件 | 知識ファイルに存在しない、または誤った内容 |

### 真の幻覚 5件

| シナリオ | claim | 内容 |
|---|---|---|
| impact-06 | claim 1 | DBストア定期削除を「バッチ」と表現（知識ファイルは「定期的に削除する必要がある」のみ。バッチという語なし） |
| impact-08 | claim 2 | fixedDate の桁数を「14桁」「17桁」と誤記（知識ファイルは「12桁」「15桁」） |
| impact-08 | claim 4 | 「BasicBusinessDateProvider の**設定ファイル**を差し替える」（知識ファイルは「コンポーネント定義で指定する**クラス**を差し替える」） |
| qa-05 | claim 3 | 「String型宣言は Bean Validation の**要件**」（知識ファイルはBean Validationの仕様要件とは言っていない。設計上の推奨事項） |
| qa-12a | claim 4 | `Required.message=**必須項目です**`（知識ファイルは `Required.message=入力してください。`） |

### search_sections 外の false FAIL 4件（KB には存在する）

| シナリオ | claim | 知識ファイルの場所 | search_sections |
|---|---|---|---|
| impact-06 | claim 2（clientType プロパティ） | adapters-redisstore-lettuce-adaptor.json:**s7** | s1/s5/s6 のみ |
| impact-06 | claim 4（HiddenStore + AesEncryptor） | libraries-session-store.json:**s12** | s2/s8/s16 のみ |
| review-09 | claim 6（SecureHandler 設定順序） | handlers-secure-handler.json:**s3** | s7/s8/s9 のみ |
| review-09 | claim 7（デフォルトコンポーネント明示設定） | handlers-secure-handler.json:**s5** | s7/s8/s9 のみ |

**根本原因**: evaluate.py の幻覚チェックは must/acceptable セクションのみを参照しており、LLM が実際に参照した search_sections を含めていない。真の幻覚は5件のみ（全unsupported claimsの約6%）。B-4-1-C で修正方針を設計する。

---

## 精度FAIL 分析（B-4-1-A 追記）

精度FAIL は qa-12a・qa-12b の2件。

### read-sections.sh permission_denied の全体状況

`claude -p` 実行時の `--allowedTools "Bash(read-sections.sh *)"` パターンが、LLM が `bash scripts/read-sections.sh ...` と呼び出す際にマッチせず denied になるケースが多発している（`bash` が先頭にあるため pattern `read-sections.sh *` にマッチしない）。

30シナリオ中 **23シナリオ** で `read-sections.sh` の denied が発生。ただし denied が発生しても大半のシナリオでは BENCHMARK_SEARCH にセクションが記録されている。これは semantic-search の返り値（ページ・セクション候補）を LLM がそのまま BENCHMARK_SEARCH に出力しているため。denied は回答の品質に影響するが、シナリオによって影響度が異なる。

### qa-12a 精度FAIL の事実

**must fact**: `HttpErrorHandler が ApplicationException のメッセージを ErrorMessages に変換しリクエストスコープに設定する`  
**must fact のセクション**: `handlers-HttpErrorHandler.json:s4`

**LLM の動き（trace.json の permission_denials より）**:
- LLM が `read-sections.sh` に渡そうとしたセクションリスト（4回全て denied）:
  ```
  web-application-error-message.json:s1
  handlers-InjectForm.json:s3, s4
  libraries-bean-validation.json:s7, s16
  libraries-tag.json:s29
  libraries-tag-reference.json:s48, s49
  ```
- `handlers-HttpErrorHandler.json` は **このリストに含まれていない**
- BENCHMARK_SEARCH のセクションも HttpErrorHandler なし

**原因**: semantic-search が `handlers-HttpErrorHandler.json` をそもそも返さなかった。denied とは無関係。ページ選定（semantic-search）の段階で HttpErrorHandler が漏れた。semantic-search の中間ログは trace.json に記録されないため、なぜ漏れたかは現状のログから確認不可。

### qa-12b 精度FAIL の事実

**must fact 1**: `@Valid アノテーションによりバリデーションエラーが自動的にエラーレスポンスになる`  
**must fact 1 のセクション**: `libraries-bean-validation.json:s17`

**must fact 2**: `ErrorResponseBuilder の継承クラスでエラーメッセージをレスポンスボディに設定する`  
**must fact 2 のセクション**: `handlers-jaxrs-response-handler.json:s7`（search_sections に含まれ、回答にも記載 → PRESENT）

**LLM の動き（trace.json の permission_denials より）**:
- LLM が `read-sections.sh` に渡そうとしたセクションリスト（3回全て denied）:
  ```
  handlers-jaxrs-response-handler.json:s4, s7
  handlers-jaxrs-bean-validation-handler.json:s4
  libraries-bean-validation.json:s17   ← must fact のセクション
  restful-web-service-feature-details.json:s2, s11
  ```
- `libraries-bean-validation.json:s17` は **選定リストに含まれていた**
- しかし denied で内容を読めず、BENCHMARK_SEARCH の最終出力から s17 が**脱落**した

**evaluate.py の claim verdict**: UNCERTAIN（ABSENTではない）。理由：LLM の回答は「@Valid を付与する」と書いているが「自動的にエラーレスポンスになる」とは書いておらず、カスタム実装が必要と説明している。評価 LLM が一致判断困難と判定。

**原因のまとめ**:
- s17 はセクション選定に含まれていたが `read-sections.sh` denied で内容未読
- 内容を読めないまま回答生成 → @Valid の動作を知識ファイルに基づかず不正確に説明
- さらに denied 後の BENCHMARK_SEARCH 出力から s17 が脱落（LLM が denied を受けてセクションリストを修正した）

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| LoopHandler が transactionAbnormalEnd を呼び出す | false FAIL | handlers-loop-handler.json:s6「ロールバック後にコールバック処理を実行する」+コード例 |
| TransactionEventCallback の2メソッドとロールバック後の新トランザクション | false FAIL | handlers-transaction-management-handler.json:s6 に明記 |
| Handler+TransactionEventCallback 同時実装 → LoopHandler後続配置 | false FAIL | handlers-loop-handler.json:s6 のコード例・説明に明記 |
| 複数ハンドラで例外発生時に残りコールバック未実行 | false FAIL | handlers-loop-handler.json:s6「残りのハンドラに対するコールバック処理は実行しない」 |

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

**裏取り結果**:

| claim | 判定 | 根拠 |
|---|---|---|
| DBストア定期削除「バッチ」 | **真の幻覚** | 知識ファイルは「定期的に削除する必要がある」と記述。「バッチ」という語は存在しない |
| clientType プロパティ (masterReplica/cluster) | false FAIL | adapters-redisstore-lettuce-adaptor.json:s7 に明記。ただし search_sections は s1/s5/s6 のみで s7 は含まれず → LLM は知識ファイルから正確に引用したが evaluate.py が渡すセクション外 |
| 3クラスの存在 | false FAIL | adapters-redisstore-lettuce-adaptor.json:s6（search_sections に含まれる）に明記 |
| HiddenStore + AesEncryptor/Base64Key + key/iv | false FAIL | libraries-session-store.json:s12 に明記。ただし search_sections は s2/s8/s16 のみで s12 は含まれず → LLM は知識ファイルから正確に引用したが evaluate.py が渡すセクション外 |
| 有効期間はデフォルトHTTPセッション → ステートレス化にはDB変更 | false FAIL | libraries-stateless-web-app.json:s2（search_sections に含まれる）「セッションストアはデフォルトでHTTPセッションに依存」に記述あり |

**impact-06 まとめ**: claim 1（バッチ）のみ**真の幻覚**。claim 2・4 は false FAIL だが evaluate.py が渡すセクション外での記述（search_sections の選択ミス）。claim 3・5 は evaluate.py の false FAIL（search_sections 内に記述あり）。

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

**裏取り結果**:

| claim | 判定 | 根拠 |
|---|---|---|
| nablarch.test.FixedSystemTimeProvider | false FAIL | testing-framework-03-Tips.json:s12（search_sections に含まれる）に明記 |
| fixedDate「14桁」「17桁」 | **真の幻覚** | 知識ファイルは「12桁」「15桁」と記載。14桁・17桁は LLM による誤記（フォーマット文字列の文字数を数えて間違えた） |
| nablarch.core.date.BasicSystemTimeProvider | false FAIL | libraries-date.json:s5（search_sections に含まれる）に明記 |
| BasicBusinessDateProvider の設定ファイル差し替え | **真の幻覚** | 知識ファイルの記述は「コンポーネント定義で指定するクラスを差し替える」。「設定ファイルを差し替える」という表現は存在しない |
| BusinessDateProvider 実装クラスをコンポーネント定義に設定 | false FAIL | libraries-date.json:s13（search_sections に含まれる）に明記 |

**impact-08 まとめ**: claim 2（桁数誤記）・claim 4（設定ファイル差し替えという誤表現）が**真の幻覚**。他は false FAIL。

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| BeanValidationStrategy を validationStrategy 名で定義 | false FAIL | libraries-bean-validation.json:s16（search_sections）に明記 |
| @InjectForm インターセプタ経由バリデーション | false FAIL | libraries-bean-validation.json:s16 / libraries-nablarch-validation.json:s21（search_sections）に明記 |
| @InjectForm の validate 属性 | false FAIL | handlers-InjectForm.json:s3（search_sections）のコード例に明記 |
| @OnError(type = ApplicationException.class) | false FAIL | handlers-InjectForm.json:s3（search_sections）のコード例に明記 |
| @OnError 未設定でシステムエラー扱い | false FAIL | handlers-InjectForm.json:s4（search_sections）に明記 |

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| Excelのセル書式はすべて文字列 | false FAIL | testing-framework-01-Abstract.json:s14（search_sections）「全てのセルの書式を文字列に設定」 |
| testSetterAndGetter の対応型 | false FAIL | testing-framework-01-entityUnitTestWithBeanValidation.json:s14（search_sections）に対応型一覧が明記 |
| 4つのテストメソッド名 | false FAIL | testing-framework-01-entityUnitTestWithBeanValidation.json:s6/s9/s12/s14（search_sections）で各メソッド確認 |

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

**裏取り結果**:

| claim | 判定 | 根拠 |
|---|---|---|
| @Consumes → BodyConvertHandler → BodyConverter で変換 | false FAIL | handlers-body-convert-handler.json:s5（search_sections）「Consumesにより決まる」「対応したBodyConverterでリクエストボディが変換される」に明記 |
| GenerationType.AUTO/SEQUENCE/IDENTITY/TABLE | false FAIL | libraries-universal-dao.json:s13（search_sections）「すべてのストラテジをサポート」+4種の実装例 |
| String型宣言は Bean Validation の要件 | **真の幻覚（表現の誤り）** | 知識ファイルは「Beanクラスのプロパティの型は全てStringとして定義すること」と記述するが、「Bean Validationの要件」とは言っていない。理由は「変換失敗前にバリデーションが走らなくなるため」という設計上の考慮事項。restful-web-service-getting-started-create.json:s1（search_sections）には「プロパティは全てString型で宣言する」の記述はある |

**qa-05 まとめ**: claim 3 のみ**真の幻覚（因果の誤帰属）**。claim 1・2 は false FAIL。

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| ObjectMapperIterator + DataReader 内で iterator パターン | false FAIL | nablarch-batch-getting-started:s2（search_sections）に明記 |
| DataReader<T> の read/hasNext/close | false FAIL | nablarch-batch-getting-started:s2（search_sections）のコード例に明記 |
| BatchAction<T> 継承 + handle/createReader 実装 | false FAIL | nablarch-batch-getting-started:s3（search_sections）のコード例に明記 |
| @LineNumber アノテーション | false FAIL | nablarch-batch-getting-started:s2（search_sections）に明記 |
| FilePathSetting.getInstance().getFileWithoutCreate() | false FAIL | nablarch-batch-getting-started:s2（search_sections）のコード例に明記 |
| FileDataReader / FileBatchAction | false FAIL | nablarch-batch-architecture.json:s7/s8（search_sections）に明記 |
| ObjectMapper スレッドアンセーフ | false FAIL | libraries-data-bind.json:s15（search_sections）に明記 |

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| LanguageAttribute + defaultLanguage | false FAIL | handlers-thread-context-handler.json:s4（search_sections）のXML例に明記 |
| LanguageAttributeInHttpCookie + 2プロパティ | false FAIL | handlers-thread-context-handler.json:s7（search_sections）のXML例に明記 |
| LanguageAttributeInHttpUtil.keepLanguage() | false FAIL | handlers-thread-context-handler.json:s7（search_sections）のコード例に明記 |
| n:submitLink + n:param の JSP パターン | false FAIL | handlers-thread-context-handler.json:s7（search_sections）のJSP例に明記 |

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| BusinessDateProvider.setDate(segment, date) | false FAIL | libraries-date.json:s10（search_sections）のコード例に明記 |
| SystemRepository.get("businessDateProvider") | false FAIL | libraries-date.json:s10（search_sections）に明記 |
| -DBasicBusinessDateProvider.<区分>=yyyyMMdd | false FAIL | libraries-date.json:s9（search_sections）に明記 |
| nablarch-common-jdbc モジュール | false FAIL | libraries-date.json:s3（search_sections）に明記（注: s3 は search_sections リストにないが libraries-date.json:s2 から参照されている。ただし s2 自体は search_sections に含まれる） |

**補足**: claim 4 については libraries-date.json:s2（search_sections）に「モジュール一覧参照」の記述があり、s3 に実際の依存関係が記載。s3 自体は search_sections に含まれていないが、s2 が含まれており LLM は s3 も参照した可能性がある。いずれも知識ファイルに明記された事実。

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| defaultPages にステータスコードパターン→JSP マッピング | false FAIL | handlers-HttpErrorHandler.json:s6（search_sections）に設定例あり |
| defaultPages より web.xml 推奨 | false FAIL | handlers-HttpErrorHandler.json:s6（search_sections）「web.xml へ行うことを推奨する」 |
| @OnErrors + サブクラスを先に定義 | false FAIL | handlers-on-errors.json:s3（search_sections）に明記 |
| FailureLogUtil クラス | false FAIL | libraries-failure-log.json:s3（search_sections）のコード例に明記 |
| 障害通知ログ(MONITOR) / 障害解析ログ(クラス名) | false FAIL | libraries-failure-log.json:s1（search_sections）のテーブルに明記 |

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| ServiceError → ServiceError#writeLog | false FAIL | handlers-global-error-handler.json:s4（search_sections）のエラーテーブルに明記 |
| Result.Error → FATAL | false FAIL | handlers-global-error-handler.json:s4（search_sections）に明記 |
| ThreadDeath → INFO | false FAIL | handlers-global-error-handler.json:s4（search_sections）に明記 |
| StackOverflowError/OutOfMemoryError/VirtualMachineError → FATAL | false FAIL | handlers-global-error-handler.json:s4（search_sections）に3エントリ全てFATAL記載 |
| nablarch.fw.jaxrs.JaxRsAccessLogHandler + INFOレベル | false FAIL | handlers-jaxrs-access-log-handler.json:s4（search_sections）＋libraries-jaxrs-access-log.json:s1（search_sections）に明記 |
| GlobalErrorHandler は設定で切り替え不可 → プロジェクト固有ハンドラ作成 | false FAIL | handlers-global-error-handler.json:s5（search_sections）に明記 |

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

**裏取り結果**:

| claim | 判定 | 根拠 |
|---|---|---|
| @OnError 未設定でシステムエラー扱い | false FAIL | handlers-InjectForm.json:s4（search_sections）に明記 |
| errors.hasError('form.userName') | false FAIL | web-application-error-message.json（search_sections、ファイル全体）に実装例あり |
| errors.getMessage('form.userName') | false FAIL | web-application-error-message.json（search_sections、ファイル全体）に実装例あり |
| Required.message=必須項目です | **真の幻覚** | 知識ファイルの記述は `Required.message=入力してください。`。「必須項目です。」は存在しない |
| BeanValidationStrategy の設定 | false FAIL | libraries-bean-validation.json:s16（search_sections）に明記 |

**qa-12a まとめ**: claim 4（メッセージ内容の誤り）のみ**真の幻覚**。他は false FAIL。

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| JaxRsBeanValidationHandler が ApplicationException 送出 | false FAIL | handlers-jaxrs-bean-validation-handler.json:s4（search_sections）のintroに明記 |
| errorResponseBuilder プロパティに継承クラス登録 | false FAIL | handlers-jaxrs-response-handler.json:s4（search_sections）のXML例・説明に明記 |
| ErrorResponseBuilder 処理中例外 → WARN + 500 | false FAIL | handlers-jaxrs-response-handler.json:s4（search_sections）に明記 |

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

**裏取り結果**: 全件 search_sections に明記あり → **evaluate.py の false FAIL**

| claim | 判定 | 根拠 |
|---|---|---|
| BodyConvertHandler が JSON を Form に変換 | false FAIL | handlers-body-convert-handler.json:s5（search_sections）に明記 |
| バリデーションエラー → ApplicationException 送出 | false FAIL | handlers-jaxrs-bean-validation-handler.json:s4（search_sections）のintroに明記 |
| daoContextFactory 名で BasicDaoContextFactory | false FAIL | libraries-universal-dao.json:s6（search_sections）に明記 |
| bodyConverters 未設定 MIME → 415 | false FAIL | handlers-body-convert-handler.json:s4（search_sections）に明記 |
| JaxRsBeanValidationHandler は BodyConvertHandler より後ろ | false FAIL | handlers-jaxrs-bean-validation-handler.json:s3（search_sections）に明記 |

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

