**結論**: NablarchのRESTfulウェブサービスでは、`@Consumes(MediaType.APPLICATION_JSON)` アノテーションを付けたアクションメソッドにリクエストボディの変換を任せ、`UniversalDao.insert` でDBに登録する構成になります。JSONの受け取りからDB登録までは主に「リクエストボディ変換ハンドラ」「Bean Validationハンドラ」「アクションクラス」の3段構えで処理されます。

---

**根拠**

**処理の流れ（ハンドラキュー）**

最小ハンドラ構成に沿った処理の流れは以下のとおりです。

| 順 | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンスの書き込み・エラー処理 |
| 3 | データベース接続管理ハンドラ | DB接続の取得/解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット/ロールバック |
| 5 | ルーティングアダプタ | URIをもとに呼び出すアクションメソッドを決定 |
| 6 | **リクエストボディ変換ハンドラ** | **JSONリクエストボディをFormクラスに変換** |
| 7 | **Bean Validationハンドラ** | **変換したFormに対してバリデーションを実行** |

**JSONを受け取る仕組み（リクエストボディ変換ハンドラ）**

アクションメソッドに付与された `@Consumes` アノテーションのMIMEタイプを見て、対応する `BodyConverter` がリクエストボディをFormクラスに変換します。

```java
// リクエストボディをFormに変換する仕組み
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse saveJson(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**DBに登録する実装例**

`ProjectForm` (Formクラス) から `Project` (Entity) に `BeanUtil.createAndCopy` で変換し、`UniversalDao.insert` でDB登録します。

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

**URLとのマッピング（ルーティングアダプタ）**

`@Path` アノテーションでクラスにパスを、`@POST` でHTTPメソッドを紐づけます。

```java
@Path("/sample")
public class SampleAction {
    @POST
    @Produces(MediaType.APPLICATION_JSON)
    public int register(JaxRsHttpRequest request) {
        // 省略
    }
}
```

---

**注意点**

- Formクラスのプロパティは**全てString型**で宣言すること。バリデーションルールの設定に関わります。
- `BodyConvertHandler` の `bodyConverters` プロパティに `application/json` に対応したコンバータを設定しておく必要があります。設定がない場合はステータスコード `415` が返ります。
- バリデーションエラー時は `ApplicationException` が送出され、後続のDB登録処理は実行されません。
- `BodyConvertHandler` はルーティングアダプタよりも**後ろ**に設定する制約があります。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8