**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDB登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてFormで受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDB登録する。

**根拠**:

**処理の流れ（ハンドラキューを通じた全体の仕組み）**

リクエスト受信からDB登録までの流れは次のとおり：

| 順序 | ハンドラ | 役割 |
|------|---------|------|
| 1 | グローバルエラーハンドラ | 例外時ログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・例外時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得と解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始/コミット/ロールバック |
| 5 | ルーティングアダプタ | URIからアクションメソッドを決定 |
| 6 | **BodyConvertHandler** | **JSONリクエストボディ → Formクラスに変換** |
| 7 | **JaxRsBeanValidationHandler** | **変換したFormにバリデーション実行** |

JSONの変換には `BodyConvertHandler` の `bodyConverters` に設定された `BodyConverter` 実装クラスが使われる。Jersey環境では `JerseyJaxRsHandlerListFactory` を使うことで `Jackson2BodyConverter` が自動設定される：

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

**実装例**

Formクラス（JSONのプロパティを受け取る）：

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

アクションクラス（URL紐付けとDB登録）：

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON受付を宣言 → BodyConvertHandlerがJSONをFormに変換
- `@Valid` でバリデーションを有効化 → JaxRsBeanValidationHandlerがFormを検証
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換
- `UniversalDao.insert()` でDB登録（Jakarta PersistenceアノテーションをEntityに付けるだけでSQLを自動生成）
- 戻り値はステータスコード `201`（リソース作成完了）の `HttpResponse`

**注意点**:
- Formのプロパティは全て `String` 型で宣言する
- `@Consumes` に設定したMIMEとリクエストのContent-Typeが不一致の場合、ステータスコード `415`（サポートしていないメディアタイプ）が返却される
- `BodyConvertHandler` は `RoutesMapping`（ルーティングアダプタ）より後ろのハンドラキューに設定する

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2