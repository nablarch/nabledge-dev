十分な情報が得られました。回答を生成します。

---

**結論**: RESTfulウェブサービスでDB登録を実装するには、FormクラスにBean Validationアノテーションを付け、アクションメソッドで `@Valid` によるバリデーション → `BeanUtil.createAndCopy()` でForm→Entity変換 → `UniversalDao.insert()` でDB登録という3ステップのパターンを使います。

**根拠**:

**1. Formクラスの作成**（クライアントから受け取るリクエストをマッピング）

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> プロパティは全てString型で宣言する。

**2. 業務アクションメソッドの実装**

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
| `@Path("/projects")` + `@POST` | URLとメソッドのマッピング（POSTリクエストにバインド） |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSON形式で受け付ける |
| `@Valid` | `JaxRsBeanValidationHandler` がFormに対してBean Validationを実行。エラー時は `ApplicationException` を送出 |
| `BeanUtil.createAndCopy(Project.class, project)` | FormをEntityに変換（同名プロパティをコピー、型変換あり） |
| `UniversalDao.insert(entity)` | EntityをDBに登録 |
| `HttpResponse.Status.CREATED.getStatusCode()` | ステータスコード201（作成完了）をレスポンスとして返却 |

**注意点**:

- `JaxRsBeanValidationHandler` は、ハンドラ設定においてリクエストボディ変換ハンドラ（`BodyConvertHandler`）より後ろに配置すること。バリデーションは変換済みのFormに対して行われるため。
- `UniversalDao` を使用するには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-bean-validation-handler.json:s3, libraries-universal-dao.json:s6

---