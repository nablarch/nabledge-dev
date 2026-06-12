**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラスを作成し、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与して、`UniversalDao.insert()` でDB登録します。

**根拠**:

**① フォームクラスの作成**

JSONリクエストを受け取るフォームを作成します。プロパティは全て `String` 型で宣言します。

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONが自動的にフォームに変換される（リクエストボディ変換ハンドラが処理）
- `@Valid` を付与することで、フォームに対してBean Validationが実行される。バリデーションエラー時は `ApplicationException` がスローされる
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値として `201 Created` を表す `HttpResponse` を返す

**③ URLマッピング（ルーティングアダプタを使用）**

`@Path` と `@POST` アノテーションでPOSTリクエストとメソッドのマッピングを定義します。

**注意点**:
- フォームのプロパティは全て `String` 型で宣言すること（バリデーション後に型変換が行われる）
- `@Consumes` に設定したMIMEと異なる `Content-Type` でリクエストが来た場合、ステータスコード `415`（Unsupported Media Type）が返却される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4