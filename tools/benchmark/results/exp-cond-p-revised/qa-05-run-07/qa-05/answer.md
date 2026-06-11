**結論**: アクションクラスのメソッドに `@POST`、`@Consumes(MediaType.APPLICATION_JSON)`、`@Valid` を付与し、`BeanUtil.createAndCopy` でFormをEntityに変換して `UniversalDao.insert` でDB登録する。レスポンスはステータスコード `201` の `HttpResponse` を返却する。

**根拠**:

**1. Formクラスの作成**

受け取るJSONのフィールドに対応するFormを作成する。プロパティはすべて `String` 型で宣言すること。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストボディをJSONとして受け付ける。リクエストの `Content-Type` がマッチしない場合は 415 を返す
- `@Valid` — リクエストのバリデーションを実行する（Jakarta RESTful Web Services Bean Validationハンドラが処理する）
- `BeanUtil.createAndCopy(Project.class, project)` — FormをEntityに変換する
- `UniversalDao.insert(...)` — EntityをDBに登録する
- `HttpResponse.Status.CREATED.getStatusCode()` — ステータスコード `201` を返却する

**3. JSON変換設定（コンポーネント定義）**

JSONの変換にはJersey（またはRESTEasy）用アダプタを使用する。Jersey環境では以下のように `JerseyJaxRsHandlerListFactory` を設定すると、JSONコンバータとして `Jackson2BodyConverter` が自動的に設定される。

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

**4. UniversalDAO設定**

コンポーネント定義に `BasicDaoContextFactory` を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティはすべて `String` 型で宣言すること。String以外の型に不正な値が送信された場合、バリデーション前の変換処理が失敗し、予期せぬ例外が発生する
- バリデーションエラー発生時は `ApplicationException` が送出され、後続の処理は実行されない

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, libraries-bean-validation.json:s8