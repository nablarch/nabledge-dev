**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、フォームクラスで受け取り `UniversalDao.insert()` で登録します。

---

**根拠**:

**① フォームクラスの作成**

JSONリクエストのフィールドを受け付けるFormクラスを作成します。プロパティは全て `String` 型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // その他フィールド、ゲッタ・セッタは省略
}
```

**② アクションクラスの実装**

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

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` を付けるとBean Validationが自動実行される（バリデーションエラー時は `ApplicationException` がスローされ後続処理は行われない）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録
- 登録完了時はステータスコード `201`（Created）の `HttpResponse` を返す

**③ JSONコンバータの設定**（コンポーネント設定ファイル）

Jersey環境の場合、`JerseyJaxRsHandlerListFactory` を設定すると `Jackson2BodyConverter`（JSON変換）が自動的に組み込まれます。

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

RESTEasy環境の場合は `ResteasyJaxRsHandlerListFactory` を使います。

---

**注意点**:
- Formのプロパティは全て `String` 型で宣言すること（型変換はBeanUtilが処理）
- `bodyConverters` に設定されたコンバータで変換できないMIMEがリクエストで指定された場合、ステータスコード `415`（Unsupported Media Type）が返却される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, adapters-jaxrs-adaptor.json:s3