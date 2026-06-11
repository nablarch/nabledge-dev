**結論**: JSONを受け取ってDBに登録するリソースクラスは、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたメソッドでフォームを受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

#### 1. フォームクラスの作成

受け取るJSONをマッピングするフォームを作成する。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. リソースクラスの実装

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

**実装のポイント:**

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONが `ProjectForm` に変換される（リクエストボディ変換ハンドラが処理）
- `@Valid` アノテーションを設定することで、フォームに対してBean Validationが実行される
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをEntityに変換する
- `UniversalDao.insert(entity)` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED.getStatusCode()`（ステータスコード `201`）を返す

#### 3. メソッドシグネチャのバリエーション

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディのJSONをフォームにマッピングして受け取る場合 |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータ、HTTPヘッダを取得したい場合 |
| 組み合わせ | `public HttpResponse save(SampleForm form, JaxRsHttpRequest request)` のように組み合わせ可能 |

**注意点**:

- `@Valid` を使うには、リクエストボディ変換ハンドラよりも後ろに `JaxRsBeanValidationHandler` を設定する必要がある
- `UniversalDao` を使うには、コンポーネント定義に `BasicDaoContextFactory` を `"daoContextFactory"` という名前で設定する必要がある
- フォームのプロパティは全て `String` 型で宣言すること（バリデーションルールの設定方法の制約）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4