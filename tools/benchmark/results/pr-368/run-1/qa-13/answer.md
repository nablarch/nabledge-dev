**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、リソースクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、Formを引数で受け取る。その後 `BeanUtil.createAndCopy` でEntityに変換し、`UniversalDao.insert` でDBに登録して、ステータスコード201の `HttpResponse` を返却する。

---

**根拠**:

**① Formクラスの作成**

クライアントから送信された値を受け付けるFormクラスを作成する。プロパティは全てString型で宣言し、バリデーションアノテーションを付与する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスの実装（URLマッピングとアクションメソッド）**

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

- `@Path` と `@POST` でURLとメソッドをマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストボディを受け付ける。指定したMIMEと異なるContent-Typeが送られた場合はステータスコード `415` を返却する
- `@Valid` でFormに定義したバリデーションルールを実行する
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換する
- `UniversalDao.insert(...)` でEntityをDBに登録する（SQL記述不要）
- 戻り値はリソース作成完了を示すステータスコード `201` の `HttpResponse`

**③ UniversalDAOのコンポーネント設定**

`UniversalDao` を使用するには、コンポーネント定義に `BasicDaoContextFactory` を設定する。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**④ Entityクラスの定義**

Entityには Jakarta Persistence アノテーションを付与することで、SQLなしにCRUD（登録を含む）が利用できる。主キーに採番が必要な場合は `@GeneratedValue` を使用する。

```java
@Entity
@Table(name = "PROJECT")
public class Project {

    @Id
    @Column(name = "PROJECT_ID")
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "seq")
    @SequenceGenerator(name = "seq", sequenceName = "PROJECT_ID_SEQ")
    private Long projectId;

    // 他フィールドおよびゲッタ・セッタは省略
}
```

---

**注意点**:
- `@Consumes` に指定したMIMEと異なるContent-Typeがリクエストに設定されている場合、ステータスコード `415` が返却される
- Formのプロパティは全てString型で宣言すること（バリデーションの仕様による）

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-body-convert-handler.json:s5, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6, libraries-universal-dao.json:s13