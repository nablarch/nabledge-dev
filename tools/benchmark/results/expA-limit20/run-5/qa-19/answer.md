**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録する処理は、BodyConvertHandlerがJSONをFormに変換 → JaxRsBeanValidationHandlerがバリデーション → アクションクラスでUniversalDao.insert()というハンドラキューを通じた流れで実現する。

**根拠**:

**処理の流れ**

1. WebFrontControllerがリクエストを受信し、ハンドラキューに委譲する
2. ディスパッチハンドラ（RoutesMapping）がURIからアクションクラスを特定する
3. BodyConvertHandlerがリクエストボディ（JSON）をアクションで受け取るFormに変換する
4. JaxRsBeanValidationHandlerが変換後のFormをバリデーションする
5. アクションクラスが業務ロジックを実行しHttpResponseを返却する

**最小ハンドラ構成**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | エラー時のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンスの書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | **BodyConvertHandler** | JSONボディ→Form変換 |
| 7 | **JaxRsBeanValidationHandler** | Formのバリデーション |

**JSON変換の仕組み**

アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` を付与すると、BodyConvertHandlerがそのMIMEに対応したコンバータを使ってリクエストボディをFormに変換する。JerseyまたはRESTEasy環境では、`JerseyJaxRsHandlerListFactory` / `ResteasyJaxRsHandlerListFactory` を使用することでJackson2BodyConverterが自動的に設定される。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyのhandlerListをファクトリインジェクションするだけでBodyConvertHandler+BeanValidationHandlerが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**アクションクラスの実装例**

```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid  // ← JaxRsBeanValidationHandlerがこのアノテーションを見てバリデーションを実行
    public HttpResponse save(ProjectForm form) {
        // BeanUtil.createAndCopy()でFormからEntityに変換し、UniversalDao.insert()でDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode()); // 201を返す
    }
}
```

Formクラスのプロパティは全てString型で宣言し、Bean Validationアノテーションでバリデーションルールを定義する：

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**注意点**:
- `@Valid` アノテーションを付けないとバリデーションが実行されない
- FormのプロパティはString型で宣言すること（型変換はBeanUtilが担う）
- BodyConvertHandlerは `@Consumes` のMIMEと異なるContent-Typeのリクエストには `415 Unsupported Media Type` を返す

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4