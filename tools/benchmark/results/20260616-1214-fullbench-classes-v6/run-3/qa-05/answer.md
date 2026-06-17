**結論**: `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与したアクションメソッドでJSONボディを受け取り、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録する。

---

**根拠**:

**1. Formクラスを作成する**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全てString型で宣言する。

**2. アクションメソッドを実装する**

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

- `@Consumes(MediaType.APPLICATION_JSON)` : JSONリクエストを受け付けることを示す。リクエストボディ変換ハンドラがこのアノテーションをもとにJSONをFormへ変換する。
- `@Valid` : Bean Validationを実行する。
- `BeanUtil.createAndCopy` : FormをEntityクラスに変換する。
- `UniversalDao.insert` : Entityをデータベースに登録する。
- ステータスコード `201`（Created）を返す。

**3. コンポーネント設定（JSONボディコンバータの設定）**

Jersey環境の場合、`JerseyJaxRsHandlerListFactory` を設定することで、JSONコンバータとして `Jackson2BodyConverter` が自動的に組み込まれる。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyJaxRsHandlerListFactoryがJackson2BodyConverterを自動設定する -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

RESTEasy環境の場合は `ResteasyJaxRsHandlerListFactory` を使用する。

---

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの要件）。
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が一致しない場合、ステータスコード `415` が返される。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2