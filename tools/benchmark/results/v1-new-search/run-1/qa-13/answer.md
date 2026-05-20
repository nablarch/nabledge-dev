**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`ProjectForm` のような Formクラスを定義し、`@Valid` アノテーション付きアクションメソッドで `BeanUtil.createAndCopy()` を使ってエンティティに変換後、`UniversalDao.insert()` で登録します。

**根拠**:

**1. Formクラスの作成**

クライアントから受け取る値をマップするFormクラスを作成します。プロパティはすべて `String` 型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

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

実装のポイント:

- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストをJSON形式で受け付ける
- `@Valid` アノテーションを設定すると、`JaxRsBeanValidationHandler` が FormのBean Validationを実行する（バリデーションエラー時は `ApplicationException` を送出）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録
- 戻り値はリソース作成完了（ステータスコード `201`）を表す `HttpResponse` を返却

**3. URLマッピング**

`@Path` アノテーションと `@POST` アノテーションを組み合わせて、POSTリクエスト時のマッピングを定義します（ルーティングアダプタ使用）。

**注意点**:
- Formのプロパティは全て `String` 型で宣言すること（Bean Validationの仕様）
- `UniversalDao` を使用するには、`BasicDaoContextFactory` のコンポーネント定義設定が必要

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6