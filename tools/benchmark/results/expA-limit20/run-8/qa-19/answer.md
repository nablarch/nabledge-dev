**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてFormでJSON本文を受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録します。

**根拠**:

**① フォームクラスの作成**

JSONのプロパティに対応するFormクラスを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を付けることで、リクエストボディが `BodyConvertHandler`（内部で `Jackson2BodyConverter`）によりFormに自動変換される
- `@Valid` でBean Validationハンドラによるバリデーションが実行される
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する
- `HttpResponse.Status.CREATED.getStatusCode()` によりステータスコード `201` を返却する
- `@Path` と `@POST` でURLとのマッピングを定義する

**③ JSON変換の仕組み（BodyConverter設定）**

Jersey環境では、`JerseyJaxRsHandlerListFactory` をファクトリインジェクションするだけで、JSONコンバータ（`Jackson2BodyConverter`）が自動設定されます。

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

**④ ユニバーサルDAOの設定**

コンポーネント定義に `BasicDaoContextFactory` を追加します。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- リクエストヘッダの `Content-Type` が `application/json` 以外の場合、ステータスコード `415`（サポートしていないメディアタイプ）が返却されます
- RESTfulウェブサービスでは `排他制御` ライブラリ（クライアントtaglibとの連動が前提）は使用できません。楽観的ロックが必要な場合はリクエストボディにバージョン番号を含めてください

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6