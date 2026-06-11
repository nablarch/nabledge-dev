**結論**: `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` をリソースクラスのメソッドに付与し、`BeanUtil.createAndCopy()` でFormをEntityに変換して `UniversalDao.insert()` でDBに登録する。

**根拠**:

**1. Formクラスの作成**

クライアントから送信されたJSON値を受け付けるFormを作成する。プロパティは**全てString型**で宣言する。

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

| アノテーション | 役割 |
|---|---|
| `@Path("/projects")` | URLとクラスのマッピングを定義 |
| `@POST` | POSTリクエスト時にこのメソッドを呼び出す |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして受け付ける。`BodyConvertHandler` がこのアノテーションを参照してFormへ変換する |
| `@Valid` | `JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する |

**3. 変換とDB登録**

- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityクラスにコピー変換
- `UniversalDao.insert(...)`: ユニバーサルDAOでDBに挿入
- 戻り値: ステータスコード `201 (CREATED)` を返す `HttpResponse`

**注意点**:
- Formのプロパティは全てString型で宣言すること（バリデーションルールの要件）
- ハンドラキューに `BodyConvertHandler`（リクエストボディ変換）と `JaxRsBeanValidationHandler`（バリデーション）を設定する必要がある。後者は前者より後ろに配置すること
- `@Valid` によるバリデーションエラー時は `ApplicationException` が送出され、後続処理は実行されない

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4