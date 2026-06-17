**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションクラスに `@Consumes(MediaType.APPLICATION_JSON)` を付けたメソッドを定義し、`BodyConvertHandler`（内部でJackson2BodyConverterを使用）がJSONをFormクラスに変換した後、`UniversalDao.insert()` でDBに登録する。

---

**根拠**:

### 処理の流れ

リクエストが届いてからDBに登録されるまで、以下の流れで処理される。

1. **WebFrontController** (ServletFilter) がリクエストを受信
2. **ルーティングアダプタ** (RoutesMapping) がURIをもとに呼び出すアクションクラス・メソッドを決定
3. **BodyConvertHandler** がリクエストボディ（JSON）をアクションメソッドで受け取るFormクラスに変換（`@Consumes`で指定したMIMEタイプに対応するBodyConverterを使用）
4. **JaxRsBeanValidationHandler** が変換済みFormにバリデーションを実行（`@Valid`が付いている場合）
5. **アクションクラス** が業務ロジック（DB登録）を実行
6. **JaxRsResponseHandler** がレスポンスをクライアントへ返却

### 最小ハンドラ構成

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外時のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラー時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得/解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始/コミット/ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | BodyConvertHandler | JSONボディ ⇔ Formクラスの変換 |
| 7 | JaxRsBeanValidationHandler | Formのバリデーション実行 |

### JSON変換の仕組み

`BodyConvertHandler`は、アクションメソッドの`@Consumes`アノテーションで指定されたMIMEタイプに対応する`BodyConverter`を使って変換する。JSONの場合、`Jackson2BodyConverter`が使用される。

Jersey環境ではJerseyアダプタ、RESTEasy環境ではRESTEasyアダプタを使うと、`Jackson2BodyConverter`を含むBodyConvertHandlerが自動的に設定される。

```xml
<!-- Jersey環境の場合 -->
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

### アクションクラスの実装例

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        // BeanUtilでFormをEntityに変換し、UniversalDaoでDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

実装のポイント:
- `@Path("/projects")` + `@POST` でPOSTリクエスト時のマッピングを定義
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言
- `@Valid` でFormへのバリデーションを有効化（JaxRsBeanValidationHandlerが実行）
- `BeanUtil.createAndCopy(Entity.class, form)` でFormをEntityに変換
- `UniversalDao.insert(entity)` でDB登録（SQLは不要、Jakarta Persistenceアノテーションから自動構築）
- 戻り値はステータスコード`201`（リソース作成完了）を表すHttpResponse

### フォームクラスの実装例

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // getter/setter省略
}
```

### ユニバーサルDAOの設定

ユニバーサルDAOを使用するには、コンポーネント定義に以下を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**: `@Consumes`に設定したMIMEとリクエストの`Content-Type`が異なる場合は、ステータスコード`415`（Unsupported Media Type）が返却される。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6