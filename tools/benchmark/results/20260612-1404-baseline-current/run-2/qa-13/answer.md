**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、①JSONを受け取るFormクラス作成 → ②`@Valid`アノテーションでバリデーション → ③`BeanUtil.createAndCopy`でEntityに変換 → ④`UniversalDao.insert`でDB登録、という4ステップで実装します。

**根拠**:

**1. Formクラスの作成**

クライアントから受け取る値を保持するFormを作成します。プロパティは必ず全て`String`型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> **注意点**: プロパティを`String`以外の型にすると、不正な値が送信された際にBean変換処理が失敗し、バリデーションエラーとして返せなくなります。外部からの値は必ず`String`で受け取り、バリデーション後に変換してください。

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付けることを指定。リクエストボディ変換ハンドラがJSONをFormに変換します
- `@Valid`: Jakarta RESTful Web Services Bean ValidationハンドラがFormに対してバリデーションを実行します。エラー時は`ApplicationException`が送出され、後続処理には進みません
- `@Path("/projects")` + `@POST`: ルーティングアダプタがPOSTリクエストとURLをこのメソッドにマッピングします
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換します
- `UniversalDao.insert(...)`: Jakarta PersistenceアノテーションをEntityに付けることでSQLを書かずにDB登録できます
- レスポンスとしてステータスコード`201`（リソース作成完了）を返します

**3. EntityクラスへのJakarta Persistenceアノテーション付与**

`UniversalDao.insert`でSQLを自動生成するために、EntityクラスにJakarta Persistenceアノテーションを付与します（`@Table`、`@Id`、`@Column`など）。

**注意点**:

- Content-Typeヘッダが`@Consumes`に指定したMIMEタイプと異なる場合、ステータスコード`415`が返ります
- `UniversalDao`では主キー以外の条件を指定した更新/削除はできないため、その場合はJDBCラッパー（`データベースアクセス`）を使用してください
- `UniversalDao`は共通項目（登録ユーザ、更新ユーザ等）の自動設定機能を持ちません。必要な場合は、insertの前にアプリケーションで明示的に値をセットしてください

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, libraries-bean-validation.json:s8