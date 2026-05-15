**結論**: フォームデータをDBに登録する標準パターンは、「フォーム→Entityへの変換 → セッション保存 → 確認後にUniversalDaoで登録」の3ステップで構成されます。

**根拠**:

**① 入力フォームからEntityへ変換（確認画面遷移時）**

`BeanUtil.createAndCopy()` を使ってフォームオブジェクトをEntityに変換し、セッションストアに保存します。

```java
// リクエストスコープから入力情報を取得
ProjectForm form = context.getRequestScopedVar("form");

// FormからEntityへ変換
Project project = BeanUtil.createAndCopy(Project.class, form);

// 入力情報をセッションストアに保存
SessionUtil.put(ctx, "project", project);
```

**② 登録処理の実行（確認後）**

セッションからEntityを取り出し、`UniversalDao.insert()` でDBに登録します。登録後はセッションを削除します。

```java
// セッションストアから入力情報を取得
Project project = SessionUtil.get(ctx, "project");

// UniversalDaoでDB登録
UniversalDao.insert(project);

// セッションストアから入力情報を削除
SessionUtil.delete(ctx, "project");
```

**③ UniversalDaoのCRUD機能**

EntityにJakarta Persistenceアノテーション（`@Table`、`@Column` 等）を付けるだけで、SQLを書かずに登録・更新・削除・検索が可能です。SQLはアノテーションをもとに実行時に自動構築されます。

**④ 全体フロー（Webアプリ）**

| 処理 | URL | メソッド |
|------|-----|---------|
| 初期表示 | `/action/client/` | GET |
| 登録内容の確認 | `/action/client/confirm` | POST |
| 登録画面に戻る | `/action/client/back` | POST |
| **登録処理の実行** | `/action/client/create` | POST |

**⑤ サロゲートキーの採番（オプション）**

主キーを自動採番する場合は `@GeneratedValue` アノテーションを使用します。

```java
@Id
@Column(name = "PROJECT_ID")
@GeneratedValue(strategy = GenerationType.AUTO)
public Long getId() { return id; }
```

**注意点**:
- 初期表示時に既存のセッションを削除しておく（`SessionUtil.delete(ctx, "project")`）。ブラウザを閉じた場合などにセッションが残留するケースへの対処です。
- `@Table` アノテーションでスキーマ指定はできますが、環境ごとにスキーマを切り替えたい場合はUniversalDaoではなくJDBCラッパーを使用してください。
- `BeanUtil.createAndCopy()` はプロパティ名が一致するフィールドを自動マッピングします。フォームとEntityのプロパティ名が一致していることを確認してください。

参照: `component/libraries/libraries-create-example.json#s2`, `component/libraries/libraries-create-example.json#s4`, `component/libraries/libraries-universal-dao.json#s2`, `component/libraries/libraries-universal-dao.json#s13`, `processing-pattern/web-application/web-application-getting-started-client-create.json#s1`