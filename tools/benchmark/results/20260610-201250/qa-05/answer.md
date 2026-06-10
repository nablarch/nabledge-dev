**結論**: リソースクラスに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与したメソッドを定義し、引数のフォームを `BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` でDB登録する。

**根拠**:

**1. フォームクラスの作成**

JSONのリクエストボディを受け取るフォームを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソース（アクション）クラスの実装**

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

- `@Path` アノテーションでクラスにURLパスを、`@POST` でHTTPメソッドをマッピングする
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、`BodyConvertHandler` がリクエストボディをJSONとしてフォームに変換する
- `@Valid` を指定すると `JaxRsBeanValidationHandler` がフォームのBean Validationを実行し、エラー時は後続処理に委譲せず `ApplicationException` を送出する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED`（ステータスコード `201`）を返す

**3. メソッドシグネチャの選択肢**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディ（JSON）を受け取る場合 |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータ・HTTPヘッダが必要な場合 |
| 組み合わせ | 両方必要な場合は `save(SampleForm form, JaxRsHttpRequest request)` |

**注意点**:

- `BodyConvertHandler` の `bodyConverters` プロパティに、使用するMIMEタイプに対応した `BodyConverter` を設定すること。設定されていないMIMEタイプのリクエストが来た場合はステータスコード `415` が返却される
- `UniversalDao` を使用するには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要:
  ```xml
  <component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
  ```

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8