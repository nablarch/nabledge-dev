**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、`BeanUtil.createAndCopy`でフォームをエンティティに変換して`UniversalDao.insert`でDBに登録し、ステータスコード201の`HttpResponse`を返す。

**根拠**:

処理の仕組みは以下の流れになります。

1. WebFrontControllerがリクエストを受信し、ハンドラキューに委譲
2. **リクエストボディ変換ハンドラ**（`BodyConvertHandler`）が、`Jackson2BodyConverter`を使ってJSONボディをフォームクラスに変換
3. **Bean Validationハンドラ**（`JaxRsBeanValidationHandler`）がフォームのバリデーションを実行
4. アクションメソッドが業務処理を実行し、DBへ登録
5. `JaxRsResponseHandler`がレスポンスをクライアントに返却

**フォームクラス**（プロパティは全てString型）:

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**業務アクションメソッド**:

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

**JSONコンバータの設定**（Jersey環境の場合）:

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyJaxRsHandlerListFactoryにより以下が自動設定される：
             - BodyConvertHandler (Jackson2BodyConverter含む)
             - JaxRsBeanValidationHandler -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**実装のポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付ける宣言をする
- `@Valid` でBeanValidationを実行する
- `BeanUtil.createAndCopy` でフォームをエンティティに変換する
- `UniversalDao.insert` でDB登録する
- 戻り値にステータスコード`201`（リソース作成完了）を返す

**注意点**:
- フォームのプロパティは全てString型で宣言する必要がある
- リクエストのContent-Typeが`application/json`でない場合、サポートしていないメディアタイプを示すステータスコード`415`が返却される
- Jersey/RESTEasyアダプタを使用すると`Jackson2BodyConverter`等が自動設定され、JSONの変換が有効になる

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2