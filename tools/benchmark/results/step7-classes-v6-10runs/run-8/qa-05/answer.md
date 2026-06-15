**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドを作成し、`BeanUtil.createAndCopy` でフォームをエンティティに変換して `UniversalDao.insert` でDBに登録する。

**根拠**:

**1. Formクラスの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で宣言する

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

- `@Path` でURLをマッピング、`@POST` でPOSTリクエストに対応
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONがFormクラスへ変換される
- `@Valid` を付けるとBean Validationによる入力チェックが実行される（エラー時は `ApplicationException` がスローされる）
- `BeanUtil.createAndCopy` でFormからエンティティに変換し、`UniversalDao.insert` でDBに登録
- ステータスコード `201`（作成完了）を返す

**3. Jacksonアダプタの設定（JSON変換に必要）**

Jersey環境の場合、コンポーネント設定ファイルで以下のように設定する。これにより `Jackson2BodyConverter` が自動的に組み込まれ、JSONの変換が行われる。

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

RESTEasy環境の場合は `ResteasyJaxRsHandlerListFactory` を使用する。

**注意点**:
- `@Consumes` に設定したMIMEと異なる `Content-Type` のリクエストが来た場合、ステータスコード `415`（Unsupported Media Type）が返される
- Bean Validationハンドラはリクエストボディ変換ハンドラよりも後ろに設定する必要がある（`JerseyJaxRsHandlerListFactory` が自動的に正しい順序で設定してくれる）
- JSONコンバータには `nablarch-jackson-adaptor` モジュールへの依存が必要

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2