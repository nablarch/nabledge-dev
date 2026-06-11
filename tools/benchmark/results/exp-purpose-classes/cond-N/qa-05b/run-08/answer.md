**結論**: RESTful ウェブサービスで JSON を受け取って DB に登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたメソッドで Form を受け取り、`BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**① Form クラスの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する

    // ゲッタ及びセッタは省略
}
```

**② リソースクラス（アクションメソッド）の実装**

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

| ポイント | 説明 |
|---|---|
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディ変換ハンドラが JSON をこのアノテーションをもとに Form に変換する |
| `@Valid` | Jakarta RESTful Web Services Bean Validation ハンドラが Form に対してバリデーションを実行する。エラー時は `ApplicationException` を送出し後続処理に委譲しない |
| `@Path` + `@POST` | ルーティングアダプタが `@Path` の値とHTTPメソッドアノテーションをもとにリクエストをディスパッチする |
| `BeanUtil.createAndCopy()` | Form（全 String 型）をエンティティクラスに変換する |
| `UniversalDao.insert()` | エンティティをデータベースに登録する |
| 戻り値 `HttpResponse(201)` | リソース作成完了を示すステータスコード 201 を返却する |

**注意点**:
- Form のプロパティは全て `String` 型で宣言すること（型変換はバリデーション処理が行う）
- `@Valid` を付けない場合、バリデーションは実行されない
- `Content-Type: application/json` 以外のリクエストが来た場合、ステータスコード `415`（Unsupported Media Type）が返却される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8