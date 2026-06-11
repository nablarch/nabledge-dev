**結論**: フォームクラスを引数に取るメソッドに `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付与し、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` でDB登録するパターンを使う。

**根拠**:

**1. フォームクラスの作成**

リクエストボディのJSONをマッピングするフォームクラスを作成する。プロパティは全てString型で宣言する。

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

各アノテーション・APIの役割:

| 要素 | 役割 |
|------|------|
| `@Path("/projects")` | クラスにURLパスをマッピング |
| `@POST` | POSTリクエスト時にこのメソッドをマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストをJSON形式で受け付ける |
| `@Valid` | Bean ValidationによるフォームのバリデーションをBean Validationハンドラが実行 |
| `ProjectForm`（引数） | リクエストボディからフォームへの変換は自動で行われる |
| `BeanUtil.createAndCopy()` | フォームからエンティティクラスに値をコピーして変換 |
| `UniversalDao.insert()` | エンティティをDBに登録 |
| `HttpResponse.Status.CREATED` | 登録完了のレスポンス（ステータスコード201）を返却 |

**注意点**:
- フォームクラスのプロパティは全てString型で宣言する（Bean Validationの仕様による）
- `@Path`/`@POST` などのアノテーションによるURLマッピングはルーティングアダプタを使用する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1