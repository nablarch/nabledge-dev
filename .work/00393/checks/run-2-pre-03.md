# pre-03 — run-2

## 質問

UniversalDaoでデータベースのデータを検索するにはどうすればいいですか？

## 回答

**結論**: `UniversalDao.findAllBySqlFile()` メソッドを使い、SQLファイルとSQL IDを指定して検索するのが基本です。主キーによる単純な検索も SQL を書かずに実行できます。

**根拠**:

**① 主キーを指定した検索（SQLなし）**

Entityに `@Entity`、`@Id` などの Jakarta Persistence アノテーションを付けるだけで、SQL を書かずに主キー指定の検索が実行できます。

**② SQLファイルを使った検索（基本パターン）**

SQLファイルを作成し、SQL IDを指定して検索します:

```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは検索結果の Bean クラスから自動導出されます（例: `sample.entity.User` → `sample/entity/User.sql`）。

**③ 条件を指定した検索**

検索条件 Bean を第3引数として渡します:

```java
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

`condition` は検索条件を保持する専用の Bean（Entity とは別の DTO）を使います。Bean のプロパティ名に対応した `:propertyName` バインド変数が SQL に自動的にバインドされます。

**④ ページング付き検索**

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

**⑤ 大量データの遅延ロード**

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 処理
    }
}
```

遅延ロード使用時は `DeferredEntityList#close` を必ず呼び出すこと（`try-with-resources` 推奨）。

**設定**

コンポーネント定義ファイルに `BasicDaoContextFactory` の設定が必要です:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- 検索結果をマッピングする Bean のプロパティ名は SELECT 句の列名と一致させる必要があります
- 遅延ロード中にトランザクション制御を行うと、RDBMS によってはカーソルがクローズされエラーになる場合があります
- 主キー以外の条件による更新/削除はユニバーサルDAOでは行えないため、データベースアクセス(JDBCラッパー)を使用します

参照: libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, libraries-universal-dao.json:s6, web-application-getting-started-project-search.json:s1

## 参照ナレッジ

- [任意のSQL(SQLファイル)で検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#任意のsqlsqlファイルで検索する) (s7)
- [条件を指定して検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#条件を指定して検索する) (s10)
- [検索結果を遅延ロードする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果を遅延ロードする) (s9)
- [ページングを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ページングを行う) (s12)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)
- [SQLを書かなくても単純なCRUDができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#sqlを書かなくても単純なcrudができる) (s2)
- [検索結果をBeanにマッピングできる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果をbeanにマッピングできる) (s3)
- [検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-getting-started-project-search.md#検索する) (s1)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers the key fact from the Expected Output: using a SQL file with a specified SQL ID for searching, and mapping results to a Bean. The Actual Output explicitly shows `findAllBySqlFile()` with SQL ID specification, demonstrates Bean class mapping (User.class, Project.class), and explains that SQL file paths are auto-derived from the Bean class. All core elements of the expected fact are present and clearly explained. |
| answer_relevancy | 0.95 | 0.90 | NG | The score is 0.90 because the response mostly addresses how to search data using UniversalDao, but includes some irrelevant information about limitations for update/delete operations and recommendations for alternative tools for those operations, which are unrelated to the question about searching data. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「SQLファイルを作成してSQL IDを指定した検索ができ、検索結果はBeanにマッピングされる」は回答の「SQLファイルを作成し、SQL IDを指定して検索します: UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME")」および「検索結果をマッピングするBeanのプロパティ名はSELECT句の列名と一致させる必要があります」に含まれている |
| answer_relevancy | NG | 回答末尾の「参照: libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, libraries-universal-dao.json:s6, web-application-getting-started-project-search.json:s1」など内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ内容と矛盾なし（findAllBySqlFileの使い方・SQLファイルパス導出・Bean マッピング・遅延ロード・ページング・設定・主キー以外の更新削除制約、いずれもナレッジの記述と一致） |

### 参照事実（expected_facts）

- SQLファイルを作成してSQL IDを指定した検索ができ、検索結果はBeanにマッピングされる
