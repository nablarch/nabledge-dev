**結論**: アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与してFormクラスで受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録する。JSON変換は `Jackson2BodyConverter` が担い、ハンドラキューを経由して自動的に処理される。

**根拠**:

**① 処理の流れ（ハンドラキュー）**

リクエストはWebフロントコントローラが受信し、ハンドラキューに委譲される。最小構成では以下の順で処理が流れる。

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンスへの書き込み |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIをもとにアクションを決定 |
| 6 | BodyConvertHandler | リクエストボディをFormに変換（`@Consumes`に基づく） |
| 7 | JaxRsBeanValidationハンドラ | Formに対してバリデーションを実行 |

**② JSONの変換の仕組み**

JSONの変換は `Jackson2BodyConverter` が行う。Jersey/RESTEasyアダプタを使用する場合、`JerseyJaxRsHandlerListFactory`（または`ResteasyJaxRsHandlerListFactory`）を設定することで、`BodyConvertHandler` に `Jackson2BodyConverter` が自動的にセットされる。

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

**③ アクションの実装例**

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
- `@Valid` でBeanValidationによるバリデーションを有効にする
- `BeanUtil.createAndCopy()` でFormをEntityに変換する
- `UniversalDao.insert()` でDBに登録する
- 戻り値は作成完了（ステータスコード `201`）を表す `HttpResponse` を返す

**④ ユニバーサルDAOの設定**

DBへの登録には、コンポーネント定義に `BasicDaoContextFactory` の設定が必要となる。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- FormクラスのプロパティはすべてString型で宣言する（ユーザ入力値のバリデーションのため）
- Formで受け取った値は直接DBに挿入せず、`BeanUtil.createAndCopy()` でEntityに変換してから使用する
- `@Consumes`に指定したMIMEと異なるContent-Typeでリクエストされた場合、ステータスコード `415` が返却される

参照: restful-web-service-getting-started-create.json:s1, adapters-jaxrs-adaptor.json:s2, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, libraries-universal-dao.json:s6