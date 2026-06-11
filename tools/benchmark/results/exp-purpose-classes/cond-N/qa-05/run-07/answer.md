**結論**: JSONを受け取ってDBに登録するには、フォームクラスとリソースクラスを作成し、`@Path`/`@POST`/`@Consumes(MediaType.APPLICATION_JSON)`/`@Valid` を組み合わせて実装する。DB登録は `BeanUtil.createAndCopy()` でフォームをエンティティに変換後、`UniversalDao.insert()` で行い、ステータスコード `201` を返す。

---

**根拠**:

#### 1. フォームクラスを作成する

クライアントから受け取るJSONのフィールドに対応したフォームを作成する。プロパティは**全て `String` 型**で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. リソースクラスを実装する

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

**各アノテーションのポイント**:

| アノテーション | 役割 |
|---|---|
| `@Path("/projects")` | クラスをURLパス `/projects` にマッピング |
| `@POST` | POSTリクエストをこのメソッドにマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | JSONリクエストボディをフォームに変換（リクエストボディ変換ハンドラが処理） |
| `@Valid` | フォームのBean Validationを実行（バリデーションエラー時は `ApplicationException` を送出） |

#### 3. 処理フロー

1. JSONリクエストボディ → リクエストボディ変換ハンドラが `ProjectForm` に変換
2. `@Valid` → Bean Validationハンドラがバリデーションを実行
3. `BeanUtil.createAndCopy(Project.class, project)` → フォームをエンティティに変換
4. `UniversalDao.insert(entity)` → DBに登録
5. `new HttpResponse(201)` → 登録完了レスポンス（ステータスコード `201 Created`）を返却

#### メソッド引数・戻り値のバリエーション

| 引数/戻り値 | 説明 |
|---|---|
| `SampleForm form` | JSONボディをフォームに変換して受け取る場合 |
| `JaxRsHttpRequest request` | パスパラメータ・クエリパラメータ・ヘッダが必要な場合 |
| `void` | `204 NoContent` を返す場合 |
| `HttpResponse` | ステータスコードを明示したい場合 |
| フォーム(Java Beans) | レスポンスボディにJSONを返す場合 |

**注意点**: `@QueryParam` や `@PathParam`（Jakarta RESTful Web Services標準のアノテーション）は使用できない。パスパラメータ・クエリパラメータは `JaxRsHttpRequest` から取得すること。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8