**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドを実装し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換して `UniversalDao.insert()` で登録する。JSONのデシリアライズはフレームワークが自動的に行う。

---

**根拠**:

#### 処理の流れ（仕組み）

リクエスト受信からDB登録までの流れは以下のとおり：

1. WebFrontController（`jakarta.servlet.Filter`実装）がリクエストを受信
2. ハンドラキューに設定されたDispatchHandlerがURIをもとにアクションクラスを特定
3. **リクエストボディ変換ハンドラ**（`BodyConvertHandler`）がJSON本文をFormクラスに変換
4. **Bean Validationハンドラ**（`JaxRsBeanValidationHandler`）がFormに対してバリデーションを実行
5. アクションメソッドがDBへ登録処理を実行
6. **Jakarta RESTful Web Servicesレスポンスハンドラ**（`JaxRsResponseHandler`）がレスポンスを返却

#### ハンドラキューの最小構成

| No. | ハンドラ | 役割 |
|-----|--------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み・エラー応答 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを決定 |
| 6 | リクエストボディ変換ハンドラ | JSON→Formへの変換 |
| 7 | Bean Validationハンドラ | Formのバリデーション実行 |

#### JSONのデシリアライズ仕組み

`BodyConvertHandler` は、アクションメソッドの `@Consumes` アノテーションで指定されたMIMEタイプを見て、対応する `BodyConverter` を選択する。Jersey環境では `Jakarta RESTful Web ServicesアダプタJerseyJaxRsHandlerListFactory` を使用すると、`Jackson2BodyConverter` が自動的にJSONコンバータとして設定される。

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

#### アクションメソッドの実装例

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

フォームクラス（受け取り用）:
```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**注意点**:
- Formクラスのプロパティは全て `String` 型で宣言すること
- `@Consumes(MediaType.APPLICATION_JSON)` に合わないContent-Typeのリクエストが来た場合、ステータスコード `415` が返却される
- DBアクセスにはトランザクション制御ハンドラが必要（ハンドラキューへの設定が前提）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2