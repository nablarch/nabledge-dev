**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてFormを受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録する。レスポンスはステータスコード `201 Created` を返す。

**根拠**:

**① Formクラスの作成**（受け取る値を宣言）

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> プロパティは全て `String` 型で宣言する。

**② アクションクラスの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストボディをJSONとして受け付ける。リクエストボディ変換ハンドラが `application/json` 対応のコンバータでFormに変換する
- `@Valid` — リクエストのBean Validationによるバリデーションを実行する
- `BeanUtil.createAndCopy` — FormからEntityに値をコピー
- `UniversalDao.insert` — Entityをそのままテーブルに登録
- `@Path`/`@POST` — URLマッピング（ルーティングアダプタが処理）

**③ ユニバーサルDAOの設定**（コンポーネント定義ファイルへの追加が必要）

```xml
<!-- コンポーネント名は "daoContextFactory" で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `BeanUtil.createAndCopy` の第1引数に渡すEntityクラスは、Jakarta Persistenceアノテーション（`@Entity`、`@Table`、`@Id`、`@Column` 等）が設定されている必要がある
- リクエストボディ変換ハンドラの `bodyConverters` に `application/json` 対応のコンバータが設定されていること（ブランクプロジェクトでは設定済み）

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, libraries-universal-dao.json:s6