**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付与したアクションメソッドでJSONを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDBに登録します。ステータスコード `201` の `HttpResponse` を返すのが基本パターンです。

**根拠**:

処理の流れ（ハンドラキューの役割）は以下の通りです：

1. `WebFrontController`（Filterの実装）がリクエストを受信し、ハンドラキューに委譲
2. `BodyConvertHandler` が `@Consumes(APPLICATION_JSON)` の設定に従い、リクエストボディをFormクラスに変換
3. `JaxRsBeanValidationHandler` が `@Valid` アノテーションの設定に従い、Formに対してBean Validationを実行
4. アクションクラスの業務ロジックが実行される
5. `JaxRsResponseHandler` が処理結果をクライアントへのレスポンスに変換

**Formクラスの定義**:
```java
public class ProjectForm implements Serializable {
    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**アクションクラスの実装**:
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
- `@Path` + `@POST` でPOSTリクエストとURLのマッピングを定義
- `@Consumes(MediaType.APPLICATION_JSON)` で受け付けるメディアタイプを指定。`BodyConvertHandler` がこれを見てJSONをFormに変換する
- `@Valid` でバリデーションを有効化。バリデーションエラー時のレスポンス生成は `JaxRsResponseHandler` が担当
- `BeanUtil.createAndCopy(Project.class, project)` でFormからEntityに変換
- `UniversalDao.insert()` でDB登録
- ステータスコード `201`（リソース作成完了）を返却

**JSONコンバータの設定（Jersey環境の場合）**:

Jersey環境では `JerseyJaxRsHandlerListFactory` を使うと、JSONのコンバータとして `Jackson2BodyConverter` が自動的に設定されます：

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

**注意点**:
- Formクラスのプロパティは**全てString型**で定義すること。String以外の型が存在する場合、不正な値が入力されるとBeanへの変換処理がバリデーション前に失敗し、障害となる
- Jersey未使用の場合は `BodyConvertHandler` の `bodyConverters` プロパティに使用するMIMEに対応した `BodyConverter` を手動で設定すること

参照: restful-web-service-architecture.json:s2, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, libraries-bean-validation.json:s8