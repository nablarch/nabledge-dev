セクション内容が揃いました。回答を生成します。

---

**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付けたアクションメソッドでFormを受け取り、`BeanUtil.createAndCopy`でEntityに変換後、`UniversalDao.insert`でDBに登録する。

**根拠**:

**1. Formクラスの作成**

プロパティはすべて`String`型で宣言すること（型変換エラーを防ぐため）。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
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
- `@Path` + `@POST`: URLとアクションメソッドのマッピングを定義
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディをJSON形式で受け付ける
- `@Valid`: リクエストのバリデーション（Bean Validationハンドラが実行）を有効化
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換
- `UniversalDao.insert(...)`: DBへの登録
- 戻り値: ステータスコード `201`（リソース作成完了）を返す

**3. ユニバーサルDAOの設定**

コンポーネント定義に`BasicDaoContextFactory`を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- FormのプロパティはすべてString型にすること。String以外の型の場合、バリデーション前のBean変換で例外が発生する可能性がある
- Formから取得した値を直接Entityとして使うのではなく、`BeanUtil.createAndCopy`で変換してから`UniversalDao.insert`に渡すこと

参照: `restful-web-service-getting-started-create.json:s1`, `handlers-body-convert-handler.json:s5`, `libraries-bean-validation.json:s8`, `libraries-universal-dao.json:s6`

---