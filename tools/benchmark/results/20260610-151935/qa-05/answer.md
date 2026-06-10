**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたメソッドにFormを引数として受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

**フォームクラスの作成**

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

**リソースクラス（アクション）の実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを指定する。
- `@Valid` アノテーションにより、`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する。バリデーションエラー時は `ApplicationException` が送出される。
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する。
- 正常登録時はステータスコード `201 Created` を返す。

**URLマッピング**

`@Path` アノテーションでクラスにベースパスを指定し、`@POST` アノテーションでHTTP POSTリクエストとメソッドをマッピングする。

**注意点**:
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が一致しない場合、ステータスコード `415 Unsupported Media Type` が返される。
- JSON変換には `Jackson2BodyConverter` などのBodyConverterがハンドラ設定で必要になる。
- `@Path` および `@POST` アノテーションによるルーティングは、ルーティングアダプタの設定が必要（`JaxRsPathOptionsProvider` を使用する場合）。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4