**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたメソッドでFormを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` でDBに登録する。レスポンスはステータスコード `201` の `HttpResponse` を返すのが標準パターン。

---

**根拠**:

**1. Formクラスの作成**

クライアントから送信されたJSONを受け付けるFormを作成する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で宣言する（後述の注意点を参照）

**2. 業務アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言する。これにより、リクエストボディ変換ハンドラがJSONをFormに変換する。
- `@Valid` アノテーションでBean Validationによるバリデーションを実行する。
- `BeanUtil.createAndCopy()` でFormをエンティティクラスにコピーし、`UniversalDao.insert()` でDBに登録する。
- 戻り値はリソース作成完了を示すステータスコード `201` の `HttpResponse` を返す。
- `@Path` と `@POST` でURLとのマッピングを定義する。

**3. URLマッピング**

ルーティングアダプタを使用してURLとのマッピングを行う。上記のように `@Path("/projects")` と `@POST` アノテーションを使うJakarta RESTful Web Servicesの `@Path` アノテーション方式が推奨される。

---

**注意点**:

- Formのプロパティは**全てString型**で宣言すること。数値型など他の型に変換するのはBean Validationの後にエンティティ側で行う。
- `@Valid` アノテーションはバリデーションエラー時にはリクエスト処理がフレームワークに移譲されるため、アクションメソッド内でバリデーション失敗を明示的にハンドリングする必要はない。
- RESTfulウェブサービスでは `排他制御` ライブラリはクライアント(taglib)との連動が前提のため使用できない。楽観的ロックを行う場合はリクエストボディにバージョン番号を含める。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5