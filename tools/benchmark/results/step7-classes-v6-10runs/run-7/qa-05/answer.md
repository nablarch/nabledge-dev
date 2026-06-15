**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドにフォームを引数として受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録します。

**根拠**:

**1. フォームクラスの作成**

JSONの各フィールドを受け付けるフォームを作成します。プロパティは全て `String` 型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ
}
```

**2. アクションクラスの実装**

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm form) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONがフォームに変換される
- `@Valid` でBean Validationによるバリデーションが実行される
- `BeanUtil.createAndCopy(Project.class, form)` でフォームをEntityに変換する
- `UniversalDao.insert(entity)` でDBに登録する
- 登録成功時は201（Created）を返却する

**3. JSON変換の仕組み**

`BodyConvertHandler`（リクエストボディ変換ハンドラ）が `Jackson2BodyConverter` を使ってリクエストのJSONボディをフォームに変換します。Jersey環境の場合、`JerseyJaxRsHandlerListFactory` を設定すると `Jackson2BodyConverter` が自動的にセットアップされます。

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

コンポーネント定義に `BasicDaoContextFactory` を追加する必要があります。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Content-TypeヘッダにJSONのMIME（`application/json`）が設定されていない場合、ステータスコード415（Unsupported Media Type）が返却される
- フォームのプロパティは全て `String` 型で宣言すること

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6