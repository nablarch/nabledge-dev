**結論:** アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、フォームクラスでJSONを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換した後 `UniversalDao.insert()` でDBに登録する。

---

**根拠:**

**処理の流れ**

NablarchのRESTfulウェブサービスでは、リクエスト受信からDB登録まで以下の流れで処理される。

1. WebフロントコントローラがHTTPリクエストを受信
2. `BodyConvertHandler`（リクエストボディ変換ハンドラ）がContent-Typeに基づいてJSONリクエストボディをフォームクラスに変換
3. `JaxRsBeanValidationHandler` がフォームクラスに対してバリデーションを実行
4. アクションメソッドがフォームクラスを受け取り業務ロジックを実行

---

**実装手順**

**① フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```
> プロパティは全て `String` 型で宣言する。

**② アクションメソッドの実装**

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

各ポイント：
- `@Path("/projects")` + `@POST` でURLとHTTPメソッドをマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを宣言（BodyConvertHandlerがこのアノテーションを元に変換処理を実行する）
- `@Valid` でJakarta RESTful Web Servcies Bean Validationハンドラによるバリデーションを実行
- `BeanUtil.createAndCopy()` でフォームクラスをエンティティクラスに変換
- `UniversalDao.insert()` でエンティティをDBに登録
- ステータスコード `201`（Created）を返す `HttpResponse` を返却

---

**ハンドラ構成の設定**

JSONを処理するには `BodyConvertHandler` にJSON対応コンバータの設定が必要。Jerseyを使用する場合、`JerseyJaxRsHandlerListFactory` を利用すると `Jackson2BodyConverter` が自動で設定される。

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

**注意点:**
- フォームのプロパティは全て `String` 型で宣言すること（バリデーション・型変換の仕組みのため）
- `BodyConvertHandler` に設定されたコンバータが対応していないMIMEタイプがContent-Typeに設定されていた場合、ステータスコード `415`（Unsupported Media Type）が返却される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2