**結論**: RESTfulウェブサービスでJSONを受け取りDBに登録するには、アクションメソッドに`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid`を付け、`BeanUtil.createAndCopy()`でフォームをエンティティに変換後、`UniversalDao.insert()`でDBに登録する。

---

**根拠**:

**処理の流れ**

1. WebFrontControllerがPOSTリクエストを受信し、ハンドラキューに委譲する
2. `RoutesMapping`（ルーティングアダプタ）がURIを元にアクションクラスを特定する
3. `BodyConvertHandler`がリクエストボディのJSONをFormクラスに変換する
4. `JaxRsBeanValidationHandler`がFormに対してBean Validationを実行する
5. アクションメソッドで業務ロジック（DB登録）を実行する
6. `JaxRsResponseHandler`がレスポンスをクライアントに返却する

**最小ハンドラ構成**（コンポーネント設定ファイル）

| No. | ハンドラ |
|---|---|
| 1 | グローバルエラーハンドラ |
| 2 | JaxRsResponseHandler（レスポンス・エラー処理） |
| 3 | データベース接続管理ハンドラ |
| 4 | トランザクション制御ハンドラ |
| 5 | RoutesMapping（ルーティングアダプタ） |
| 6 | BodyConvertHandler（JSONコンバータ設定） |
| 7 | JaxRsBeanValidationHandler |

**JerseyアダプタでJSON対応を自動設定する**

`JerseyJaxRsHandlerListFactory`を使うと、JSONコンバータ（`Jackson2BodyConverter`）とBean Validationハンドラが自動設定される:

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

**ユニバーサルDAOの設定**

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**フォームクラスの実装**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**アクションクラスの実装**（JSONを受け取りDBに登録）

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを宣言する
- `@Valid` でリクエストのBean Validationを有効にする
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換する
- `UniversalDao.insert()` でDBに登録する
- 戻り値はリソース作成完了を示すステータスコード`201`の`HttpResponse`を返す

**注意点**:
- フォームのプロパティは全て`String`型で宣言すること（Bean Validationの仕様上の制約）
- `BodyConvertHandler`はルーティングアダプタより後ろに設定すること（アクションのアノテーション情報が必要なため）
- `JaxRsBeanValidationHandler`は`BodyConvertHandler`より後ろに設定すること（変換後のFormに対してバリデーションを実行するため）

参照: processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/adapters/adapters-jaxrs-adaptor.json:s2, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/libraries/libraries-universal-dao.json:s6