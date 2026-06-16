**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションをアクションメソッドに設定することで、`BodyConvertHandler`（`Jackson2BodyConverter`）がリクエストJSONをFormに自動変換し、`UniversalDao.insert()` でDBに登録する仕組みになっている。

---

**根拠**:

**処理の流れ（ハンドラ構成）**

リクエストは以下の順でハンドラキューを通過する。

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | `JaxRsResponseHandler` | レスポンス書き込み・エラー対応レスポンス生成 |
| 3 | `DbConnectionManagementHandler` | DB接続取得・解放 |
| 4 | `TransactionManagementHandler` | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URLとアクションの紐付け |
| 6 | `BodyConvertHandler` | JSONボディ→Form変換 / アクション結果→レスポンスボディ変換 |
| 7 | `JaxRsBeanValidationHandler` | Formに対するBean Validationの実行 |

**JSONコンバータの設定**

Jersey環境では、`JerseyJaxRsHandlerListFactory` を設定するだけで `Jackson2BodyConverter`（JSON）、`JaxbBodyConverter`（XML）、`FormUrlEncodedConverter`（フォーム）が自動的に設定される。

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

**フォームクラスの実装**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // getter/setter省略
}
```

**アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定すると `BodyConvertHandler` がJSONボディを `ProjectForm` に変換する
- `@Valid` を指定すると `JaxRsBeanValidationHandler` が変換後のFormにBean Validationを実行する
- `BeanUtil.createAndCopy()` でFormをEntityに変換してから `UniversalDao.insert()` でDB登録する
- 正常登録時はステータスコード `201`（CREATED）を返す

---

**注意点**:
- Formのプロパティは全てString型で宣言する（型変換はBeanUtilが担う）
- 設定していないMIMEのリクエストが来た場合、ステータスコード `415`（Unsupported Media Type）が返る

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, restful-web-service-architecture.json:s4, handlers-jaxrs-bean-validation-handler.json:s4