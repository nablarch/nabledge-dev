**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドでJSONをフォームクラスとして受け取り、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

処理の流れは次のとおり：

1. **リクエストボディ変換ハンドラ**（`BodyConvertHandler`）がアクションメソッドの `@Consumes` アノテーションを参照し、`Jackson2BodyConverter` がリクエストのJSONをフォームクラスに変換する
2. **Bean Validationハンドラ**（`JaxRsBeanValidationHandler`）が変換後のフォームにバリデーションを実行する（メソッドに `@Valid` が付いている場合）
3. アクションクラスが業務ロジックを実行し、`UniversalDao.insert` でDBに登録する

**フォームクラス**:

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ・セッタ省略
    // ※プロパティは全てString型で宣言する
}
```

**アクションクラス**:

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

**注意点**:
- フォームのプロパティは全て `String` 型で宣言する（Bean Validationの制約）
- `BodyConvertHandler` にはJSONコンバータ（`Jackson2BodyConverter`）の設定が必要。Jerseyアダプタ（`JerseyJaxRsHandlerListFactory`）またはRESTEasyアダプタを使うと自動で設定される
- 対応コンバータが設定されていないMIMEのリクエストを受け取ると、ステータスコード `415`（Unsupported Media Type）が返る

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4