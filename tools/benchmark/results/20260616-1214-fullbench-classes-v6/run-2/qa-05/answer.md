**結論**: REST APIでJSONを受け取りDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`UniversalDao.insert()` でエンティティを保存します。

**根拠**:

**1. フォームクラスを作成する**

クライアントから受け取るJSONをマッピングするフォームを作成します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // その他プロパティ（全てString型で宣言すること）
    // ゲッタ及びセッタは省略
}
```

**2. アクションクラスを実装する**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONがフォームに変換される
- `@Valid` を指定することで、Bean Validationによるバリデーションが実行される（エラー時は `ApplicationException` が送出される）
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録する
- レスポンスとして登録完了（ステータスコード `201`）を返す

**3. コンポーネント設定（Jersey環境の場合）**

JSONのボディ変換には `Jackson2BodyConverter` が必要です。Jersey環境では以下の設定で自動的に構成されます。

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- Jerseyのハンドラキューを設定するとJackson2BodyConverter等が自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
  ...
</component>
```

**4. ユニバーサルDAOの設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームのプロパティは全て `String` 型で宣言すること
- `@Consumes` に設定したMIMEと異なる `Content-Type` がリクエストに含まれる場合、ステータスコード `415` が返される
- `UniversalDao.insert()` に渡すのはフォームではなくエンティティクラスであるため、`BeanUtil.createAndCopy()` での変換が必要

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6, adapters-jaxrs-adaptor.json:s2