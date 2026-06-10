**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`@Valid`アノテーションでバリデーション済みのFormを`BeanUtil.createAndCopy`でEntityに変換し、`UniversalDao.insert`で登録する。レスポンスはステータスコード201（Created）の`HttpResponse`を返す。

**根拠**:

フォームクラスの作成:

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全てString型で宣言する

業務アクションメソッドの実装:

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

1. **JSONリクエスト受付**: `@Consumes(MediaType.APPLICATION_JSON)` を指定してJSONボディを受け付ける
2. **バリデーション**: `@Valid` アノテーションを設定すると、`JaxRsBeanValidationHandler`がリクエスト受信時に自動でBean Validationを実行する
3. **Entity変換**: `BeanUtil.createAndCopy(Project.class, project)` でフォームをEntityに変換する
4. **DB登録**: `UniversalDao.insert` でEntityをDBに登録する
5. **URLマッピング**: `@Path` と `@POST` アノテーションでPOSTリクエストのURLマッピングを定義する

**注意点**:
- フォームのプロパティは全てString型で宣言すること。不正な値が送信された場合のBean変換失敗を防ぐため
- RESTfulウェブサービスで楽観的ロックを使う場合、`ETag`/`If-Match`には対応していない。バージョン番号はリクエストボディに直接含めること

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/libraries/libraries-bean-validation.json:s17