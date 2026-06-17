**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、Formクラスを作成してJSONリクエストを受け取り、`BeanUtil.createAndCopy()`でEntityに変換した後、`UniversalDao.insert()`でDB登録します。バリデーションは`@Valid`アノテーションで行います。

**根拠**:

**1. Formクラスの作成**

クライアントから送信された値を受け付けるFormを作成します。プロパティは必ず全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` アノテーションを付けることで、`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する（バリデーションエラー時は`ApplicationException`が送出され、登録処理は実行されない）
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換する
- `UniversalDao.insert(entity)` でDB登録する
- 戻り値にステータスコード201（Created）を表す`HttpResponse`を返す
- `@Path("/projects")` + `@POST` でURLとのマッピングを定義する

**3. コンポーネント定義（ユニバーサルDAOの設定）**

`UniversalDao`を使用するには、コンポーネント定義に以下を追加します。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは必ずすべて`String`型で宣言すること。String以外の型を使うと、不正な値が送信された場合にバリデーション前のBean変換処理で予期せぬ例外が発生する
- RESTfulウェブサービスでは `ETag` / `If-Match` を使った楽観的ロックには対応していないため、楽観的ロックが必要な場合はリクエストボディにバージョン番号を含めること

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6, libraries-bean-validation.json:s8