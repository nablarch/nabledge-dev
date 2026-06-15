**結論**: リソース(アクション)メソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてFormを引数で受け取り、`BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDBに登録する。

---

**根拠**:

#### 1. Formクラスの作成

JSONの各フィールドに対応するFormクラスを作成する。プロパティは**全てString型**で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. リソース(アクション)クラスの実装

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

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストをJSON形式で受け付けることを指定する
- `@Valid` — リクエストのBean Validationを実行する
- `BeanUtil.createAndCopy(Project.class, project)` — FormをEntityに変換する
- `UniversalDao.insert()` — Entityをもとにインサート用SQLを自動生成してDBに登録する
- 戻り値はステータスコード `201`（作成完了）の `HttpResponse` を返す

#### 3. JSONコンバータの設定（アダプタ）

JSON変換には `Jackson2BodyConverter` が使われる。Jerseyを使う場合は `JerseyJaxRsHandlerListFactory` を、RESTEasyを使う場合は `ResteasyJaxRsHandlerListFactory` を設定すると、JSONコンバータ（`Jackson2BodyConverter`）とBean Validationハンドラが自動的に構成される。

**Jersey環境の場合:**

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

**RESTEasy環境の場合:**

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.resteasy.ResteasyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**注意点**:
- Formのプロパティは全てString型で宣言すること（バリデーション後に `BeanUtil` で型変換される）
- `UniversalDao` を使うには別途 `BasicDaoContextFactory` のコンポーネント設定が必要
- アプリケーションサーバにJacksonがバンドルされていない場合は、Jacksonのモジュールをアプリケーションモジュールとセットでデプロイすること

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2, component/adapters/adapters-jaxrs-adaptor.json:s3, component/libraries/libraries-universal-dao.json:s6