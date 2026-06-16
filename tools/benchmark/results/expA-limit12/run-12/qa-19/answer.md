**結論**: NablarchのRESTfulウェブサービスでは、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与したアクションメソッドでJSONボディをFormクラスとして受け取り、`UniversalDao.insert()` でDBに登録する。フレームワークの `BodyConvertHandler` がJSONをFormに変換し、`JaxRsBeanValidationHandler` がバリデーションを実行する、という流れになっている。

---

**根拠**:

**処理の流れ（アーキテクチャ）**

1. Webフロントコントローラがリクエスト受信
2. ルーティングアダプタ（`RoutesMapping`）がURIをもとにアクションを特定
3. **`BodyConvertHandler`** がリクエストボディ（JSON）を `@Consumes` の指定に従いFormクラスに変換（JacksonアダプタはJSONに `Jackson2BodyConverter` を使用）
4. **`JaxRsBeanValidationHandler`** がFormに対してBean Validationを実行
5. アクションメソッドが呼び出され、業務ロジックを実行
6. `JaxRsResponseHandler` がレスポンスをクライアントに返す

**実装コード例**

Formクラス:
```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

アクションクラス:
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

**ハンドラ構成の設定例（最小構成）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外ログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | BodyConvertHandler | JSONボディ ↔ Formクラス変換 |
| 7 | JaxRsBeanValidationHandler | Formに対するバリデーション実行 |

Jerseyアダプタを使用する場合、No.6/7のハンドラは以下の設定で自動的に構成される（`Jackson2BodyConverter` がJSONコンバータとして自動設定される）:
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

---

**注意点**:
- Formのプロパティは全て **String型** で宣言すること（型変換はフレームワーク側で行う）
- `@Consumes` に設定したMIMEタイプとリクエストの `Content-Type` が異なる場合、ステータスコード **415（Unsupported Media Type）** が返される
- `@Valid` アノテーションがないメソッドではバリデーションは実行されない

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2