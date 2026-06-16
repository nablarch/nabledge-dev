**結論**: REST APIでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、フレームワークがJSONをFormオブジェクトに変換したものを受け取り、`BeanUtil`でEntityに変換後、`UniversalDao.insert()`でDBに登録します。

---

**根拠**:

### 処理の流れ（仕組み）

リクエストがサーバに届いてからDB登録完了までの流れは以下のとおりです。

1. **WebフロントコントローラがHTTPリクエストを受信**し、ハンドラキューに処理を委譲します。
2. **ルーティングアダプタ（`RoutesMapping`）** がURIをもとに呼び出すアクションクラス・メソッドを決定します。
3. **リクエストボディ変換ハンドラ（`BodyConvertHandler`）** がリクエストのJSONボディをアクションメソッドの引数型（Formクラス）に変換します。JSON変換には `Jackson2BodyConverter` が使われます。
4. **Bean Validationハンドラ（`JaxRsBeanValidationHandler`）** が変換後のFormに対してバリデーションを実行します。
5. **アクションメソッド**がFormを受け取り、`BeanUtil.createAndCopy()`でEntityに変換後、`UniversalDao.insert()`でDBに登録します。
6. **`JaxRsResponseHandler`** がアクションの戻り値（`HttpResponse`）をHTTPレスポンスとしてクライアントに返します。

### 最小ハンドラ構成

| No. | ハンドラ | 役割 |
|-----|----------|------|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得/解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始/コミット/ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの対応付け |
| 6 | リクエストボディ変換ハンドラ | JSONボディ↔Formオブジェクトの変換 |
| 7 | Bean Validationハンドラ | Formのバリデーション |

### 実装例

**Formクラス（JSONのキーに対応するプロパティを持つ）**:
```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```
- プロパティは全て `String` 型で宣言します。

**アクションクラス**:
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
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付けることを宣言します。`BodyConvertHandler`はこのアノテーションをもとに変換処理を行います。
- `@Valid`: フレームワークがFormに対してBean Validationを実行します。
- `BeanUtil.createAndCopy(Project.class, project)`: FormからEntityへ変換します。
- `UniversalDao.insert(entity)`: EntityをDBに登録します（SQL不要。`@Table`/`@Column`等のJakarta PersistenceアノテーションをEntityに付けておくと、SQLが自動生成されます）。
- 戻り値の `new HttpResponse(201)` は登録成功（HTTP 201 Created）を示します。

### JSON変換の設定（Jersey環境の例）

Jerseyを使用する場合は `JerseyJaxRsHandlerListFactory` をファクトリインジェクションするだけで、`Jackson2BodyConverter`（JSON）などのコンバータが自動設定されます。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyのハンドラキューをファクトリインジェクションするとJSON変換が自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

### ユニバーサルDAOの設定

`UniversalDao`を使うには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要です。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- `@Valid`をアクションメソッドに付けないとバリデーションは実行されません。
- `@Consumes`に設定したMIMEとリクエストの`Content-Type`が不一致の場合、HTTP 415（Unsupported Media Type）が返ります。
- Formクラスのプロパティは全て`String`型で宣言してください（Bean Validationの制約）。
- `UniversalDao.insert()`はEntityを受け取ります。FormをそのままinsertせずBeanUtilでEntityに変換してください。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2