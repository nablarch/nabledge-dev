**結論**: NablarchのRESTfulウェブサービスでJSONをDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドでFormを受け取り、`BeanUtil.createAndCopy` でEntityに変換後 `UniversalDao.insert` でDB登録する。JSONの変換はフレームワーク（`BodyConvertHandler` + `Jackson2BodyConverter`）が自動で行う。

**根拠**（仕組みの流れ）:

リクエストは以下の順でハンドラを通る：

| No. | ハンドラ | JSON登録時の役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外時のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み／例外時のエラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションメソッドを決定 |
| 6 | BodyConvertHandler | JSONボディをFormクラスに変換 |
| 7 | JaxRsBeanValidationHandler | Formに対してバリデーション実行 |

**① Formクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**② アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: `BodyConvertHandler`がこれを見てJSONをFormに変換する
- `@Valid`: `JaxRsBeanValidationHandler`にバリデーション実行を指示する
- `BeanUtil.createAndCopy`: FormをEntityに変換する
- `UniversalDao.insert`: EntityをDBに登録する
- ステータスコード `201`（リソース作成完了）を返す

**③ ハンドラ設定（Jersey環境）**

`JerseyJaxRsHandlerListFactory`を使うと、JSONコンバータ（`Jackson2BodyConverter`）が自動設定される：

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

**④ UniversalDAOの設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全て`String`型で宣言する
- `BodyConvertHandler`はルーティングアダプタより後ろに設定する（最小ハンドラ構成のNo.5→No.6の順序）
- `@Consumes`に指定したMIMEと異なるContent-TypeのリクエストにはHTTP 415が返される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6