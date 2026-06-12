**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`@Valid` と `@Consumes(MediaType.APPLICATION_JSON)` を付けたアクションメソッドでフォームクラスを受け取り、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録します。ステータスコード `201` の `HttpResponse` を返します。

---

**根拠**:

**1. フォームクラスの作成**

クライアントから送信された値を受け付けるフォームクラスを作成します。プロパティは**全てString型**で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. アクションメソッドの実装**

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
- `@Valid` でリクエストのバリデーションを実行する
- `BeanUtil.createAndCopy` でフォームをエンティティに変換する
- `UniversalDao.insert` でDBに登録する
- ステータスコード `201`（リソース作成完了）の `HttpResponse` を返す

**3. エンティティクラスの作成**

Jakarta PersistenceアノテーションをEntityクラスに設定することで、`UniversalDao.insert` がSQL文を自動生成してDBに登録します。

```java
@Entity
@Table(name = "PROJECT")
public class Project {

    @Id
    @Column(name = "PROJECT_ID")
    private Long projectId;

    @Column(name = "PROJECT_NAME")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

---

**注意点**:

- **フォームのプロパティは必ずString型で宣言すること**: Bean Validationでは入力値をBeanに変換した後でバリデーションが実施されるため、String以外の型があると不正値入力時にBeanへの変換処理が失敗し予期せぬ例外が発生する。
- **ハンドラキューの設定**: DB登録処理には「データベース接続管理ハンドラ」「トランザクション制御ハンドラ」「リクエストボディ変換ハンドラ（BodyConvertHandler）」「Jakarta RESTful Web Servcies Bean Validationハンドラ（JaxRsBeanValidationHandler）」が必要。Jakarta RESTful Web Servicesアダプタを使用した場合、BodyConvertHandlerとJaxRsBeanValidationHandlerは自動的にハンドラキューに追加される。
- **バリデーションルールの管理**: 個別にアノテーションを設定するより `@Domain` アノテーションによるドメインバリデーションを使用することが推奨される。`@Required` はドメインBeanではなく個別のFormクラス側に設定する。

参照: `restful-web-service-getting-started-create.json:s1`, `restful-web-service-architecture.json:s4`, `libraries-universal-dao.json:s2`, `libraries-universal-dao.json:s24`, `libraries-bean-validation.json:s8`, `libraries-bean-validation.json:s17`, `libraries-bean-validation.json:s9`, `adapters-router-adaptor.json:s8`

---