**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、Formクラスを作成し、アクションメソッドで `@Valid` + `UniversalDao.insert()` を使う実装パターンが標準です。

**根拠**:

**1. Formクラスの作成**

クライアントから送信されたJSONを受け付けるFormクラスを定義します。プロパティは**全てString型**で宣言します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONが `ProjectForm` に変換される
- `@Valid` アノテーションによりFormのバリデーションが実行される（バリデーションエラー時は自動的にエラーレスポンスが返る）
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値として `HttpResponse` にステータスコード `201`（Created）を設定して返す
- `@Path` と `@POST` でPOSTリクエスト時のURLマッピングを定義する

**注意点**:
- Formのプロパティは全てString型で宣言する必要があります
- Jakarta RESTful Web Servicesで規定されている `@QueryParam` や `@PathParam` は使用できません（NablarchではJaxRsHttpRequestから取得します）
- `@Consumes` に設定されたMIMEとリクエストの `Content-Type` が異なる場合、ステータスコード `415` が返却されます

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-body-convert-handler.json:s5