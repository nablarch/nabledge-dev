**結論**: NablarchのRESTful Webサービスで「JSONを受け取ってDBに登録する」には、①フォームクラス（リクエストJSONのマッピング先）、②アクションクラス（`@Path` / `@POST` / `@Consumes(APPLICATION_JSON)` を付けた業務メソッド）の2つを実装し、`BeanUtil.createAndCopy` でフォームをエンティティに変換して `UniversalDao.insert` でDBに登録する。

---

**根拠**:

#### 1. クラス設計の全体像

| クラス | 役割 |
|--------|------|
| フォームクラス | リクエストボディ（JSON）をマッピング。バリデーションアノテーションを持つ。**プロパティは全て `String` 型** で定義する |
| アクションクラス | リクエストを受け取り業務ロジックを実行し、レスポンスを返す |
| エンティティクラス | テーブルと1対1に対応するクラス |

#### 2. フォームクラスの実装

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 3. アクションクラスの実装

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

**実装ポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することでリクエストボディのJSONをフォームに自動変換する
- `@Valid` アノテーションでリクエストのBean Validationを実行する
- `BeanUtil.createAndCopy` でフォームをエンティティに変換する
- `UniversalDao.insert` でDBに登録する
- 戻り値は `HttpResponse` でステータスコード `201`（リソース作成完了）を返す
- `@Path` と `@POST` でURLマッピングを定義する（ルーティングアダプタ経由）

---

**注意点**:
- フォームクラスのプロパティは数値・日付も含めて **全て `String` 型** で定義すること（Bean Validationの制約）
- 登録用と更新用でAPIが異なる場合は、**フォームクラスをAPI単位で別クラスとして作成**する（インタフェース変更の影響範囲を限定するため）
- `@PathParam`（Jakarta RESTful Web Services標準）は使用できない点に注意

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-application-design.json, restful-web-service-resource-signature.json:s1