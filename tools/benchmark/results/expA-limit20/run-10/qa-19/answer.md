**結論**: アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてフォームクラスをパラメータに受け取り、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

**処理の仕組み（流れ）**

1. `BodyConvertHandler`（リクエストボディ変換ハンドラ）が、アクションメソッドの `@Consumes` アノテーションで指定されたMIMEタイプを見て、対応する `BodyConverter` を選択しリクエストボディをフォームクラスに変換する。JSONの場合は `Jackson2BodyConverter` が使われる。
2. `JaxRsBeanValidationHandler` が、変換されたフォームに対してバリデーションを実行する（`@Valid` アノテーションが必要）。
3. アクションメソッドが呼ばれ、フォームをエンティティに変換してDBに登録し、`HttpResponse` を返す。
4. `JaxRsResponseHandler` がレスポンスをクライアントに返却する。

**フォームクラス**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**アクションクラス**

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

**最小ハンドラ構成（コンポーネント定義）**

| No. | ハンドラ |
|---|---|
| 1 | グローバルエラーハンドラ |
| 2 | JaxRsResponseHandler |
| 3 | データベース接続管理ハンドラ |
| 4 | トランザクション制御ハンドラ |
| 5 | ルーティングアダプタ（以降はルーティングアダプタ内に設定） |
| 6 | BodyConvertHandler |
| 7 | JaxRsBeanValidationHandler |

Jerseyを使用する場合は `JerseyJaxRsHandlerListFactory` を設定すると `BodyConvertHandler`（`Jackson2BodyConverter` 含む）と `JaxRsBeanValidationHandler` が自動的にセットアップされる:

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

ユニバーサルDAOには `BasicDaoContextFactory` のコンポーネント定義も必要:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームクラスのプロパティは全て `String` 型で宣言する
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が異なる場合、ステータスコード `415` が返却される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6