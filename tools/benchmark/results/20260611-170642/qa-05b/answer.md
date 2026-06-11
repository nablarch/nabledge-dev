**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、引数にフォームBeanを受け取って `UniversalDao.insert` でDB登録する。

**根拠**:

リソースクラスの実装例（`ProjectAction.java`）:

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

フォームクラス（`ProjectForm.java`）:

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

各要素の役割:

| 要素 | 役割 |
|------|------|
| `@Path` + `@POST` | URLとHTTPメソッドのマッピング定義 |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして受け付ける。BodyConvertHandlerがJSONをフォームBeanに変換する |
| フォームBean引数 | リクエストボディから変換されたBeanを受け取る |
| `@Valid` | JaxRsBeanValidationHandlerがフォームに対してBean Validationを実行。エラー時は`ApplicationException`を送出 |
| `BeanUtil.createAndCopy` | フォームをEntityに変換 |
| `UniversalDao.insert` | EntityをDBに登録 |
| `HttpResponse(201)` | リソース作成完了（201 Created）をクライアントに返却 |

メソッド引数のパターン（用途に応じて組み合わせ可能）:

| 引数 | 用途 |
|------|------|
| フォーム(Java Beans) | リクエストボディ変換が必要な場合 |
| `JaxRsHttpRequest` | パス/クエリパラメータやHTTPヘッダ取得が必要な場合 |
| `ExecutionContext` | スコープ変数にアクセスしたい場合 |

メソッド戻り値のパターン:

| 戻り値型 | 動作 |
|----------|------|
| `void` | 204 No Content をクライアントに返却 |
| フォーム(Java Beans) | BodyConvertHandlerでレスポンスボディに変換して返却 |
| `HttpResponse` | ステータスコード・ヘッダを指定してクライアントに返却 |

**注意点**:
- フォームのプロパティは**全てString型**で宣言する
- `JaxRsBeanValidationHandler`（`@Valid`）はBodyConvertHandlerの後に設定する必要がある（BodyConvertHandlerがフォームに変換した後にバリデーションを実行するため）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-body-convert-handler.json:s5