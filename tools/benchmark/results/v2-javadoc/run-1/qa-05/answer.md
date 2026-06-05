Javadocセクションは内容が薄いため、主要な知識セクションで回答を生成します。

これまでのセクション収集結果を元に、回答を生成します。

**selected_pages（Step 3）:**

1. `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json` — REST登録機能の実装例そのものを含む
2. `processing-pattern/restful-web-service/restful-web-service-resource-signature.json` — リソースクラスのメソッドシグネチャ・引数・戻り値の仕様
3. `processing-pattern/restful-web-service/restful-web-service-feature-details.json` — 入力バリデーション・DBアクセスへの参照を含む
4. `component/handlers/handlers-body-convert-handler.json` — JSONリクエストボディ変換の仕組み
5. `component/handlers/handlers-jaxrs-bean-validation-handler.json` — バリデーションハンドラの使い方
6. `component/adapters/adapters-router-adaptor.json` — `@Path`/`@POST`によるルーティング定義
7. `component/libraries/libraries-universal-dao.json` — DBへのinsert処理

**回答生成（Step 5）:**

---

**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` アノテーションを付けたメソッドを実装し、`BeanUtil` でフォームをエンティティに変換した上で `UniversalDao.insert()` で登録する。

**根拠**:

全体の実装は3つの要素で構成される。

**① フォームクラスの作成**

JSONのリクエストボディを受け取るフォームを作る。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスのメソッド実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディがリクエストボディ変換ハンドラによりフォームに変換される
- `@Valid` を付けることで `JaxRsBeanValidationHandler` がフォームに対してBean Validationを実行する
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換する
- `UniversalDao.insert()` でDBに登録する
- 戻り値に `new HttpResponse(HttpResponse.Status.CREATED.getStatusCode())` を返してステータスコード `201` を返却する

**③ ルーティングの定義**

`@Path` アノテーション（クラスレベル）と `@POST` アノテーション（メソッドレベル）を組み合わせることで、`POST /projects` がこのメソッドにディスパッチされる。

**メソッドシグネチャの選択肢**:

| 引数の型 | 用途 |
|---|---|
| フォーム (Java Beans) | リクエストボディをフォームに変換して受け取る（本ケース） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する |
| `ExecutionContext` | スコープ変数にアクセスする |

戻り値は `void`（204 NoContent）、フォーム（レスポンスボディとして返す）、`HttpResponse`（ステータスコード等を指定する）から選択できる。

**注意点**: `Content-Type` が `@Consumes` に指定したMIMEタイプと異なる場合、ステータスコード `415`（Unsupported Media Type）が返却される。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-resource-signature.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-router-adaptor.json:s8

---

**Step 6: Verify**

クレームの検証:
1. `@Consumes(MediaType.APPLICATION_JSON)` でリクエストボディがフォームに変換される → s5に明示あり ✅
2. `@Valid` でBean Validationが実行される → s4に明示あり ✅
3. `BeanUtil.createAndCopy` でフォームをエンティティに変換 → s1に明示あり ✅
4. `UniversalDao.insert()` でDB登録 → s1に明示あり ✅
5. ステータスコード `201` を返却 → s1に明示あり ✅
6. `Content-Type` 不一致時に `415` を返す → s5に明示あり ✅
7. `@Path`・`@POST` でルーティング → s8に明示あり ✅
8. プロパティは全て `String` 型で宣言する → s1に明示あり ✅

**verify_result = PASS**

---

**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付けたメソッドを実装し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換した後に `UniversalDao.insert()` でDBに登録する。

**根拠**:

全体の実装は3つの要素で構成される。

**① フォームクラスの作成**

JSONのリクエストボディを受け取るフォームを作る。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスのメソッド実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定すると、リクエストボディ変換ハンドラがJSONをフォームに変換して渡してくれる
- `@Valid` を付けると、`JaxRsBeanValidationHandler` がフォームに対してBean Validationを自動実行する
- `BeanUtil.createAndCopy(Project.class, project)` でフォームをDBエンティティに変換する
- `UniversalDao.insert()` でDBに登録する
- ステータスコード `201`（Created）を返すには `new HttpResponse(HttpResponse.Status.CREATED.getStatusCode())` を返却する

**③ ルーティングの定義**

`@Path`（クラスレベル）+ `@POST`（メソッドレベル）を組み合わせることで、`POST /projects` がこのメソッドにディスパッチされる。

**メソッドシグネチャの選択肢**（用途に応じて引数を選ぶ）:

| 引数の型 | 用途 |
|---|---|
| フォーム (Java Beans) | リクエストボディをフォームとして受け取る（本ケース） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する |
| `ExecutionContext` | スコープ変数にアクセスする |
| 組み合わせ | 上記を複数組み合わせることも可能 |

**注意点**: リクエストの `Content-Type` が `@Consumes` に指定したMIMEタイプと一致しない場合、ステータスコード `415`（Unsupported Media Type）が返却される。

参照:
- processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1
- processing-pattern/restful-web-service/restful-web-service-resource-signature.json:s1
- component/handlers/handlers-body-convert-handler.json:s5
- component/handlers/handlers-jaxrs-bean-validation-handler.json:s4
- component/adapters/adapters-router-adaptor.json:s8

---