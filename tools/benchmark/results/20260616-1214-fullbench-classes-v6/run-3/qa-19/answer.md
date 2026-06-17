**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドでJSONボディをFormとして受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**1. 処理の流れ（ハンドラキュー）**

最小ハンドラ構成でのJSON受信～DB登録の流れ：

| No. | ハンドラ | 役割 |
|---|---|---|
| 3 | `DbConnectionManagementHandler` | DB接続取得・解放 |
| 4 | `TransactionManagementHandler` | トランザクション開始・コミット・ロールバック |
| 6 | `BodyConvertHandler` | リクエストボディ（JSON）→Formに変換 |
| 7 | `JaxRsBeanValidationHandler` | Bean Validationを実行 |

**2. JSONをFormに変換する仕組み**

`BodyConvertHandler` に設定されたコンバータが `Content-Type: application/json` のリクエストボディをFormクラスに変換する。Jerseyの場合、`JerseyJaxRsHandlerListFactory` を使うことで `Jackson2BodyConverter` が自動的に設定される：

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

**3. アクションの実装**

```java
// Formクラス
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する
    // ゲッタ・セッタ省略
}

// アクションクラス
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)  // JSONで受け取る
    @Valid                                  // Bean Validationを実行
    public HttpResponse save(ProjectForm project) {
        // FormをEntityに変換してDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode()); // 201
    }
}
```

**4. ユニバーサルDAO設定**

コンポーネント定義ファイルに `BasicDaoContextFactory` を追加する必要がある：

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全て `String` 型で宣言する（Bean Validationの要件）
- バリデーションエラー時は `ApplicationException` がスローされ、後続処理には進まない
- RESTEasy使用の場合は `JerseyJaxRsHandlerListFactory` の代わりに `ResteasyJaxRsHandlerListFactory` を使用する

参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1`, `processing-pattern/restful-web-service/restful-web-service-architecture.json:s4`, `component/handlers/handlers-body-convert-handler.json:s4`, `component/handlers/handlers-body-convert-handler.json:s5`, `component/adapters/adapters-jaxrs-adaptor.json:s2`, `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`, `component/libraries/libraries-universal-dao.json:s6`