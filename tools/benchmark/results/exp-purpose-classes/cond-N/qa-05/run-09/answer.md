**結論**: JSONを受け取ってDBに登録するには、Formクラスを引数に取るメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`UniversalDao.insert()` でDB登録、`HttpResponse(201)` を返す。URLとのマッピングはクラスに `@Path`、メソッドに `@POST` を付与して定義する。

**根拠**:

**①フォームクラスの作成**

リクエストボディの値を受け付けるFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**②業務アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストボディをJSON形式として受け付ける。これにより、リクエストボディ変換ハンドラがFormへの変換処理を行う
- `@Valid` でBean Validationによるバリデーションを実行する
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録する
- ステータスコード `201 Created` を表す `HttpResponse` を返す

**③メソッド引数・戻り値の選択肢**

| 引数 | 用途 |
|------|------|
| フォーム(Java Beans) | リクエストボディをFormとして受け取る場合 |
| JaxRsHttpRequest | パスパラメータ・クエリパラメータが必要な場合 |
| 組み合わせ | 両方必要な場合（例: `save(ProjectForm form, JaxRsHttpRequest req)`） |

| 戻り値 | 説明 |
|--------|------|
| `HttpResponse` | ステータスコード等を個別に指定する場合 |
| void | 204 No Content を返す場合 |
| フォーム(Java Beans) | レスポンスボディにオブジェクトをJSON変換して返す場合 |

**注意点**:
- Formのプロパティは全てString型で宣言すること
- `@Path` アノテーションによるルーティングを使用する場合、`RoutesMapping` ではなく `PathOptionsProviderRoutesMapping` をディスパッチハンドラに設定する必要がある
- Jakarta RESTful Web Servicesの `@PathParam` アノテーションは使用できない。パスパラメータは `JaxRsHttpRequest#getPathParam()` で取得すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, adapters-router-adaptor.json:s8