**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドでJSONをFormに変換し、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録します。

**根拠**:

**① Formクラスの作成**

クライアントから送信されたJSONの各フィールドを受け取るFormを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② アクションクラスの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストをJSON形式で受け付けることを指定します
- `@Valid` でBean Validationによるバリデーションを実行します
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録します
- 戻り値としてリソース作成完了（ステータスコード: `201`）を表す `HttpResponse` を返します

**③ JSON変換の設定（Jersey環境の場合）**

`JerseyJaxRsHandlerListFactory` をファクトリインジェクションすることで、JSON変換用の `Jackson2BodyConverter` を含むハンドラ構成が自動設定されます。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
  <!-- 上記以外のプロパティは省略 -->
</component>
```

RESTEasy環境の場合は `ResteasyJaxRsHandlerListFactory` を使用します。

**④ ユニバーサルDAOの設定**

コンポーネント定義に `BasicDaoContextFactory` を追加します。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全てString型で宣言すること（バリデーション処理の仕様）
- `@Valid` によるバリデーションエラー時はステータスコード400が返却されます
- サーバにJacksonがバンドルされていない場合は、`nablarch-jackson-adaptor` をアプリケーションモジュールとセットでデプロイすること

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6