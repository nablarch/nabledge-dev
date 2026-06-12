**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたアクションメソッドに `ProjectForm` などのフォームクラスを引数として受け取り、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDB登録する。

**根拠**:

**1. フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```
- プロパティは全て `String` 型で宣言する。

**2. アクションクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディが JSON として受け付けられ、`BodyConvertHandler` がフォームへ変換する。
- `@Valid` アノテーションにより、`JaxRsBeanValidationHandler` がフォームのバリデーションを実行する。
- `BeanUtil.createAndCopy` でフォームをエンティティに変換し、`UniversalDao.insert` でDB登録する。
- 成功時はステータスコード `201`（Created）を返す。

**3. URL マッピングの設定**

`@Path("/projects")` アノテーションをクラスに、`@POST` アノテーションをメソッドに付与することで、POSTリクエストに対するマッピングが定義される。ディスパッチハンドラには `PathOptionsProviderRoutesMapping` を使用する構成が必要。

**注意点**:
- `BodyConvertHandler` の設定で `application/json` に対応したコンバータ（例: Jackson連携）を設定しておく必要がある。設定がない場合、ステータスコード `415`（Unsupported Media Type）が返却される。
- `BodyConvertHandler` はハンドラキューで `ルーティングアダプタ` より後ろ、`JaxRsBeanValidationHandler` はその後ろに設定すること。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-router-adaptor.json:s8