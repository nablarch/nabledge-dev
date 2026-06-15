**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドでJSON付きのFormを受け取り、`BeanUtil` でEntityに変換して `UniversalDao.insert()` でDBに登録する。

**根拠**:

**1. フォームクラスを作成する**

JSONリクエストボディを受け取るFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. 業務アクションメソッドを実装する**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定して、JSONリクエストを受け付けることを宣言する
- `@Valid` アノテーションでフォームに対するBean Validationを実行する（バリデーションエラー時は `ApplicationException` がスローされる）
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換する
- `UniversalDao.insert()` でDBに登録する
- レスポンスとしてステータスコード `201`（リソース作成完了）を返す

**3. JSONコンバータの設定（Jakarta RESTful Web Servicesアダプタ）**

JSONの変換には `Jackson2BodyConverter` が使用される。Jersey環境の場合は `JerseyJaxRsHandlerListFactory` を設定することで自動的に有効になる。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**注意点**:
- `Content-Type` が `application/json` 以外のリクエストが来た場合、ステータスコード `415`（サポートしていないメディアタイプ）が返却される
- `@Valid` を付けたメソッドへのリクエストでバリデーションエラーが発生した場合、後続のDB登録処理には進まず `ApplicationException` がスローされる

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2