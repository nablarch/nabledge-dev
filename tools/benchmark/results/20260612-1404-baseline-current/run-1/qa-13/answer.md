**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、①フォームクラスを作成し、②業務アクションに `@Valid` + `UniversalDao.insert()` を実装し、③`@Path`/`@POST` でURLマッピングを定義する3ステップで実現できる。

**根拠**:

**① フォームクラスの作成**

クライアントから受け取る値をフォームクラスで定義する。プロパティは**全てString型**で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② 業務アクションメソッドの実装**

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

各ポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` — JSONリクエストボディをフォームに変換する
- `@Valid` — バリデーションを実行する（`JaxRsBeanValidationHandler` が処理）
- `BeanUtil.createAndCopy(Project.class, project)` — フォームをエンティティに変換する
- `UniversalDao.insert(entity)` — エンティティをDBに登録する
- ステータスコード `201`（Created）を返す

**③ URLマッピング**

`@Path` と `@POST` アノテーションで、POSTリクエスト時のURLと業務アクションを紐づける。

**注意点**:
- ユニバーサルDAOを使用するには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

- サロゲートキー（ID自動採番）が必要な場合は、エンティティに `@GeneratedValue` アノテーションを付与する。
- フォームのプロパティは全てString型で宣言すること（バリデーションの仕様上の制約）。

参照: restful-web-service-getting-started-create.json:s1, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/libraries/libraries-universal-dao.json:s6, component/libraries/libraries-bean-util.json:s2