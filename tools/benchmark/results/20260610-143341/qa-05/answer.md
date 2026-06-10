**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)` を付与したリソースクラスを作成し、フォームで受け取ったデータを `BeanUtil` でエンティティに変換して `UniversalDao.insert()` で登録します。

**根拠**:

**1. フォームクラスの作成**

受信するJSONのフィールドに対応したフォームを作成します。プロパティは全て `String` 型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラスの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を付与することで、リクエストボディを `BodyConvertHandler` がフォームへ変換します
- `@Valid` アノテーションで Bean Validation によるバリデーションを実行します
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録します
- 戻り値として `HttpResponse.Status.CREATED`（ステータスコード `201`）を返します

**3. メソッドシグネチャのバリエーション**

| 引数の型 | 用途 |
|---|---|
| フォーム（Java Beans） | リクエストボディの受け取り（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダの取得 |
| 組み合わせ | 上記の複数を同時に使用したい場合 |

**注意点**:
- `BodyConvertHandler` のコンポーネント設定に `application/json` 対応の `BodyConverter` が設定されていること（設定されていない場合はステータスコード `415` が返ります）
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が一致しない場合もステータスコード `415` が返ります

参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1`, `processing-pattern/restful-web-service/restful-web-service-resource-signature.json:s1`, `component/handlers/handlers-body-convert-handler.json:s4`, `component/handlers/handlers-body-convert-handler.json:s5`