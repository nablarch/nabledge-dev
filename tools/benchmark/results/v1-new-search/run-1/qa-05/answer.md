**結論**: RESTfulウェブサービスでJSONを受け取りDBに登録するには、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーションを付けたリソースクラスのメソッドを実装し、`BeanUtil` でフォームをエンティティに変換した後、`UniversalDao.insert()` でDB登録する。

**根拠**:

**① フォームクラスの作成**

リクエストボディを受け取るフォームを作成する。プロパティは全てString型で宣言する。

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

各ポイント:
- `@Path` アノテーションでクラスにURLプレフィックスを設定する
- `@POST` アノテーションでPOSTリクエストにマッピングする
- `@Consumes(MediaType.APPLICATION_JSON)` によりリクエストボディが `application/json` として扱われ、フォームに変換される（Content-Typeが一致しない場合はステータスコード `415` が返却される）
- `@Valid` アノテーションによりBean Validationが実行される
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値として `HttpResponse` にステータスコード `201` を指定して返却する

**③ メソッドシグネチャのまとめ**

| 引数の型 | 用途 |
|---|---|
| フォーム（Java Beans） | リクエストボディをフォームとして受け取る |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダの取得 |
| `ExecutionContext` | スコープ変数へのアクセス |

| 戻り値の型 | 説明 |
|---|---|
| `HttpResponse` | ステータスコードなどを明示的に制御する場合 |
| フォーム（Java Beans） | レスポンスボディとして変換・返却する場合 |
| `void` | `204: NoContent` を返す場合 |

**注意点**: `@Valid` アノテーションによるバリデーションエラー時のレスポンスは `JaxRsResponseHandler` が制御する。また、楽観的ロックを行う場合はリクエストボディにバージョン番号を含める必要がある（ETag/If-Matchには対応していない）。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-resource-signature.json:s1, component/handlers/handlers-body-convert-handler.json:s5