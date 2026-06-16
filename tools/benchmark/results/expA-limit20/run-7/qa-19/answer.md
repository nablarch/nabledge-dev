**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたアクションメソッドを定義すれば、フレームワークがJSONボディをFormクラスに自動変換・バリデーションし、`UniversalDao.insert()` でDBに登録できる。

---

**根拠**:

### 処理の流れ

リクエストがハンドラキューを通過する順番（最小ハンドラ構成）:

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1-2 | グローバルエラーハンドラ、JaxRsResponseHandler | エラー処理・レスポンス書き込み |
| 3-4 | DB接続管理ハンドラ、トランザクション制御ハンドラ | DB接続・トランザクション管理 |
| 5 | ルーティングアダプタ | URIをアクションにマッピング |
| 6 | **BodyConvertHandler** | JSONボディ → Formクラスに変換 |
| 7 | **JaxRsBeanValidationHandler** | Formに対してBean Validationを実行 |

### Formクラスの作成

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ・セッタは省略（プロパティは全てString型で宣言）
}
```

### アクションメソッドの実装

```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)  // JSON受け取りを指定
    @Valid                                  // バリデーションを有効化
    public HttpResponse save(ProjectForm project) {
        // BeanUtilでFormをEntityに変換し、UniversalDaoでDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode()); // 201返却
    }
}
```

### JSONコンバータの設定

Jerseyを使う場合、`JerseyJaxRsHandlerListFactory` を設定するだけで `Jackson2BodyConverter`（JSON変換）と `JaxRsBeanValidationHandler` が自動的にハンドラキューに追加される：

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- これだけでJSON対応コンバータとBeanValidationハンドラが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

RESTEasyを使う場合は `ResteasyJaxRsHandlerListFactory` を設定する。

**注意点**:
- リクエストのContent-TypeがConsumesに指定したMIMEタイプと異なる場合、ステータスコード `415`（サポートしていないメディアタイプ）が返される
- バリデーションエラー時は `ApplicationException` がスローされ、デフォルトの `JaxRsResponseHandler` がエラーレスポンスを生成する（エラーレスポンスにメッセージを含めたい場合は `ErrorResponseBuilder` のカスタマイズが必要）

参照: handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1