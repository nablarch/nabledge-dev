**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスに `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付与し、引数にフォームクラスを定義する。フレームワークがJSONをフォームに自動変換し、`BeanUtil.createAndCopy()` でエンティティに変換後 `UniversalDao.insert()` でDB登録する。

**根拠**:

### 1. フォームクラスの作成

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**ポイント**: プロパティは全て `String` 型で宣言する。

### 2. リソースクラスの実装

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

**ポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` を指定すると、リクエストボディのJSONがフレームワーク（`BodyConvertHandler`）によってフォームクラスに自動変換される
- `@Valid` アノテーションでフォームのBean Validationが実行される
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換してからDB登録する
- 登録成功時はステータスコード `201 Created` を返す

### 3. URLマッピング

クラスに `@Path("/projects")`、メソッドに `@POST` を付与することで、`POST /projects` リクエストにマッピングされる（ルーティングアダプタのJakarta RESTful Web Servicesアノテーション方式を使用）。

**注意点**:
- `Content-Type: application/json` 以外のリクエストが来た場合、フレームワークはステータスコード `415 Unsupported Media Type` を返す
- Jakarta RESTful Web Services仕様の `@QueryParam` や `@PathParam` は使用できない（パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得する）

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5