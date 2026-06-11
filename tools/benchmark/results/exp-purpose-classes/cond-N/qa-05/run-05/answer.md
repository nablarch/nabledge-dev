**結論**: REST APIでJSONを受け取ってDBに登録するには、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーションをリソースクラスのメソッドに付与し、引数にFormクラスを受け取って `UniversalDao.insert()` でDB登録するパターンを使用します。

**根拠**:

**1. Formクラスの作成**

クライアントから受け取るJSONの各フィールドに対応するFormクラスを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

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

各アノテーションの役割:
- `@Path("/projects")`: クラスにURLパスをマッピング（ルーティングアダプタによる設定でも可）
- `@POST`: HTTPメソッドをPOSTにマッピング
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディをJSON (`application/json`) として受け取ることを指定。リクエストボディ変換ハンドラがこのアノテーションを見てJSONをFormに変換する
- `@Valid`: Jakarta RESTful Web Services Bean ValidationハンドラによるBean Validationを実行。バリデーションエラー時はApplicationExceptionが送出される
- `BeanUtil.createAndCopy(Project.class, project)`: FormからEntityへ変換
- `UniversalDao.insert(...)`: DBへの登録
- 戻り値の `HttpResponse(201)`: リソース作成完了 (Created) を返却

**3. メソッドシグネチャのバリエーション**

| 引数の型 | 用途 |
|---|---|
| Form (Java Beans) | リクエストボディのJSONを変換して受け取る場合 |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータ、HTTPヘッダを取得したい場合 |
| 組み合わせ | Form + JaxRsHttpRequest の両方が必要な場合 |

**注意点**:
- `Content-Type: application/json` でリクエストを送らないと、ステータスコード `415` (サポートしていないメディアタイプ) が返却される
- Formのプロパティは全てString型で宣言すること（Bean Validationのルール）
- ルーティングアダプタの設定が必要（`@Path` アノテーションによるマッピング、または routes定義ファイル）

参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1`, `processing-pattern/restful-web-service/restful-web-service-resource-signature.json:s1`, `component/handlers/handlers-body-convert-handler.json:s5`, `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`