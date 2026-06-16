**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、ハンドラキューで`BodyConvertHandler`（Jackson2BodyConverter）がJSONをFormに変換し、アクションメソッドで`UniversalDao.insert()`を呼び出す構造になっています。

**根拠**:

**処理の全体の流れ**

```
HTTPリクエスト(JSON)
    ↓
WebFrontController（Servletフィルタ）
    ↓ ハンドラキュー
1. グローバルエラーハンドラ
2. JaxRsResponseHandler（レスポンス書き込み・エラー処理）
3. DB接続管理ハンドラ（DB接続の取得・解放）
4. トランザクション制御ハンドラ（コミット・ロールバック）
5. ルーティングアダプタ（URIとアクションを紐付け）
6. BodyConvertHandler（JSON → Formに変換）  ← Jackson2BodyConverterが動作
7. JaxRsBeanValidationHandler（バリデーション実行）
    ↓
アクションメソッド（業務ロジック）
    ↓
UniversalDao.insert()でDB登録
```

**BodyConvertHandlerの仕組み**

アクションメソッドに付与された `@Consumes` アノテーションで指定したMIMEタイプに対応するコンバータが自動選択されます。`application/json` の場合は `Jackson2BodyConverter` が使用されます。

Jersey環境の場合、`JerseyJaxRsHandlerListFactory` を設定することで `BodyConvertHandler`（JSON/XML/form対応）と `JaxRsBeanValidationHandler` が自動的にハンドラキューに追加されます：

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

**アクションクラスの実装例**

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        // BeanUtilでFormをEntityに変換し、UniversalDaoでDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` ：JSONを受け付けることを宣言。これにより `BodyConvertHandler` がJSONをFormに変換
- `@Valid` ：`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行。エラー時は `ApplicationException` が送出される
- `BeanUtil.createAndCopy(Project.class, project)` ：FormをEntityに変換
- `UniversalDao.insert()` ：EntityをDBに登録（SQL不要）
- 戻り値にステータスコード `201`（Created）を返す

**Formクラスの例**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言

    // getter/setter
}
```

**注意点**:
- `BodyConvertHandler` は `ルーティングアダプタ` よりも後ろに設定する必要があります（ルーティングアダプタが先にアクションを特定してから変換処理が行われるため）
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` よりも後ろに設定する必要があります（変換後のFormに対してバリデーションを行うため）
- `UniversalDao` の使用には `BasicDaoContextFactory` のコンポーネント定義が必要です

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6, handlers-jaxrs-bean-validation-handler.json:s4