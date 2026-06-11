**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)` を付けたリソースクラスのメソッドを定義し、フォームクラスで入力を受け取って `UniversalDao.insert` でDB登録します。

**根拠**:

**1. クラス構成（責務）**

| クラス | 責務 |
|---|---|
| アクションクラス | リクエストを受け取り業務ロジックを実行、レスポンスを返却 |
| フォームクラス | HTTPボディをマッピング。バリデーションアノテーションを持つ。**プロパティは全てString** |
| エンティティクラス | テーブルと1対1対応するクラス |

**2. フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で定義する

**3. リソースクラス（アクションクラス）の実装**

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

実装のポイント:
- `@Path` でURIを定義し、`@POST` でPOSTリクエストにマッピングする
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストボディを受け付ける
- `@Valid` でリクエストのバリデーションを実行する
- `BeanUtil.createAndCopy` でフォームをエンティティに変換し、`UniversalDao.insert` でDB登録する
- 戻り値はステータスコード `201 (Created)` を表す `HttpResponse` を返す

**4. メソッドシグネチャのバリエーション**

| 引数定義 | 用途 |
|---|---|
| 引数無し | パラメータ不要な場合 |
| フォーム(Java Beans) | リクエストボディからマッピングする場合（JSON登録はこれを使用）|
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダ取得時 |
| 組み合わせ | `SampleForm form, JaxRsHttpRequest request` のように複数指定可 |

戻り値の型:
- `HttpResponse` — ステータスコードなどを細かく制御したい場合
- フォーム(Java Beans) — レスポンスボディに変換してクライアントに返す場合
- `void` — `204 NoContent` を返す場合

**注意点**:
- フォームクラスはAPI単位に作成する。登録用と更新用で似た項目があっても、APIが異なる場合は別のフォームクラスとして定義する
- `JaxRsHttpRequest` を使用する際、Jakarta RESTful Web Servicesで規定されている `@PathParam` アノテーションは使用できない（`JaxRsHttpRequest#getPathParam` で取得すること）

参照: `restful-web-service-getting-started-create.json:s1`, `restful-web-service-resource-signature.json:s1`, `restful-web-service-application-design.json:s1`