**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラスを作成し、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けて、`UniversalDao.insert()` でDBに登録する。ハンドラキューの `BodyConvertHandler` がリクエストのJSONを自動的にフォームクラスに変換する。

**根拠**:

**1. フォームクラスの作成**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

プロパティは全て `String` 型で宣言する。

**2. アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でBean Validationを実行する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換してから `UniversalDao.insert()` で登録する
- レスポンスとしてステータスコード `201 Created` を返す

**3. 処理の流れ（仕組み）**

| No. | ハンドラ | 処理内容 |
|---|---|---|
| 3 | データベース接続管理ハンドラ | DB接続を取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット/ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを特定 |
| 6 | リクエストボディ変換ハンドラ (BodyConvertHandler) | JSONをフォームクラスに変換 |
| 7 | JaxRsBeanValidationハンドラ | フォームにバリデーションを実行 |

**4. JSONコンバータの設定（Jerseyアダプタ使用時）**

`JerseyJaxRsHandlerListFactory` を使用すると、JSONのコンバータとして `Jackson2BodyConverter` が自動的に設定される。

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

**5. ユニバーサルDAOの設定**

コンポーネント定義に `BasicDaoContextFactory` を追加する必要がある。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**: フォームのプロパティは全て `String` 型で宣言すること。`@Consumes` に設定したMIMEと異なる `Content-Type` がリクエストヘッダに設定されていた場合、ステータスコード `415` が返却される。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6