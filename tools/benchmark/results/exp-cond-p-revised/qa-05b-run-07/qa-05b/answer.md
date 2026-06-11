**結論**: `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーション付きのアクションメソッドを定義すると、フレームワークが自動でJSONをFormクラスに変換・バリデーションし、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDB登録できる。

**根拠**: 処理の流れは次のとおり。

1. **BodyConvertHandler** がリクエストのJSONをFormクラスに変換する。JSONの変換には `Jackson2BodyConverter` が使われる（JerseyアダプタやRESTEasyアダプタを使用する場合は自動設定される）。
2. **JaxRsBeanValidationHandler** がFormクラスに対してBean Validationを実行する。
3. **アクションクラス** のメソッドに変換済みのFormが渡され、業務処理（DB登録）を実行する。

フォーム・アクション・URLマッピングの実装例：

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

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

最小ハンドラ構成（ルーティングアダプタ以降）：

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | JaxRsResponseHandler | レスポンス書き込み・エラー処理 |
| 2 | DbConnectionManagementHandler | DB接続取得/解放 |
| 3 | TransactionManagementHandler | トランザクション開始/コミット/ロールバック |
| 4 | RoutesMapping (ルーティングアダプタ) | URIからアクション特定 |
| 5 | BodyConvertHandler | JSONリクエストボディ→Formクラスに変換 |
| 6 | JaxRsBeanValidationHandler | Formクラスのバリデーション実行 |

Jerseyアダプタを使用する場合のハンドラキュー設定例：

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyのハンドラキューをファクトリインジェクションするとBodyConvertHandler+JaxRsBeanValidationHandlerが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

UniversalDAOを使うためのコンポーネント定義も必要：

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全てString型で宣言すること。
- `@Consumes` に指定したMIMEとリクエストのContent-Typeが異なる場合は、ステータスコード `415` が返却される。
- BodyConvertHandlerはルーティングアダプタよりも後ろに配置すること。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6