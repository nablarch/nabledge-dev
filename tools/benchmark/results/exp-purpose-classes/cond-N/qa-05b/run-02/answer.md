**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Path`/`@POST`でURLをマッピングし、`@Consumes(MediaType.APPLICATION_JSON)` + `@Valid`を付けたメソッドでFormを受け取り、`BeanUtil.createAndCopy()`でEntityに変換して`UniversalDao.insert()`でDBに登録する。

---

**根拠**:

**① Formクラスの作成**

リクエストボディを受け取るFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスの実装**

`@Path`・`@POST`でURLをマッピングし、メソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付ける。

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

- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストボディをJSON形式で受け付ける。`BodyConvertHandler`がこのアノテーションを参照してFormへの変換形式を決定する。
- `@Valid` — `JaxRsBeanValidationHandler`が、このアノテーションが付いたメソッドのFormに対してBean Validationを実行する。
- `BeanUtil.createAndCopy(Project.class, project)` — FormをEntityに変換する。
- `UniversalDao.insert(...)` — EntityをDBに登録する。SQLを書かずにCRUDが実行できる。
- 戻り値の`HttpResponse(201)` — リソース作成完了を示すステータスコード201を返す。

**③ メソッドシグネチャのバリエーション**

引数・戻り値には以下の型が使える。

| 引数 | 用途 |
|---|---|
| フォーム (Java Beans) | リクエストボディから変換したFormを処理する場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 上記を複数組み合わせて定義できる |

| 戻り値 | 説明 |
|---|---|
| `HttpResponse` | ステータスコードを明示して返す場合 |
| フォーム (Java Beans) | `BodyConvertHandler`がレスポンスボディに変換する場合 |
| `void` | ボディが空の204 NoContentを返す場合 |

**④ ハンドラキューの必須設定**

JSON受信・バリデーションを動作させるには、ハンドラキューに以下が必要。

| ハンドラ | 役割 |
|---|---|
| `BodyConvertHandler` | リクエストボディをFormに変換し、レスポンスボディへの逆変換も行う |
| `JaxRsBeanValidationHandler` | `@Valid`付きメソッドのFormにバリデーションを実行する |

`JaxRsアダプタ`を使用している場合は、これらが自動的にハンドラキューに追加される。

---

**注意点**:

- Formのプロパティは全てString型で宣言すること（バリデーション仕様のため）
- `@Consumes`に設定したMIMEとリクエストのContent-Typeが異なる場合はステータスコード`415`が返る
- EntityクラスにはJakarta Persistenceアノテーション（`@Entity`、`@Table`、`@Id`、`@Column`等）を設定する必要がある

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2