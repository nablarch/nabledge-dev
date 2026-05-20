**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーションを付けたアクションメソッドで、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDB登録する。

**根拠**:

**1. Formクラスの作成**

クライアントから送信された値を受け付けるFormクラスを作成する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で宣言する。

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

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディをJSON形式で受け付ける。リクエストボディ変換ハンドラ（`BodyConvertHandler`）が、このアノテーションに基づいてリクエストボディをFormに変換する。
- `@Valid`: `JaxRsBeanValidationHandler` がこのアノテーションを検知してBean Validationを実行する。バリデーションエラー時は `ApplicationException` が送出される。
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する。
- `UniversalDao.insert(...)`: EntityのJakarta Persistenceアノテーション情報を元にINSERT SQLを自動生成してDB登録する。
- 戻り値: リソース作成完了を示すHTTPステータスコード `201` を返す。

**注意点**:
- `BodyConvertHandler` は `ルーティングアダプタ` より後ろ、`JaxRsBeanValidationHandler` は `BodyConvertHandler` より後ろのハンドラキューに設定する必要がある。
- `UniversalDao` を使用するには、`BasicDaoContextFactory` のコンポーネント定義が必要。
- `UniversalDao.insert()` は主キーを使ったCRUDに対応しているが、主キー以外の条件を指定した更新・削除はJDBCラッパー（データベースアクセス）を使用すること。

参照: `restful-web-service-getting-started-create.json:s1`, `handlers-body-convert-handler.json:s5`, `handlers-jaxrs-bean-validation-handler.json:s4`