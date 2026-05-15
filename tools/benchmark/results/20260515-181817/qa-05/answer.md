**結論**: REST APIでJSONを受け取ってDBに登録するには、フォームクラス・アクションクラス（リソースクラス）・エンティティクラスの3層で実装する。アクションメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換後、`UniversalDao.insert()` で登録する。

**根拠**:

**1. クラス構成**

| クラス | 責務 |
|--------|------|
| フォームクラス | リクエストボディのJSONをマッピング。バリデーションアノテーションを保持 |
| アクションクラス | リクエストを元に業務ロジックを実行、レスポンスを生成 |
| エンティティクラス | テーブルと1対1対応。DBへの永続化に使用 |

**2. フォームクラスの実装**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全て `String` 型**で宣言する（Bean Validationの要件）

**3. アクションクラス（リソースクラス）の実装**

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
- `@Path` でURLをマッピング、`@POST` でPOSTリクエストにバインド
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付ける
- `@Valid` でリクエストのBean Validationを有効化
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換
- `UniversalDao.insert()` でDBへ登録
- 戻り値は `201 Created` を表す `HttpResponse`

**4. メソッドシグネチャの選択肢**

リクエストボディのみ必要な場合はフォームを引数とする。パスパラメータやクエリパラメータも必要な場合は `JaxRsHttpRequest` を組み合わせる。

```java
// フォームのみ
public HttpResponse save(ProjectForm form) { ... }

// フォーム + HTTPヘッダ等が必要な場合
public HttpResponse save(ProjectForm form, JaxRsHttpRequest request) { ... }
```

**注意点**:
- フォームクラスは**API単位**に作成すること（登録用と更新用で共通化しない）。インタフェース変更の影響範囲を限定するため
- Jakarta RESTful Web Servicesの `@PathParam` / `@QueryParam` は**使用不可**。パスパラメータは `JaxRsHttpRequest.getPathParam()` で取得する
- 楽観的ロックを行う場合は ETag/If-Match は非対応のため、リクエストボディに直接バージョン番号を含めること

参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json#s1`, `processing-pattern/restful-web-service/restful-web-service-application-design.json`, `processing-pattern/restful-web-service/restful-web-service-resource-signature.json#s1`