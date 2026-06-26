**結論**: NablarchでREST APIとしてJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` を付け、`UniversalDao.insert()` でDBに登録する。JSONボディのフォームへの変換は `BodyConvertHandler`（実装: `Jackson2BodyConverter`）がフレームワーク側で自動的に行う。

---

**根拠**:

**① 処理の流れ（仕組み）**

リクエストはハンドラキューを通して処理される。最小ハンドラ構成での主要な流れは以下のとおり。

| No. | ハンドラ | 往路処理 | 復路処理 |
|---|---|---|---|
| 2 | JaxRsResponseHandler | ─ | レスポンス書き込み |
| 3 | データベース接続管理ハンドラ | DB接続取得 | DB接続解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始 | コミット／ロールバック |
| 5 | ルーティングアダプタ | URIからアクション決定 | ─ |
| 6 | **BodyConvertHandler** | request bodyをFormクラスに変換 | 結果をresponse bodyに変換 |
| 7 | JaxRsBeanValidationHandler | Formをバリデーション | ─ |

`BodyConvertHandler` はアクションメソッドの `@Consumes` に設定されたMIMEタイプを読み取り、対応するコンバータでボディを変換する。JSONの場合は `Jackson2BodyConverter`（Jersey環境）が使用される。

**② JSONコンバータの設定**

Jerseyを使用する場合、`JerseyJaxRsHandlerListFactory` を設定すると `Jackson2BodyConverter` が自動的に組み込まれる。

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

**③ アクションメソッドの実装例**

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

ポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言する。これにより `BodyConvertHandler` がJSONボディを `ProjectForm` に変換する。
- `@Valid` で `JaxRsBeanValidationHandler` によるバリデーションが実行される。
- `BeanUtil.createAndCopy()` でフォームクラスをエンティティクラスに変換する。
- `UniversalDao.insert()` でエンティティをDBに登録する（SQL不要）。
- 戻り値に `201 CREATED` ステータスを返す。

**④ UniversalDAOについて**

`UniversalDao` は `@Entity` などのJakarta Persistenceアノテーションをエンティティに付けるだけで、SQLを書かずに登録・更新・削除・検索などの単純なCRUDが可能。

---

**注意点**:
- `BodyConvertHandler` はルーティングアダプタ（No.5）より**後ろ**に設定する必要がある。アクションメソッドのアノテーション情報を使って変換するため、ディスパッチ先が決定された後に動作する。
- `@Consumes` に設定されたMIMEと異なるContent-Typeのリクエストが来た場合、`BodyConvertHandler` はステータスコード `415`（Unsupported Media Type）を返す。

参照: `restful-web-service-getting-started-create.json:s1`, `restful-web-service-architecture.json:s2`, `restful-web-service-architecture.json:s4`, `handlers-body-convert-handler.json:s4`, `handlers-body-convert-handler.json:s5`, `adapters-jaxrs-adaptor.json:s2`, `libraries-universal-dao.json:s2`