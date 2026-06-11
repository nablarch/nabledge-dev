**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を組み合わせたアクションクラスを実装し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換後、`UniversalDao.insert()` でDBに登録する。

---

**根拠**:

### クラス構成

| クラス | 責務 |
|--------|------|
| アクションクラス | 業務ロジックを実行し、レスポンスを返却する |
| フォームクラス | リクエストボディ（JSONのhttp body）をマッピングし、バリデーションアノテーションを持つ |
| エンティティクラス | テーブルと1対1で対応するクラス |

### フォームクラスの実装

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する

    // ゲッタ及びセッタは省略
}
```

### アクションクラスの実装

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

### 実装のポイント

- **`@Consumes(MediaType.APPLICATION_JSON)`**: JSONリクエストを受け付けるために指定する。`BodyConvertHandler` がこのアノテーションを元にリクエストボディをフォームに変換する。Content-Typeが一致しない場合は `415` を返却する
- **`@Valid`**: フォームに対してBean Validationを実行する。バリデーションエラー時は `ApplicationException` がスローされる
- **`BeanUtil.createAndCopy()`**: フォームをエンティティクラスに変換する
- **`UniversalDao.insert()`**: エンティティをDBに登録する
- **ステータスコード201**: リソース作成完了を示す `HttpResponse.Status.CREATED.getStatusCode()` を返却する

### フォームクラス設計の注意点

- フォームクラスのプロパティは**全て `String` 型**で定義する（Bean Validationの制約）
- フォームクラスは**API単位**に作成する（登録用と更新用は別クラスにする）

---

**注意点**:

- `@Consumes` に設定されたMIMEとリクエストの `Content-Type` が異なる場合、`415 Unsupported Media Type` が返却される
- `JaxRsHttpRequest` は `HttpRequest` より優先して使用すること（後方互換性のためのみ `HttpRequest` も使用可）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, restful-web-service-application-design.json