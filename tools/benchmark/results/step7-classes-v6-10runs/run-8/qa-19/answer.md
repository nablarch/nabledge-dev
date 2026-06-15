**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与する。`BodyConvertHandler`（`Jackson2BodyConverter`）がJSONをFormクラスに自動変換し、`BeanUtil.createAndCopy()` でFormをEntityに変換後、`UniversalDao.insert()` でDB登録する。

---

**根拠**:

### 処理の流れ

1. WebFrontControllerがHTTPリクエストを受信し、ハンドラキューに委譲
2. DispatchHandler（ルーティングアダプタ）がURIからアクションクラスを特定
3. **BodyConvertHandler** がリクエストボディ（JSON）をFormクラスに変換
4. **JaxRsBeanValidationHandler** がバリデーションを実行
5. アクションクラスが業務ロジック（DB登録）を実行
6. JaxRsResponseHandlerがレスポンスをクライアントに返却

### アクションクラスの実装例

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

- `@Path` と `@POST` でURLとPOSTリクエストをマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを指定
- `@Valid` でBean Validationによるバリデーションを実行
- `BeanUtil.createAndCopy()` でFormクラスをEntityクラスに変換
- `UniversalDao.insert()` でDB登録
- ステータスコード `201`（Created）を返却

### Formクラスの作成

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

### JSON変換の仕組み（BodyConvertHandler）

`BodyConvertHandler` の `bodyConverters` プロパティに設定されたコンバータがJSON変換を担当する。Jerseyアダプタを使用する場合、`Jackson2BodyConverter` が自動的に設定され、`application/json` のリクエストボディをFormクラスに変換する。

Jerseyアダプタ使用時の設定例：

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyのハンドラキューをファクトリインジェクションするとJackson2BodyConverterが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

### 最小ハンドラ構成

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラー処理 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | URI→アクションのマッピング |
| 6 | BodyConvertHandler | JSON→Formクラスの変換 |
| 7 | JaxRsBeanValidationHandler | バリデーション実行 |

---

**注意点**:
- Formクラスのプロパティは全てString型で宣言すること
- `@Consumes` に指定したMIMEとリクエストの `Content-Type` が異なる場合、ステータスコード `415`（Unsupported Media Type）が返却される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, adapters-jaxrs-adaptor.json:s2