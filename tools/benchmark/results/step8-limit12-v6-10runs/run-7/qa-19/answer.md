**結論**: REST APIでJSONを受け取ってDBに登録するには、`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)` を付けたアクションクラスのメソッドを実装し、フレームワークの `BodyConvertHandler`（`Jackson2BodyConverter`）がJSONをFormに自動変換した後、`UniversalDao.insert()` でDB登録する。

---

**根拠**:

### 処理の流れ

```
HTTPリクエスト (POST, Content-Type: application/json)
  → WebFrontController
  → ハンドラキュー
      1. グローバルエラーハンドラ
      2. JaxRsResponseHandler（レスポンス書き込み・エラー処理）
      3. DB接続管理ハンドラ（DB接続取得・解放）
      4. トランザクション制御ハンドラ（commit/rollback）
      5. ルーティングアダプタ（URIからアクション特定）
      6. BodyConvertHandler（JSON→Formオブジェクト変換）
      7. JaxRsBeanValidationHandler（@Validによるバリデーション）
  → アクションクラスのメソッド実行
  → UniversalDao.insert() でDB登録
  → HttpResponse(201) を返却
```

---

### 実装例

**Formクラス（JSON受信用）**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;

    // プロパティは全てString型で宣言する
    // getter/setter は省略
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

- `@Consumes(MediaType.APPLICATION_JSON)` — `BodyConvertHandler` がこのアノテーションを元に `Jackson2BodyConverter` でJSONをFormに変換する
- `@Valid` — `JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する
- `BeanUtil.createAndCopy()` — FormオブジェクトをEntityクラスにコピーする
- `UniversalDao.insert()` — EntityをDBに登録する
- 戻り値のステータスコードは `201`（CREATED）

---

### ハンドラ設定（Jersey環境の場合）

`JerseyJaxRsHandlerListFactory` を使うと、`BodyConvertHandler`（`Jackson2BodyConverter` 含む）と `JaxRsBeanValidationHandler` が自動的にハンドラキューへ追加される。

```xml
<component name="packageMapping"
           class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyJaxRsHandlerListFactory が自動でBodyConvertHandler等を設定 -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
</component>
```

---

**注意点**:
- `@Valid` を設定するとバリデーションエラー時はアクションに処理が渡らず、後続のハンドラに `ApplicationException` を送出して終了する
- `BodyConvertHandler` はルーティングアダプタより後ろに設定する必要がある（最小ハンドラ構成の順序に従う）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, handlers-jaxrs-bean-validation-handler.json:s4