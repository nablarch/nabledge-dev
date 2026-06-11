**結論**: リソースクラスは `@Path`・`@POST`・`@Consumes(APPLICATION_JSON)`・`@Valid` を付けたメソッドを持つJavaクラスとして実装し、受け取ったフォームを `BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` でDB登録、ステータスコード201の `HttpResponse` を返すパターンが基本形です。

---

**根拠**:

**① フォームクラス（入力値受け取り用）**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② 業務アクションメソッド（リソースクラス）**

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

**実装のポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` を付けることで、BodyConvertHandler が `application/json` に対応した `BodyConverter`（Jackson2BodyConverter）を使ってリクエストボディをフォームクラスに変換する
- `@Valid` を付けることで、JaxRsBeanValidationHandler がフォームに対してBean Validationを実行する
- `BeanUtil.createAndCopy()` でフォームをエンティティにコピーし、`UniversalDao.insert()` でSQL不要にDB登録できる（エンティティにJakarta Persistenceアノテーションを付けておく必要がある）
- 戻り値は `HttpResponse` を使って任意のステータスコードを返せる（登録成功時は `201`）

**③ リソースクラスのメソッドシグネチャの種類**

| 引数 | 用途 |
|------|------|
| 引数なし | パラメータ・ボディ不要の場合 |
| フォーム(Java Beans) | リクエストボディをフォームに変換して処理する場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 例: `save(SampleForm form, JaxRsHttpRequest request)` |

戻り値は `void`（204）・フォーム（BodyConvertHandlerがレスポンスボディに変換）・`HttpResponse` のいずれかを使用できる。

**④ 処理の流れ（仕組み）**

```
リクエスト受信
  → WebFrontController
  → ハンドラキュー
      RoutingAdapter（URIでアクションクラスを特定）
      → BodyConvertHandler（JSON → Formに変換 /@Consumes に従う）
      → JaxRsBeanValidationHandler（@Valid でバリデーション実行）
      → アクションクラスのメソッド（業務ロジック実行）
  → JaxRsResponseHandler（HttpResponse をクライアントへ返却）
```

ハンドラのJSON変換はJersey環境の場合 `JerseyJaxRsHandlerListFactory` を使うことで `Jackson2BodyConverter` が自動設定される:

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

---

**注意点**:
- フォームクラスのプロパティは**全てString型**で宣言すること。String以外の型が存在すると、不正な値が入力された場合にBeanへの変換処理が失敗して予期せぬ例外が発生する
- BodyConvertHandler は RoutingAdapter よりも後ろに設定する必要がある（アクションクラスのアノテーション情報を参照して変換処理を行うため）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, adapters-jaxrs-adaptor.json:s2, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, libraries-bean-validation.json:s8