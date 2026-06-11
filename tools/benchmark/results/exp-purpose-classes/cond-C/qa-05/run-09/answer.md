**結論**: `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`アノテーションを付与したメソッドに引数としてフォームクラスを定義し、`@Valid`でバリデーション後に`BeanUtil.createAndCopy()`でエンティティへ変換し、`UniversalDao.insert()`でDBに登録する。

**根拠**:

フォームクラス（リクエストJSONのマッピング先）:

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

リソース(アクション)クラスの実装:

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

メソッドシグネチャの型対応:

| 引数の型 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディをJSONから変換して受け取る場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ | 上記の型を複数組み合わせることも可能 |

| 戻り値の型 | 説明 |
|---|---|
| `void` | ボディなし・ステータス204を返す |
| フォーム(Java Beans) | JSONに変換してレスポンスボディに出力 |
| `HttpResponse` | ステータスコードを明示して返す |

**注意点**:
- フォームのプロパティは**全てString型**で宣言すること（バリデーションルールの制約）
- `@Consumes(MediaType.APPLICATION_JSON)`を指定すると、リクエストボディ変換ハンドラがJSONをフォームに自動変換する
- Content-Typeが`application/json`でないリクエストはステータスコード`415`で拒否される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5