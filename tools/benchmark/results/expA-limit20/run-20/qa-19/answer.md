**結論**: JSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`BeanUtil.createAndCopy()` でフォームをEntityに変換し、`UniversalDao.insert()` でDBに登録する。フレームワーク側では `BodyConvertHandler`（`Jackson2BodyConverter`）がJSONをフォームに自動変換し、`TransactionManagementHandler` がコミットを行う。

**根拠**:

**1. 処理の流れ（最小ハンドラ構成）**

リクエストはハンドラキューを通じて以下の順で処理される：

| No. | ハンドラ | 役割 |
|-----|--------|------|
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット/ロールバック |
| 5 | ルーティングアダプタ | URLをもとにアクションを決定 |
| 6 | **BodyConvertHandler** | request body → フォームクラスに変換 |
| 7 | JaxRsBeanValidationHandler | フォームのバリデーション実行 |

**2. JSONボディ変換の仕組み**

`BodyConvertHandler` は `bodyConverters` プロパティに設定された `BodyConverter` 実装クラスを使って変換する。Jersey環境では `JerseyJaxRsHandlerListFactory` を使うことで、JSONコンバータ（`Jackson2BodyConverter`）が自動設定される：

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

アクションメソッドの `@Consumes(MediaType.APPLICATION_JSON)` と、BodyConvertHandlerに設定されたコンバータのMIMEが一致したとき変換が行われる。

**3. アクションの実装例**

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

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付ける
- `@Valid` でBeanValidationによるバリデーションを実行する
- `BeanUtil.createAndCopy()` でフォームをEntityクラスに変換する
- `UniversalDao.insert()` でDBに登録する
- ステータスコード `201`（CREATED）を返す

**4. ユニバーサルDAOの設定**

ユニバーサルDAOを使うには、コンポーネント設定ファイルに以下を追加する：

```xml
<!-- コンポーネント名は "daoContextFactory" で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `BodyConvertHandler` はルーティングアダプタより後ろに配置する必要がある（ルーティング後にアクションのアノテーション情報が利用可能になるため）
- `@Consumes` に指定したMIMEとリクエストの`Content-Type`が不一致の場合はステータスコード `415`（Unsupported Media Type）が返される

参照: component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/libraries/libraries-universal-dao.json:s6