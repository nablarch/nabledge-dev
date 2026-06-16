**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションクラスに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`アノテーションを付けたメソッドを定義し、`BeanUtil.createAndCopy()`でフォームをエンティティに変換した後、`UniversalDao.insert()`でDB登録する。

**根拠**:

**① アクションクラスの実装例**

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
- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストをJSON形式で受け付けることを宣言する
- `@Valid` — `JaxRsBeanValidationHandler` によりフォームに対するバリデーションが実行される
- `@Path` と `@POST` — URL `/projects` へのPOSTリクエストにこのメソッドをマッピングする
- `BeanUtil.createAndCopy(Project.class, project)` — フォームをエンティティに変換する
- 戻り値に `HttpResponse.Status.CREATED`（ステータスコード `201`）を返す

**② フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**③ 処理の仕組み（ハンドラキュー）**

Nablarch RESTful最小ハンドラ構成:

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsレスポンスハンドラ | レスポンス書き込み・例外処理 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを特定 |
| 6 | リクエストボディ変換ハンドラ | JSONをフォームクラスに変換 |
| 7 | Bean Validationハンドラ | フォームに対してバリデーション実行 |

JSONのパースには `Jackson2BodyConverter` が使われる。Jerseyアダプタを使用した場合のコンポーネント設定例:

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyアダプタによりJackson2BodyConverterとJaxRsBeanValidationHandlerが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**④ UniversalDAOの設定**

コンポーネント定義に以下を追加する:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームのプロパティは全て `String` 型で宣言する（バリデーションルールの設定方法に準拠）
- `Content-Type: application/json` をリクエストヘッダに指定しないと、ステータスコード `415`（サポートしていないメディアタイプ）が返る
- `@Valid` がない場合、バリデーションは実行されない

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6