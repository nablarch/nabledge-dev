**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` を付けたアクションメソッドを作成し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換して `UniversalDao.insert()` を呼び出す。フレームワーク側では `BodyConvertHandler` がJSONボディをFormに自動変換し、`JaxRsBeanValidationHandler` がバリデーションを実行する。

---

**根拠**:

**処理の流れ（アーキテクチャ）**

```
クライアント
  → WebFrontController（jakarta.servlet.Filter）
  → ハンドラキュー
      → グローバルエラーハンドラ
      → JaxRsResponseHandler（レスポンス生成）
      → データベース接続管理ハンドラ（DB接続取得・解放）
      → トランザクション制御ハンドラ（コミット/ロールバック）
      → ルーティングアダプタ（URI→アクション解決）
      → BodyConvertHandler（JSON→Formに変換）  ← ここでJSONを受け取る
      → JaxRsBeanValidationHandler（バリデーション）
      → アクションクラス（業務ロジック→UniversalDao.insert()）
```

**フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
    // プロパティは全てString型で宣言する
}
```

**アクションクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: `BodyConvertHandler` がこのアノテーションを見て `Jackson2BodyConverter` でJSONボディを `ProjectForm` に変換する
- `@Valid`: `JaxRsBeanValidationHandler` がFormのバリデーションを実行する
- `BeanUtil.createAndCopy()`: FormのString型プロパティをEntityの各型に変換してコピーする
- `UniversalDao.insert()`: Jakarta PersistenceアノテーションからINSERT文を自動生成してDBに登録する
- 戻り値の `HttpResponse(201)`: リソース作成完了を示すステータスコード

**JSONコンバータの仕組み**

Jerseyを使う場合、`JerseyJaxRsHandlerListFactory` をファクトリインジェクションするだけで `BodyConvertHandler` に `Jackson2BodyConverter`（JSON）・`JaxbBodyConverter`（XML）・`FormUrlEncodedConverter` が自動設定される:

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

**ユニバーサルDAOの設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- フォームのプロパティは全て `String` 型で宣言する（バリデーション前に型変換エラーが起きないようにするため）
- `BodyConvertHandler` はルーティングアダプタより後ろに設定する必要がある（アクションのアノテーション情報が必要なため）
- サポートしていないMedia Typeのリクエストが来た場合、ステータスコード `415` が返却される

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s1, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6