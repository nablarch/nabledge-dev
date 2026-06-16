**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を指定し、`BeanUtil.createAndCopy()` でフォームをEntityに変換した後、`UniversalDao.insert()` でDBに登録する。

---

**根拠**:

#### 処理の流れ

リクエスト受信からDB登録までの流れは以下のとおり：

1. `WebFrontController`（Servlet Filter）がHTTPリクエストを受信する
2. ハンドラキューに処理を委譲する
3. `BodyConvertHandler` がJSONリクエストボディをFormクラスに変換する（`Jackson2BodyConverter` が使用される）
4. `JaxRsBeanValidationHandler` がFormクラスに対してバリデーションを実行する
5. アクションクラスが `BeanUtil` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録する
6. `HttpResponse`（ステータスコード201）を返却する

#### アクションクラスの実装例

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

#### Formクラスの実装例

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

#### 最小ハンドラ構成（コンポーネント設定）

| No. | ハンドラ | 役割 |
|-----|----------|------|
| 1 | グローバルエラーハンドラ | 例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス生成・書き込み |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを決定 |
| 6 | リクエストボディ変換ハンドラ | JSONボディをFormに変換 |
| 7 | Bean Validationハンドラ | Formに対してバリデーション実行 |

#### JSON変換コンバータの設定（Jersey環境の例）

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyアダプタでJackson2BodyConverterが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

JerseyアダプタまたはRESTEasyアダプタを使用すると、`Jackson2BodyConverter`（JSON）、`JaxbBodyConverter`（XML）、`FormUrlEncodedConverter` などが自動的に設定される。

#### ユニバーサルDAOの設定

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

Jakarta PersistenceアノテーションをEntityに付けるだけで、SQLを書かずに `UniversalDao.insert()` で登録できる。

---

**注意点**:
- `@Consumes` で指定したMIMEタイプとリクエストの `Content-Type` が一致しない場合、ステータスコード `415`（Unsupported Media Type）が返される
- `BodyConvertHandler` は `ルーティングアダプタ` よりも後ろに設定すること（アクションメソッドのアノテーション情報が必要なため）
- ユニバーサルDAOは内部でJDBCラッパーを使用するため、データベース接続の設定が別途必要

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2