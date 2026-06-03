Step 4でセクションを読み込みました。回答を生成します。

---

**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドでFormを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` で登録する。

---

**根拠**:

**① フォームクラスの作成**

クライアントから送信された値を受け付けるFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② アクションメソッドの実装**

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

各ポイント:

| アノテーション/API | 役割 |
|---|---|
| `@Path("/projects")` + `@POST` | URLとメソッドのマッピング定義 |
| `@Consumes(MediaType.APPLICATION_JSON)` | JSON形式のリクエストボディを受け付ける |
| `@Valid` | Bean Validationによるバリデーションを実行する |
| `BeanUtil.createAndCopy(Project.class, project)` | FormオブジェクトをEntityに変換する |
| `UniversalDao.insert(...)` | エンティティをDBに登録する |
| `HttpResponse.Status.CREATED.getStatusCode()` | 成功時にステータスコード `201` を返す |

---

**注意点**:
- Formクラスのプロパティは**全てString型**で宣言すること（型変換・バリデーションはフレームワーク側で行われる）
- `@Valid` が設定されたメソッドでバリデーションエラーが発生した場合、後続処理は実行されない

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5

---