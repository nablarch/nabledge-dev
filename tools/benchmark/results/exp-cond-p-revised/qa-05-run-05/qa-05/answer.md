**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`アノテーションを付けた業務アクションメソッドを実装し、`BeanUtil.createAndCopy`でEntityに変換後、`UniversalDao.insert`でDBに登録します。

**根拠**:

**1. Formクラスの作成**

クライアントから受け取るJSON項目に対応するFormクラスを作成します。プロパティは全て`String`型で宣言します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> **注意**: Beanクラスのプロパティは全てString型として定義すること。外部からの値をString以外の型に変換したい場合には、バリデーション実施後に変換すること。

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラ（`BodyConvertHandler`）がJSONをFormに変換します
- `@Valid` アノテーションを付けることで、JAX-RS Bean Validationハンドラがバリデーションを実行します
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換します
- `UniversalDao.insert(...)` でDBに登録します
- ステータスコード`201`（リソース作成完了）を表す`HttpResponse`を返します
- `@Path("/projects")` と `@POST` でURLとHTTPメソッドのマッピングを定義します

**3. ユニバーサルDAOの設定**

`BasicDaoContextFactory` をコンポーネント設定ファイルに追加します（データベースアクセス(JDBCラッパー)の設定も別途必要）。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `Content-Type: application/json` 以外のリクエストが来た場合、ステータスコード`415`（サポートしていないメディアタイプ）が返却されます
- RESTfulウェブサービスのユーザ入力値チェックの詳細は「Jakarta RESTful Web Servcies Bean Validationハンドラ」を参照してください

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/libraries/libraries-bean-validation.json:s17, component/libraries/libraries-bean-validation.json:s8, component/libraries/libraries-universal-dao.json:s6