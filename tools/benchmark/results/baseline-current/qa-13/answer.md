**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、Formクラスの作成 → `@POST` + `@Valid` + `@Consumes` によるアクションメソッド定義 → `BeanUtil.createAndCopy` でエンティティ変換 → `UniversalDao.insert` でDB登録、という流れで実装します。

**根拠**:

**① フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ・セッタは省略
}
```

- プロパティは全て `String` 型で宣言します（Bean Validationの仕様上の制約）。

**② アクションメソッドの実装**

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

各アノテーションの役割:
- `@Path("/projects")`: URLマッピング（ルーティングアダプタ使用）
- `@POST`: POSTリクエストにマッピング
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付ける
- `@Valid`: フォームに対するBean Validationを実行

**③ DB登録処理の流れ**

1. `BeanUtil.createAndCopy(Project.class, project)` — フォームをエンティティに変換
2. `UniversalDao.insert(entity)` — エンティティをDBに登録（SQLを書かず、Jakarta PersistenceアノテーションからSQL自動生成）
3. `HttpResponse(201)` — 作成完了（ステータスコード `201 Created`）を返却

**④ バリデーショングループを使い分けたい場合（応用）**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
@ConvertGroup(from = Default.class, to = Create.class)
public HttpResponse save(ProjectForm project) {
    UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
    return new HttpResponse();
}
```

- `from = Default.class` は固定
- `to` に適用したいバリデーショングループを指定

**注意点**:
- `@Valid` アノテーションを付けないとバリデーションが実行されないため、必ず付与すること
- `UniversalDao.insert` はエンティティにJakarta Persistenceアノテーション（`@Table`, `@Id` 等）が付いていることが前提
- スキーマを環境ごとに切り替えたい場合は `UniversalDao` の CRUD 機能では対応できないため、JDBCラッパーを使用すること

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json#s1, component/handlers/handlers-jaxrs-bean-validation-handler.json#s4, component/handlers/handlers-jaxrs-bean-validation-handler.json#s5, component/libraries/libraries-universal-dao.json#s2