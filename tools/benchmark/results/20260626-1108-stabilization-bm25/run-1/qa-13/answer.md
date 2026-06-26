**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、フォームクラスを作成し、リソース（アクション）クラスで `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を組み合わせたメソッドを実装して、`BeanUtil.createAndCopy` でフォームをエンティティに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

**① フォームクラスの作成**

クライアントから送信されたJSON値を受け付けるフォームを作成する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② 業務アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` アノテーションでリクエストのバリデーションを実行する（Jakarta RESTful Web Services Bean Validationハンドラが処理）
- `BeanUtil.createAndCopy` でフォームをエンティティクラスに変換する
- `UniversalDao.insert` でエンティティをDBに登録する
- 戻り値にはリソース作成完了（ステータスコード `201`）を表す `HttpResponse` を返却する
- `@Path` + `@POST` でURLとのマッピングを定義する

**注意点**:

- フォームのプロパティは**全てString型**で宣言する（バリデーション・型変換の都合上）
- バリデーションエラー時のレスポンスはJakarta RESTful Web Services Bean Validationハンドラが自動で返却する

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4