**結論**: JSONを受け取ってDBに登録するリソースクラスのメソッドには、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーションを付与し、引数にFormクラスを受け取る。メソッド内では `BeanUtil.createAndCopy` でFormをエンティティに変換し、`UniversalDao.insert` でDB登録する。

---

**根拠**:

**① フォームクラスの作成**

クライアントから送信された値を受け付けるFormクラスを作成する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する（型変換はバリデーション後に行う）

---

**② 業務アクションメソッドの実装**

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

各アノテーション・メソッドの役割:

| 要素 | 役割 |
|------|------|
| `@Path("/projects")` | URLとクラスをマッピング |
| `@POST` | POSTリクエストをこのメソッドにマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストをJSON形式で受け付ける（`BodyConvertHandler` がJSONをFormに変換） |
| `@Valid` | Bean Validationを実行する（`JaxRsBeanValidationHandler` が処理） |
| `BeanUtil.createAndCopy(Project.class, project)` | FormをEntityに変換 |
| `UniversalDao.insert(...)` | DBに登録 |
| `HttpResponse.Status.CREATED.getStatusCode()` | ステータスコード `201` を返す |

---

**③ リソースクラスのメソッドシグネチャ一覧**

**メソッド引数**:

| 引数定義 | 説明 |
|----------|------|
| 引数無し | パラメータ・リクエストボディ不要の場合 |
| フォーム (Java Beans) | リクエストボディから変換したFormで処理する場合（JSON登録のメインパターン） |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータを扱う場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 上記を複数組み合わせることも可能（例: `save(SampleForm form, JaxRsHttpRequest request)`） |

**メソッド戻り値**:

| 戻り値の型 | 動作 |
|------------|------|
| `void` | `204 No Content` を返す |
| フォーム (Java Beans) | `BodyConvertHandler` がレスポンスボディに変換して返す |
| `HttpResponse` | `HttpResponse` の情報をそのまま返す |

---

**④ リクエストボディ変換の仕組み**

`BodyConvertHandler` が `@Consumes` アノテーションを参照し、対応する `BodyConverter` でリクエストボディをFormに変換する。Content-Typeが `@Consumes` と異なる場合はステータスコード `415` を返す。

```java
// application/jsonリクエストはBodyConverterが自動的にPersonに変換する
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse saveJson(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

---

**注意点**:
- バリデーションエラー時は `ApplicationException` が送出され、後続処理は実行されない
- RESTfulウェブサービスでは ETag/If-Match による楽観的ロックは対応していない。バージョン番号をリクエストボディに含めること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4