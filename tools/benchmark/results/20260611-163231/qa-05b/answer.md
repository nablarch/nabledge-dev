**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid`を付け、引数にFormを受け取って`BeanUtil.createAndCopy()`でEntityに変換し、`UniversalDao.insert()`で登録する。

---

**根拠**:

**① Formクラスの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する

---

**② リソースクラスの実装**

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
| `@Path("/projects")` | URLパスとクラスをマッピング |
| `@POST` | POSTリクエストにこのメソッドをマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | JSONリクエストを受け付ける。リクエストボディ変換ハンドラがJSONをFormに変換する |
| `@Valid` | JaxRsBeanValidationHandlerがFormに対してBean Validationを実行する。バリデーションエラー時はApplicationExceptionを送出し処理を終了 |

処理の流れ:
1. JSONリクエストボディ → `BodyConvertHandler` が `ProjectForm` に変換
2. `@Valid` により `JaxRsBeanValidationHandler` がバリデーション実行
3. `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換
4. `UniversalDao.insert()` でDB登録
5. ステータスコード `201 Created` を返却

---

**注意点**:

- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）**より後ろ**にハンドラキューに設定すること（FormへのBody変換が終わった後にバリデーションを行うため）
- Jakarta RESTful Web Services標準の `@PathParam` アノテーションは**使用できない**。パスパラメータの取得には `JaxRsHttpRequest#getPathParam()` を使用すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8