**結論**: `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーションをリソースメソッドに付け、`BeanUtil.createAndCopy` でフォームをエンティティに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

フォームクラスを作成する（プロパティはすべて `String` 型）:

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

リソース（アクション）クラスにルーティングとメソッドを実装する:

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

**各ポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラがJSONをフォームに変換する
- `@Valid` アノテーションにより、Bean Validationハンドラがリクエストのバリデーションを実行する（エラー時は `ApplicationException` が送出される）
- `BeanUtil.createAndCopy` でフォームをエンティティに変換し、`UniversalDao.insert` でDB登録する
- 戻り値は 201 (Created) を表す `HttpResponse` を返す

コンポーネント定義でユニバーサルDAOの設定が必要:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `@Valid` を使うには `JaxRsBeanValidationHandler` がハンドラキューに設定されている必要があり、このハンドラはリクエストボディ変換ハンドラよりも後ろに設定すること
- `BodyConvertHandler` の `bodyConverters` プロパティにJSONに対応したコンバータが設定されていること（ブランクプロジェクトでは設定済み）

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/libraries/libraries-universal-dao.json:s6