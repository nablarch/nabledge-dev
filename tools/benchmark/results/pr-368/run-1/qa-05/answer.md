**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたメソッドでフォームを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**① フォームクラスの作成**

クライアントから送信された値を受け付けるフォームを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスのメソッド実装**

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
- `@Path` アノテーションと `@POST` アノテーションでPOSTリクエスト時のURLマッピングを定義する
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディが `ProjectForm` に自動変換される
- `@Valid` アノテーションを付けることで、フォームに対してBean Validationが実行される
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED.getStatusCode()` を使ってステータスコード `201` を返す

**③ メソッドシグネチャのバリエーション**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディから変換したフォームで処理する場合 |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータ、HTTPヘッダを取得する場合 |
| 組み合わせ | `(SampleForm form, JaxRsHttpRequest request)` のように組み合わせも可能 |

**注意点**:
- `@Consumes` に設定したMIMEタイプと、リクエストヘッダの `Content-Type` が一致しない場合、415（サポートしていないメディアタイプ）が返却される
- フォームのプロパティは全てString型で宣言すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4