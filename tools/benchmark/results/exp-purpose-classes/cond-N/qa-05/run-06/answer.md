**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、①Formクラスの作成、②`@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付けたアクションメソッドの実装、③`@Path` / `@POST` アノテーションによるURLマッピングの3ステップで実装する。

**根拠**:

**① Formクラスの作成**

リクエストボディのJSONをマッピングするFormクラスを作成する。プロパティは全て `String` 型で宣言し、Bean Validationアノテーションでバリデーションルールを定義する。

```java
public class ProjectForm implements Serializable {

    // 一部のみ抜粋

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> ポイント: プロパティは全て `String` 型で宣言する。

**② アクションメソッドの実装**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(ProjectForm project) {
    UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
    return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
}
```

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディをJSON形式で受け付けることを指定。リクエストボディ変換ハンドラがこのアノテーションを見てFormに変換する。
- `@Valid`: JaxRs Bean Validationハンドラが、メソッドが受け取るFormに対してBean Validationを実行する。
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する。
- `UniversalDao.insert(...)`: DBへの登録を実行する。
- 戻り値は `201 Created` を表す `HttpResponse` を返す。

**③ URLマッピングの定義**

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

- クラスに `@Path` アノテーションでURLプレフィックスを定義する。
- メソッドに `@POST` アノテーションでHTTPメソッドとのマッピングを定義する。
- `@Path` アノテーションによるルーティングを使用するには、ルーティングアダプタの設定で `PathOptionsProviderRoutesMapping` を使用する必要がある。

**注意点**:
- `@Consumes` に指定したMIMEタイプと、リクエストヘッダの `Content-Type` が異なる場合、ステータスコード `415` が返却される。
- `@Valid` はリクエストボディ変換ハンドラよりも後ろに設定されたJaxRs Bean Validationハンドラが処理するため、ハンドラキューの設定順に注意すること。
- `@Path` アノテーションによるルーティングは、JBossやWildflyなど独自のファイルシステムを使用するAPサーバでは使用できないため、その場合はXMLによるルート定義ファイルを使用すること。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-resource-signature.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-router-adaptor.json:s8