**結論**: REST APIでJSONを受け取ってDBに登録するには、リソースクラスに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)` を付けたメソッドを定義し、フォームで受け取った値を `BeanUtil` でエンティティに変換して `UniversalDao.insert()` で登録する。

**根拠**:

**1. フォームクラスの作成**

リクエストボディのJSONを受け取るフォームを定義する。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ
}
```

**2. リソースクラスの実装**

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

**メソッドシグネチャの選択肢**（リソースクラスメソッドの引数）:

| 引数定義 | 用途 |
|---|---|
| `フォーム(Java Beans)` | リクエストボディからJSONを受け取る場合（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを扱う場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 例: `(SampleForm form, JaxRsHttpRequest request)` |

**3. 登録処理のポイント**

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付けることを宣言
- `@Valid`: リクエストのバリデーションを実行（Jakarta RESTful Web Services Bean Validationハンドラが処理）
- `BeanUtil.createAndCopy(Project.class, project)`: フォームをエンティティに変換
- `UniversalDao.insert(...)`: SQLを書かずにINSERT文を自動生成して実行（Jakarta Persistenceアノテーションを元に構築）
- 戻り値: ステータスコード `201 Created` を返す `HttpResponse`

**注意点**:
- フォームのプロパティは全て `String` 型で宣言すること（バリデーションルールの設定方法に準拠）
- `UniversalDao` は共通項目（登録ユーザ・更新ユーザ等）の自動設定機能を持たない。共通項目の自動設定が必要な場合は、`insert()` 呼び出し前にアプリケーション側で明示的に設定するか、Domaアダプタのエンティティリスナー機能を使用すること
- Jakarta RESTful Web Servicesの `@PathParam` や `@QueryParam` はNablarchでは使用不可。パスパラメータが必要な場合は `JaxRsHttpRequest.getPathParam()` を使用すること

参照: `restful-web-service-getting-started-create.json#s1`, `restful-web-service-resource-signature.json#s1`, `libraries-universal-dao.json#s2`