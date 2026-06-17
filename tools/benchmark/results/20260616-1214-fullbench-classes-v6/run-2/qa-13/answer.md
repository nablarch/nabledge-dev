**結論**

フォームデータをDBに登録するには、Formクラスを作成してアクションメソッドで受け取り、`BeanUtil.createAndCopy` でエンティティに変換した上で `UniversalDao.insert` でDB登録する。レスポンスとして `HttpResponse.Status.CREATED`（ステータスコード 201）を返す。

**根拠**

**Formクラスの実装**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**アクションクラスの実装**

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
- `@Path("/projects")` + `@POST` — URLとHTTPメソッドのマッピングを定義
- `@Consumes(MediaType.APPLICATION_JSON)` — JSONリクエストボディをFormに変換するよう指示
- `@Valid` — リクエストボディ変換後にBean Validationを実行
- `BeanUtil.createAndCopy(Project.class, project)` — FormをエンティティBeanに変換
- `UniversalDao.insert(entity)` — エンティティをDBに登録

**注意点**

- Formクラスのプロパティは**必ずString型**で宣言する。String以外の型があると、不正な値が送信された際にBeanへの変換処理が失敗して予期せぬ例外が発生する（バリデーション前に障害となる）。
- `@Valid` が機能するには `JaxRsBeanValidationHandler` が `BodyConvertHandler` より後ろにハンドラキューに設定されている必要がある。Jersey/RESTEasyアダプタ（`JerseyJaxRsHandlerListFactory` 等）を使用している場合は自動的に正しい順序で設定される。

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-bean-validation-handler.json:s3, libraries-bean-validation.json:s8, adapters-jaxrs-adaptor.json:s2