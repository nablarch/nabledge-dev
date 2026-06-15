**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`BodyConvertHandler`（リクエストボディ変換ハンドラ）がリクエストのJSONをフォームクラスに変換し、アクションメソッド内で`BeanUtil.createAndCopy`によりエンティティに変換後、`UniversalDao.insert`でDBに登録します。

**根拠**:

**処理の流れ**

1. `WebFrontController`（Servletフィルタ）がリクエストを受信し、ハンドラキューに委譲する
2. ルーティングアダプタがURIからアクションクラスを特定する
3. `BodyConvertHandler`がリクエストボディ（JSON）をアクションで受け付けるフォームクラスに変換する
4. `JaxRsBeanValidationHandler`がフォームクラスに対してバリデーションを実行する
5. アクションメソッドが`UniversalDao.insert`でDBに登録する
6. `JaxRsResponseHandler`がレスポンスをクライアントに返す

**フォームクラスの実装例**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**アクションメソッドの実装例**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを宣言する
- `@Valid` でリクエストのバリデーションを実行する（`JaxRsBeanValidationHandler`が処理する）
- `BeanUtil.createAndCopy`でフォームをエンティティに変換し、`UniversalDao.insert`でDB登録する
- `HttpResponse.Status.CREATED`（ステータスコード `201`）を返す

**JSONコンバータ（BodyConverter）の設定**

`BodyConvertHandler`の`bodyConverters`プロパティにJSON用の`BodyConverter`実装クラスを設定する必要がある。Jersey環境では`JerseyJaxRsHandlerListFactory`を使用すると`Jackson2BodyConverter`（JSON変換）が自動的に設定される：

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

**最小ハンドラ構成（ハンドラキューの順序）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外・エラーのログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み、エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを決定 |
| 6 | BodyConvertHandler | JSONをフォームに変換、処理結果をレスポンスボディに変換 |
| 7 | JaxRsBeanValidationHandler | フォームへのバリデーション実行 |

**注意点**:
- `BodyConvertHandler`はルーティングアダプタよりも後ろに設定すること（アノテーション情報を参照するためディスパッチ先の特定が先に必要）
- `@Consumes`に設定したMIMEと異なるContent-Typeがリクエストに設定されている場合、ステータスコード`415`が返される
- RESTfulウェブサービスでは`@Contextアノテーション`を使ったServletリソースのインジェクションやCDIは使用できない

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, restful-web-service-architecture.json:s3