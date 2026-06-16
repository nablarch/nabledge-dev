**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、リクエストボディをFormクラスとして受け取り、`BeanUtil.createAndCopy`でEntityに変換後、`UniversalDao.insert`でDBに登録する。

**根拠**:

**① 処理の流れ（アーキテクチャ）**

リクエストは以下の順番で処理される：

1. `WebFrontController`（Servlet Filter）がリクエストを受信
2. ハンドラキューに処理を委譲
3. `BodyConvertHandler`がJSONリクエストボディをFormクラスに変換（`@Consumes`で指定したMIMEに従う）
4. `JaxRsBeanValidationHandler`がバリデーションを実行（`@Valid`で指示）
5. アクションクラスが業務ロジックを実行してDBに登録
6. `JaxRsResponseHandler`がレスポンスをクライアントに返却

**② アクションクラスの実装例**

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

**③ Formクラスの実装例**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する

**④ ハンドラ設定（コンポーネント定義）**

JSONを処理するには`BodyConvertHandler`に`Jackson2BodyConverter`が必要。Jersey環境では`JerseyJaxRsHandlerListFactory`を使うと自動設定される：

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

手動設定する場合は`BodyConvertHandler`の`bodyConverters`プロパティにJSONコンバータ（`Jackson2BodyConverter`）を追加する。

**⑤ ユニバーサルDAOの設定**

コンポーネント定義に以下を追加する：

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `@Consumes`に設定したMIMEと異なる`Content-Type`がリクエストに含まれる場合、ステータスコード`415`が返却される
- サポートしていないMIMEのコンバータも同様に`415`を返す
- Formのプロパティは全てString型で宣言すること（Bean Validationの制約）
- 最小ハンドラ構成には、データベース接続管理ハンドラとトランザクション制御ハンドラも必要

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6