**結論**: JSONを受け取ってDBに登録するリソースクラスは、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与したメソッドを実装し、`BeanUtil.createAndCopy()` でFormからEntityに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

フォームクラスの作成:

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

リソースクラスの実装:

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

- `@Path` アノテーションでURLマッピングを定義し、`@POST` でPOSTリクエストに対応するメソッドを指定する
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、`BodyConvertHandler` がリクエストボディをJSONとして解釈しFormに変換する
- `@Valid` アノテーションを設定することで、`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED.getStatusCode()`（ステータスコード `201`）を返却する

**注意点**:

- Formのプロパティは全て `String` 型で宣言する（Bean Validationの制約による）
- `BodyConvertHandler` は `ルーティングアダプタ` より後ろ、`JaxRsBeanValidationHandler` は `BodyConvertHandler` より後ろにハンドラキューを設定する必要がある

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4