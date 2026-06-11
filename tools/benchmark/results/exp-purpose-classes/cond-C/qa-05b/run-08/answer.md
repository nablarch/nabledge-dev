**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDB登録する。戻り値は `HttpResponse(201)` を返す。

**根拠**:

**リソースクラスのメソッドシグネチャ**

メソッド引数には、リクエストボディから変換したFormクラスを受け取る。戻り値には `HttpResponse`（ステータスコード指定あり）または Formクラス（BodyConvertHandlerがレスポンスボディに変換）が使える。

```java
// 引数の種類 (用途に応じて組み合わせ可)
// - Formクラス(Java Beans): リクエストボディから変換
// - JaxRsHttpRequest: パスパラメータ・クエリパラメータ取得
// - ExecutionContext: スコープ変数アクセス
// - 引数無し: ボディ不要な場合
```

**実装パターン（完全例）**

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` — `BodyConvertHandler` がこのアノテーションを元に、リクエストボディを `application/json` 対応の `BodyConverter`（JerseyではJackson）でFormクラスに変換する
- `@Valid` — `JaxRsBeanValidationHandler` が変換後のFormに対してBeanValidationを実行する。バリデーションエラー時は `ApplicationException` を送出
- `BeanUtil.createAndCopy(Project.class, project)` — FormクラスからEntityクラスへプロパティをコピーして生成
- `UniversalDao.insert(entity)` — Entityに付いたJakarta Persistenceアノテーション（`@Entity`, `@Table`, `@Id` 等）からINSERT文を自動生成して実行
- `HttpResponse(201)` — リソース作成完了を示すステータスコード201を返す

**処理の流れ**

リクエスト受信からDB登録までの流れは以下の通り:

| No. | ハンドラ | 往路処理 |
|-----|---------|---------|
| 1-2 | グローバルエラーハンドラ / JaxRsResponseHandler | エラー処理・レスポンス書き込み準備 |
| 3-4 | DB接続管理ハンドラ / トランザクション制御ハンドラ | DB接続取得・トランザクション開始 |
| 5 | ルーティングアダプタ | URIとアクションメソッドを紐付け |
| 6 | BodyConvertHandler | リクエストボディをFormクラスに変換 |
| 7 | JaxRsBeanValidationHandler | Formクラスにバリデーション実行 |
| — | リソースクラスのメソッド | `UniversalDao.insert` でDB登録 |

復路でトランザクションがコミットされ、`JaxRsResponseHandler` がレスポンスをクライアントに返す。

**注意点**:
- Formクラスのプロパティは全てString型で宣言すること（バリデーション処理の要件）
- `BodyConvertHandler` はルーティングアダプタより後ろに設定する必要がある
- Jersey環境の場合、`JerseyJaxRsHandlerListFactory` を使うと `BodyConvertHandler`（Jackson設定済み）と `JaxRsBeanValidationHandler` が自動的にセットされる

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2