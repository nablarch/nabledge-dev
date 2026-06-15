**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@POST`+`@Consumes(MediaType.APPLICATION_JSON)`+`@Valid`を付けたアクションメソッドを実装し、`BeanUtil.createAndCopy()`でFormをEntityに変換後、`UniversalDao.insert()`でDBに登録します。

**根拠**:

## 処理の全体像

リクエストはハンドラキューを経由してアクションに届きます：

```
JSONリクエスト
  → BodyConvertHandler（JSONボディ → Formオブジェクト変換）
  → JaxRsBeanValidationHandler（バリデーション実行）
  → アクションクラス（業務処理 → DB登録）
  → JaxRsResponseHandler（レスポンス返却）
```

## 実装手順

### 1. Formクラスの作成

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言すること

### 2. アクションメソッドの実装

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストを受け付けるMIMEを指定
- `@Valid`: JaxRsBeanValidationHandlerによるバリデーションを実行
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに型変換して移送
- `UniversalDao.insert()`: Entityをそのまま登録
- ステータスコード`201`（リソース作成完了）を返却

### 3. ハンドラ構成（最小構成）

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・例外時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得と解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを特定 |
| 6 | BodyConvertHandler | JSONボディをFormに変換 |
| 7 | JaxRsBeanValidationHandler | Formへのバリデーション実行 |

### 4. JSONコンバータの設定（Jersey環境の場合）

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyJaxRsHandlerListFactoryにより
             Jackson2BodyConverter（JSON対応）が自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

`JerseyJaxRsHandlerListFactory`（RESTEasyは`ResteasyJaxRsHandlerListFactory`）を設定すると、`Jackson2BodyConverter`（JSON変換）が自動的に組み込まれます。

**注意点**: `BodyConvertHandler`は`ルーティングアダプタ`より後ろに設定すること。サポートしないMIMEが指定された場合、ステータスコード`415`が返却されます。

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2