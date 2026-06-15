**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`BodyConvertHandler`（Jackson2BodyConverter経由）がリクエストボディをFormオブジェクトに変換し、アクションクラスで`UniversalDao.insert()`を呼ぶことでDB登録が行われる。

**根拠**:

**全体の処理の流れ**（`restful-web-service-architecture.json:s2`）

```
クライアント
  → WebFrontController（Filter）
  → ハンドラキュー
      1. グローバルエラーハンドラ
      2. JaxRsResponseHandler（レスポンス書き込み・エラー処理）
      3. データベース接続管理ハンドラ（DB接続取得/解放）
      4. トランザクション制御ハンドラ（コミット/ロールバック）
      5. ルーティングアダプタ（URIからアクション特定）
      6. BodyConvertHandler（JSONボディ→Formに変換）
      7. JaxRsBeanValidationHandler（Formへのバリデーション実行）
  → アクションクラス（業務ロジック実行）
  → クライアントへレスポンス返却
```

**JSONボディ変換の仕組み**（`handlers-body-convert-handler.json:s5`）

アクションメソッドに付与した `@Consumes` アノテーションのMIMEタイプに対応したBodyConverterが選ばれ、リクエストボディをFormへ変換する。`application/json`の場合は`Jackson2BodyConverter`が動作する。

Jersey環境では`JerseyJaxRsHandlerListFactory`を使用することで、以下のコンバータが自動設定される（`adapters-jaxrs-adaptor.json:s2`）：
- JSON: `Jackson2BodyConverter`
- XML: `JaxbBodyConverter`
- application/x-www-form-urlencoded: `FormUrlEncodedConverter`

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

**アクションクラスの実装例**（`restful-web-service-getting-started-create.json:s1`）

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

Formクラスの実装：

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**バリデーションの仕組み**（`handlers-jaxrs-bean-validation-handler.json:s4`）

`@Valid`アノテーションを付与すると、`JaxRsBeanValidationHandler`がFormオブジェクトに対してBean Validationを実行する。バリデーションエラーが発生した場合は`ApplicationException`を送出し、後続のアクション処理は実行されない。

**注意点**:
- `BodyConvertHandler`はルーティングアダプタよりも後ろのハンドラキューに設定すること（アクションのアノテーション情報が必要なため）
- Formクラスのプロパティは全て`String`型で宣言する
- `BeanUtil.createAndCopy()`でFormからEntityへ変換した後に`UniversalDao.insert()`でDB登録する
- Content-Typeとアクションの`@Consumes`が一致しない場合、ステータスコード`415`が返却される

参照: handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4