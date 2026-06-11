**結論**: JSONを受け取ってDBに登録するリソースクラスは、`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` アノテーションを組み合わせて実装し、`BeanUtil.createAndCopy` でフォームをエンティティに変換後、`UniversalDao.insert` でDBに登録する。ステータスコード201を `HttpResponse` で返却する。

---

**根拠**:

**① フォームクラスの作成**

クライアントから送信されたJSONを受け取るフォームを作成する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> プロパティは全てString型で宣言する。

---

**② リソースクラスの実装**

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

各アノテーション・APIの役割:

| 要素 | 説明 |
|---|---|
| `@Path("/projects")` | クラスをURLパス `/projects` にマッピングする |
| `@POST` | POSTリクエストをこのメソッドにマッピングする |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストをJSON形式で受け付け、`BodyConvertHandler` がJSONをフォームに変換する |
| `@Valid` | `JaxRsBeanValidationHandler` によりフォームのBean Validationを実行する。バリデーションエラー時は `ApplicationException` が送出される |
| `BeanUtil.createAndCopy(Project.class, project)` | フォームをエンティティクラスに変換する |
| `UniversalDao.insert(...)` | エンティティをDBに登録する |
| `HttpResponse(HttpResponse.Status.CREATED.getStatusCode())` | ステータスコード201（リソース作成完了）を返却する |

---

**③ URLマッピングの設定（`@Path` アノテーション方式）**

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定し、`JaxRsPathOptionsProvider` に `applicationPath`（共通プレフィックス）と `basePackage`（`@Path` を持つクラスの検索対象パッケージ）を指定する。設定したコンポーネントは初期化対象リストへの追加も必要。

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
  ...
</component>
```

---

**注意点**:

- フォームのプロパティは全て `String` 型で宣言すること
- パスパラメータが必要な場合は、Jakarta RESTful Web Services の `@PathParam` は使用できない。`JaxRsHttpRequest` の `getPathParam(String name)` を使用すること
- `@Consumes` に設定したMIMEと異なる `Content-Type` が送られた場合はステータスコード `415` が返却される
- JBoss/WildFly など一部のサーバでは `@Path` アノテーション方式が使用できない。その場合はXMLによるルーティング定義を使用すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8