必要なセクションが揃いました。アンサーを生成します。

---

**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Path` + `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` アノテーションを付けたメソッドでFormを受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

**1. フォームクラスの作成**

リクエストボディのJSONをマッピングするFormを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラス（アクション）の実装**

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

- `@Path` アノテーションでURLパスを指定し、`@POST` でPOSTリクエストにマッピングする
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラ（`BodyConvertHandler`）がContent-Type `application/json` に対応したコンバータでJSONをFormに変換する
- `@Valid` アノテーションでBean Validationによるバリデーションが実行される
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED`（ステータスコード `201`）を返す

**3. メソッドシグネチャの選択肢**

| 引数定義 | 用途 |
|---|---|
| `SampleForm form` | JSONリクエストボディをFormに変換して受け取る（今回のケース） |
| `JaxRsHttpRequest request` | パスパラメータ・クエリパラメータ・HTTPヘッダを扱う場合 |
| 組み合わせ `(SampleForm form, JaxRsHttpRequest request)` | ボディとHTTPヘッダ両方を扱う場合 |

**注意点**:

- フォームのプロパティは全てString型で宣言する必要がある（Bean Validationの仕様）
- `Content-Type: application/json` がリクエストヘッダに設定されていない場合、`415 Unsupported Media Type` が返される
- `@Valid` を付けないとバリデーションが実行されないため注意

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5

---