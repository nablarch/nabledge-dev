**結論**: リソースクラスに `@Path`/`@POST`/`@Consumes(APPLICATION_JSON)`/`@Valid` を付与したメソッドを定義し、受け取ったFormを `BeanUtil.createAndCopy()` でEntityに変換して `UniversalDao.insert()` でDBに登録する。

**根拠**:

**①フォームクラスの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> プロパティは全てString型で宣言する。

**②リソースクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストボディをJSON形式として受け付ける。BodyConvertHandlerがこのアノテーションを参照し、対応するBodyConverterでFormに変換する
- `@Valid` — JaxRsBeanValidationHandlerがこのアノテーションを見てFormに対するバリデーションを実行する
- `BeanUtil.createAndCopy(Project.class, project)` — FormをEntityに変換する
- `UniversalDao.insert()` — EntityをDBに登録する（SQLを書かずにCRUDが可能）
- 戻り値に `HttpResponse.Status.CREATED.getStatusCode()` (201) を指定してリソース作成完了を返す

**メソッド引数の選択肢**（必要に応じて組み合わせ可能）:

| 引数型 | 用途 |
|--------|------|
| フォーム(Java Beans) | リクエストボディから変換した値を処理する場合 |
| JaxRsHttpRequest | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| ExecutionContext | ExecutionContextのスコープ変数にアクセスする場合 |

**注意点**:
- Formのプロパティは全てString型で宣言する（Bean Validationの要件）
- サロゲートキーを自動採番する場合はEntityの`@Id`フィールドに `@GeneratedValue` を付与する（`GenerationType.AUTO`/`SEQUENCE`/`IDENTITY`/`TABLE` に対応）

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8, restful-web-service-resource-signature.json:s1, libraries-universal-dao.json:s2