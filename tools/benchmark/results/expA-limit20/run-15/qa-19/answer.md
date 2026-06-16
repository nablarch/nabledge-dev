**結論**: REST APIでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)`を付けたアクションメソッドでフォームを受け取り、`BeanUtil.createAndCopy()`でエンティティに変換してから`UniversalDao.insert()`でDB登録します。

**根拠**:

**1. アクションクラスの実装**

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

- `@Path` / `@POST` でURLとHTTPメソッドをマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` により、リクエストボディのJSONが`BodyConvertHandler`によってフォームクラス（`ProjectForm`）に変換される
- `@Valid` により`JaxRsBeanValidationHandler`がフォームのバリデーションを実行
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録
- 正常登録時はステータスコード`201`を返す

**2. フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // getter/setter省略
}
```

**3. リクエストボディ変換の仕組み**

`BodyConvertHandler`（リクエストボディ変換ハンドラ）がJSON→フォームへの変換を担当します。JerseyまたはRESTEasyアダプタを使用することで、`Jackson2BodyConverter`（Jacksonベース）が自動的に設定されます。

```xml
<!-- Jersey用アダプタの設定例 -->
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

**4. リクエスト処理の流れ（最小ハンドラ構成）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URLからアクションを決定 |
| 6 | リクエストボディ変換ハンドラ | JSON → フォームクラスへの変換 |
| 7 | Jakarta RESTful Web Servcies Bean Validationハンドラ | フォームのバリデーション実行 |

**注意点**:
- フォームのプロパティは全て`String`型で宣言すること
- `BodyConvertHandler`はルーティングアダプタより後ろのハンドラキューに設定する必要がある
- Content-TypeがConsumesに設定したMIMEと異なる場合、ステータスコード`415`が返却される
- `Jackson2BodyConverter`はJersey/RESTEasyアダプタ使用時に自動設定される

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/adapters/adapters-jaxrs-adaptor.json:s2, component/libraries/libraries-universal-dao.json:s6