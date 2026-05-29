Step 5と6のanswer生成・検証を行います。

**結論**: リソースクラスに `@Path` と `@POST` を付け、メソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたFormを引数として受け取り、`BeanUtil.createAndCopy()` でエンティティに変換後 `UniversalDao.insert()` でDBに登録します。

**根拠**:

**①フォームの作成**

クライアントから受け取るJSONのプロパティに対応するFormクラスを作成します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> プロパティは**全てString型**で宣言する必要があります。

---

**②リソース(アクション)クラスの実装**

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

| アノテーション/API | 役割 |
|---|---|
| `@Path("/projects")` | クラスとURLパスを紐づける |
| `@POST` | HTTPメソッドと紐づける |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディのJSON→Formへの変換をリクエストボディ変換ハンドラに指示する |
| `@Valid` | JaxRs Bean ValidationハンドラによるForm検証を有効化する |
| `BeanUtil.createAndCopy(Project.class, project)` | FormをEntityに変換する |
| `UniversalDao.insert(...)` | DBへ登録する |
| `HttpResponse.Status.CREATED.getStatusCode()` | 登録完了を示すステータスコード `201` を返す |

---

**③メソッドのシグネチャ**

リクエストボディから変換されたFormを引数として受け取る場合は以下の定義になります。

```java
public HttpResponse save(SampleForm form) {
    // 省略
}
```

パスパラメータやHTTPヘッダも必要な場合は `JaxRsHttpRequest` と組み合わせられます。

```java
public HttpResponse save(SampleForm form, JaxRsHttpRequest request) {
    // 省略
}
```

**注意点**:
- `@Consumes` に設定したMIMEとリクエストヘッダの `Content-Type` が異なる場合、ステータスコード `415` (Unsupported Media Type) が返却されます。
- RESTfulウェブサービスでは `排他制御` ライブラリ（taglibと連動する機能）は使用できません。楽観的ロックを行う場合はリクエストボディにバージョン番号を含める設計にしてください。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8

---