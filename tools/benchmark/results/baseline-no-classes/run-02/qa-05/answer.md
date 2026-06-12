**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションをメソッドに付与し、引数としてFormクラスを受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

#### 1. Formクラスの作成

クライアントから受け取るJSONのフィールドに対応するFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. 業務アクションメソッドの実装

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

- `@Consumes(MediaType.APPLICATION_JSON)` — JSONリクエストボディを受け付けることを宣言する。リクエストヘッダの `Content-Type` が `application/json` と一致しない場合、ステータスコード `415` が返却される。
- `@Valid` — メソッドの引数(Form)に対してBean Validationを実行する。バリデーションエラーが発生した場合はエラーレスポンスが返却される。
- `BeanUtil.createAndCopy(Project.class, project)` — FormのプロパティをEntityにコピーして新しいインスタンスを生成する。
- `UniversalDao.insert(...)` — Jakarta PersistenceアノテーションをEntityに付けるだけでSQLを書かずにDBへの登録ができる。
- 戻り値として `HttpResponse.Status.CREATED`（ステータスコード `201`）を返却する。

#### 3. URLマッピング

`@Path` アノテーションでクラスとURLを紐づけ、`@POST` アノテーションでHTTPメソッドを指定する（ルーティングアダプタを使用）。

**注意点**:
- Formのプロパティは全てString型で宣言すること（バリデーションルールの設定方法に準拠）
- Entityには `@Table`、`@Id`、`@Column` 等のJakarta PersistenceアノテーションをEntityに付与しておく必要がある

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4