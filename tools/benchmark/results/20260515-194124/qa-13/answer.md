**結論**: フォームから受け取ったデータをDBに登録するには、`@InjectForm` でバリデーション済みフォームを取得し、`BeanUtil.createAndCopy` でEntityに変換して `UniversalDao.insert()` で登録するパターンが標準です。確認画面を挟む場合は `SessionUtil` でEntityを一時保存します。

**根拠**:

#### 処理フローの全体像

顧客登録機能を例にすると、以下の4ステップで構成されます。

| NO. | 処理名 | URL | Actionメソッド | HTTPメソッド |
|---|---|---|---|---|
| 1 | 初期表示 | /action/client/ | ClientAction#input | GET |
| 2 | 登録内容の確認 | /action/client/confirm | ClientAction#confirm | POST |
| 3 | 登録画面に戻る | /action/client/back | ClientAction#back | POST |
| 4 | 登録処理の実行 | /action/client/create | ClientAction#create | POST |

#### Step 1: フォームのバリデーションと取得（確認画面へ遷移）

`@InjectForm` アノテーションでリクエストパラメータのバリデーションとフォームオブジェクトの生成を行います。

```java
@InjectForm(form = ProjectForm.class, prefix = "form", validate = "register")
@OnError(type = ApplicationException.class, path = "forward://input.jsp")
public HttpResponse confirm(HttpRequest req, ExecutionContext ctx) {

    // バリデーション済みフォームをリクエストスコープから取得
    ProjectForm form = ctx.getRequestScopedVar("form");

    // FormからEntityへ変換
    Project project = BeanUtil.createAndCopy(Project.class, form);

    // 確認画面表示のためセッションストアに保存
    SessionUtil.put(ctx, "project", project);

    return new HttpResponse("/WEB-INF/view/project/confirm.jsp");
}
```

#### Step 2: DB登録処理の実行

確認画面でユーザーが確定した後、セッションからEntityを取り出して `UniversalDao.insert()` で登録します。

```java
public HttpResponse create(HttpRequest req, ExecutionContext ctx) {

    // セッションストアから入力情報を取得
    Project project = SessionUtil.get(ctx, "project");

    // DB登録
    UniversalDao.insert(project);

    // セッションから入力情報を削除
    SessionUtil.delete(ctx, "project");

    return new HttpResponse(303, "redirect:///action/project/complete");
}
```

#### UniversalDao による登録

Entityに Jakarta Persistence アノテーションを付与するだけでSQLを書かずにCRUD操作が可能です。

```java
@Entity
@Table(name = "PROJECT")
public class Project {
    @Id
    @Column(name = "PROJECT_ID")
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "seq")
    @SequenceGenerator(name = "seq", sequenceName = "PROJECT_ID_SEQ")
    public Long getProjectId() { return projectId; }
    // ... 他フィールド
}
```

**注意点**:

- `@InjectForm` の `prefix` はHTMLの `input name` の前置詞と一致させること（例: `name="form.userId"` → `prefix = "form"`）
- バリデーションエラー時は `@OnError` で指定した画面に自動でフォワードされる
- セッションストアに保存したEntityは登録完了後に必ず `SessionUtil.delete()` で削除すること（セッション肥大化防止）
- サロゲートキーの採番は `@GeneratedValue` の `strategy` で `AUTO` / `IDENTITY` / `SEQUENCE` / `TABLE` から選択可能。DBの種類に応じて適切に選ぶこと
- `UniversalDao` のスキーマ切り替え機能（環境ごとのスキーマ変更）はサポートされていないため、環境依存のスキーマ切り替えが必要な場合はJDBCラッパーを使用すること

参照:
- `processing-pattern/web-application/web-application-getting-started-client-create.json#s1`
- `component/libraries/libraries-create-example.json#s2`
- `component/libraries/libraries-create-example.json#s4`
- `component/handlers/handlers-InjectForm.json#s3`
- `component/libraries/libraries-universal-dao.json#s2`
- `component/libraries/libraries-universal-dao.json#s13`