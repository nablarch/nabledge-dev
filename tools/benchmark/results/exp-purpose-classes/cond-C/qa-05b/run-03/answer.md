**結論**: NablarchのRESTfulウェブサービスでJSONを受け取りDBに登録するには、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付けたリソースメソッドに Formクラスを引数として定義し、`BeanUtil.createAndCopy` でエンティティに変換してから `UniversalDao.insert` でDBに登録する。

**根拠**:

**① Formクラスの作成**（入力値の受け口）

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // その他フィールド、ゲッタ/セッタは省略
}
```

- プロパティは全て `String` 型で宣言する

**② リソースクラスのメソッド実装**

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

- `@Path` + `@POST` でURLとのマッピングを定義する
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、`BodyConvertHandler` がリクエストボディの JSON を `ProjectForm` に変換する
- `@Valid` を指定すると `JaxRsBeanValidationHandler` がバリデーションを実行する
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換し、`UniversalDao.insert` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED`（ステータスコード `201`）を返す

**③ BodyConvertHandler の動作**

リクエストヘッダの `Content-Type` が `@Consumes` に指定したMIMEと一致しない場合、ステータスコード `415` (Unsupported Media Type) が返される。

**注意点**:
- `@Valid` によるバリデーションエラー時のレスポンスは `JaxRsBeanValidationHandler` が生成する
- `UniversalDao.insert` はエンティティクラスを引数に取るため、`BeanUtil.createAndCopy` によるフォーム→エンティティ変換が必須

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5