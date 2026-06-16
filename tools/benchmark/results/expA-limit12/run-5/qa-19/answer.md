**結論**: REST APIでJSONを受け取ってDBに登録するには、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付与し、`BodyConvertHandler`がJSONをFormクラスに変換した後、`BeanUtil`でエンティティに変換し`UniversalDao.insert()`でDBに登録する。

**根拠**:

**処理の流れ**

1. `WebFrontController`（`jakarta.servlet.Filter`の実装）がリクエストを受信
2. ハンドラキューを経由し、`RoutesMapping`（ルーティングアダプタ）がURIからアクションクラスを特定
3. `BodyConvertHandler`がリクエストボディをFormクラスに変換（JSONには`Jackson2BodyConverter`を使用）
4. `JaxRsBeanValidationHandler`がフォームに対してバリデーションを実行
5. アクションクラスが業務ロジックを実行し、DBに登録

**実装例**

フォームクラス（受け取るJSONのプロパティをString型で宣言）:
```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

アクションメソッド:
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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストを受け付けることを宣言
- `@Valid`: バリデーションを実行する指定
- `BeanUtil.createAndCopy()`: フォームをエンティティクラスに変換
- `UniversalDao.insert()`: エンティティをDBに登録
- 戻り値はステータスコード`201`（作成完了）の`HttpResponse`

**BodyConvertHandlerの設定（Jersey環境の場合）**:

Jersey用アダプタを使用すると、`Jackson2BodyConverter`（JSON）や`JaxbBodyConverter`（XML）などが自動的にハンドラキューに設定される。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyのハンドラキューをファクトリインジェクションするだけでOK -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**注意点**:
- フォームのプロパティは**全てString型**で宣言すること（バリデーション後に`BeanUtil`で型変換する）
- `BodyConvertHandler`はルーティングアダプタ（`RoutesMapping`）よりも後ろに設定すること
- `@Consumes`に設定したMIMEと異なる`Content-Type`でリクエストが来た場合、ステータスコード`415`が返却される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, adapters-jaxrs-adaptor.json:s2, handlers-body-convert-handler.json:s4