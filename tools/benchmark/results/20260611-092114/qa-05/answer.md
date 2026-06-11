**結論**: リソースクラスでJSONを受け取ってDBに登録するには、`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与したメソッドを定義し、フォームクラスを引数にとって `BeanUtil.createAndCopy` でエンティティ変換後、`UniversalDao.insert` で登録します。

---

**根拠**:

**1. フォームクラスの作成**

クライアントから受け取る値を保持するフォームクラスを作成します。プロパティは**全てString型**で宣言します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラスのメソッド実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストボディをフォームに自動変換する指定。`BodyConvertHandler` がこのアノテーションを元に変換処理を行います。
- `@Valid`: Bean Validationによるバリデーションを有効化。`JaxRsBeanValidationHandler` が実行します。
- `BeanUtil.createAndCopy(Project.class, project)`: フォームをエンティティクラスに変換します。
- `UniversalDao.insert(...)`: エンティティをDBに登録します。
- 戻り値: `HttpResponse` にステータスコード `201` (Created) を指定して返します。

**3. メソッドシグネチャのルール**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディからの変換結果を受け取る |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得したい場合 |
| `ExecutionContext` | スコープ変数にアクセスしたい場合 |
| 組み合わせ | 例: `save(SampleForm form, JaxRsHttpRequest request)` |

---

**注意点**:
- フォームクラスのプロパティは**全てString型**で宣言すること（型変換はバリデーション時に行われる）
- `@Consumes` に指定したMIMEタイプとリクエストのContent-Typeが異なる場合は、ステータスコード `415` (Unsupported Media Type) が返却される

---

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5