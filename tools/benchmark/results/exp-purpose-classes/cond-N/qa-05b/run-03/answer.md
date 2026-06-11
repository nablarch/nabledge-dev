**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)` アノテーションを付けたリソースクラスを実装し、引数にFormクラスを受け取って `BeanUtil` でエンティティに変換後 `UniversalDao.insert()` でDBに登録する。

---

**根拠**:

**① Formクラスの作成**

JSONの各フィールドを受け取るFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

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

各アノテーションの役割:

| アノテーション | 役割 |
|---|---|
| `@Path("/projects")` | URLとリソースクラスをマッピングする |
| `@POST` | POSTリクエスト時にこのメソッドを呼び出す |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして受け付ける。`リクエストボディ変換ハンドラ`がFormクラスへの変換を行う |
| `@Valid` | `Jakarta RESTful Web Servcies Bean Validationハンドラ`がFormに対しBean Validationを実行する |

**③ リソースクラスのメソッドシグネチャ（引数・戻り値のパターン）**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディをFormとして受け取る場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ | 例: `save(ProjectForm form, JaxRsHttpRequest request)` |

| 戻り値の型 | 説明 |
|---|---|
| `HttpResponse` | ステータスコードなどを明示的に返す場合 |
| フォーム(Java Beans) | レスポンスボディにJSONを返す場合（`@Produces`と組み合わせる）|
| `void` | `204 NoContent` を返す場合 |

---

**注意点**:
- Jakarta RESTful Web Servicesの `@PathParam` / `@QueryParam` は使用できない。パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得すること。
- `@Consumes`に設定されたMIMEとリクエストのContent-Typeが異なる場合、ステータスコード `415` が返される。
- FormクラスのプロパティはString型で宣言し、エンティティへの変換は `BeanUtil.createAndCopy()` で行う。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4