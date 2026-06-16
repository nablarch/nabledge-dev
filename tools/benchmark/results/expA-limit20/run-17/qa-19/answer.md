**結論**: RESTful APIでJSONを受け取ってDBに登録するには、Formクラスを定義し、アクションメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付け、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` で登録する。

---

**根拠**:

**1. 処理の流れ**

```
HTTPリクエスト(JSON)
  → リクエストボディ変換ハンドラ (BodyConvertHandler)
      → JSONをFormクラスに変換 (Jackson2BodyConverter)
  → JaxRsBeanValidationハンドラ (@Valid によるBean Validation)
  → アクションメソッド
      → BeanUtil.createAndCopy() でEntityに変換
      → UniversalDao.insert() でDB登録
  → HttpResponse(201) を返却
```

**2. Formクラスの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**3. アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でBean ValidationによるFormの検証を実行する
- `BeanUtil.createAndCopy()` でFormをEntityに変換する
- `UniversalDao.insert()` でDB登録し、ステータスコード `201` を返す

**4. ハンドラ構成**

DBへの登録を伴うREST APIには最低限以下のハンドラが必要：

| 順序 | ハンドラ | 役割 |
|------|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseハンドラ | レスポンス書き込み・例外時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット/ロールバック |
| 5 | ルーティングアダプタ(RoutesMapping) | URLとアクションのマッピング |
| 6 | リクエストボディ変換ハンドラ | JSONをFormクラスに変換 |
| 7 | JaxRsBeanValidationハンドラ | @Valid によるバリデーション実行 |

**5. JSONコンバータの設定（Jersey環境の場合）**

Jersey用アダプタを使うと、JSONコンバータ（`Jackson2BodyConverter`）が自動設定される：

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

これにより以下のコンバータが自動設定される：
- JSON: `Jackson2BodyConverter`
- XML: `JaxbBodyConverter`
- application/x-www-form-urlencoded: `FormUrlEncodedConverter`

**注意点**:
- Formのプロパティは全て `String` 型で宣言すること（Bean Validationの仕様）
- `@Consumes` に指定したMIMEと異なるContent-Typeのリクエストが来た場合、ステータスコード `415` が返却される
- ユニバーサルDAOを使用するには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, restful-web-service-architecture.json:s4