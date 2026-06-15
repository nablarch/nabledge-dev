**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたアクションメソッドでFormを受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**1. フォームクラスの作成**

JSONのリクエストボディを受け付けるFormを作成する。プロパティは全て`String`型で宣言し、バリデーションアノテーションを付ける。

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // その他のフィールド、ゲッタ/セッタは省略
}
```

**2. 業務アクションメソッドの実装**

`@Path` でURLを、`@POST` でHTTPメソッドを指定し、`@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言する。

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

- `@Valid` アノテーションでBean Validationを有効化する
- `BeanUtil.createAndCopy()` でFormからEntityに変換してから`UniversalDao.insert()`に渡す
- 登録成功時はステータスコード `201` を返す

**3. JSON変換の設定（Jersey環境の場合）**

`BodyConvertHandler` がリクエストボディをFormに変換する。Jersey環境では `JerseyJaxRsHandlerListFactory` を設定することで `Jackson2BodyConverter` が自動的に組み込まれ、JSON変換が可能になる。

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

**4. ユニバーサルDAOの設定**

コンポーネント定義に以下を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `Content-Type: application/json` を設定しないリクエストにはステータスコード `415`（Unsupported Media Type）が返される
- `UniversalDao.insert()` にはEntityを渡すため、`BeanUtil.createAndCopy()` でFormからEntityへの変換が必要
- `@Valid` アノテーションによりバリデーションが実行され、エラー時はフレームワークが自動でエラーレスポンスを返す

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6