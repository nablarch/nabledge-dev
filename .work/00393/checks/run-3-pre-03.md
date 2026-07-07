# pre-03 — run-3

## 質問

UniversalDaoでデータベースのデータを検索するにはどうすればいいですか？

## 回答

**結論**: UniversalDaoでデータベースを検索するには、主キー検索なら `UniversalDao.findById()` を、任意のSQL検索なら `UniversalDao.findAllBySqlFile()` を使用します。

**根拠**:

**① 主キーを指定した検索（SQLファイル不要）**

EntityクラスにJakarta Persistenceアノテーション（`@Entity`、`@Id` など）を付けるだけで、SQLを書かずに主キー検索できます。

```java
// 主キーを指定して1件取得
User user = UniversalDao.findById(User.class, userId);
```

**② 任意のSQL（SQLファイル）で検索する**

SQLファイルを作成し、SQL IDを指定して検索します。

```java
// 全件検索（条件なし）
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルはBeanのクラス名から自動導出されます（例：`sample.entity.User` → `sample/entity/User.sql`）。

**③ 条件を指定して検索する**

条件BeanをSQLファイル検索の第3引数に渡します。

```java
// 検索条件Beanを指定
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件はEntityではなく専用のBeanを使うことが推奨です（1テーブルのみの場合はEntityも可）。

**④ ページングを行う場合**

`per()` と `page()` を先に呼び出します。

```java
EntityList<Project> projects = UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

ページング情報（件数等）は `EntityList#getPagination()` で取得できます。

**⑤ 大量データを扱う場合（遅延ロード）**

`defer()` を使ってサーバサイドカーソルで1件ずつ処理できます。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

**注意点**:
- 遅延ロード中にトランザクション制御が行われると、RDBMSによってはカーソルがクローズされエラーになる場合があります。try-with-resources で `DeferredEntityList#close()` を必ず呼び出してください。
- UniversalDAOは簡易O/Rマッパーであり、主キー以外の条件での更新・削除は対応していません（その場合はデータベースアクセス（JDBCラッパー）を使用）。

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9

## 参照ナレッジ

- [SQLを書かなくても単純なCRUDができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#sqlを書かなくても単純なcrudができる) (s2)
- [検索結果をBeanにマッピングできる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果をbeanにマッピングできる) (s3)
- [任意のSQL(SQLファイル)で検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#任意のsqlsqlファイルで検索する) (s7)
- [条件を指定して検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#条件を指定して検索する) (s10)
- [ページングを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ページングを行う) (s12)
- [検索結果を遅延ロードする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果を遅延ロードする) (s9)
- [検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-getting-started-project-search.md#検索する) (s1)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 0.70 | NG | The expected output states that SQL files can be created with SQL IDs specified for searching, and that search results are mapped to Beans. The actual output explicitly covers creating SQL files and specifying SQL IDs (e.g., 'FIND_BY_NAME', 'SEARCH_PROJECT') in section ②. However, the fact that 'search results are mapped to Beans' is only implicitly covered through code examples showing results assigned to typed objects (e.g., List<Project>, EntityList<Project>), but it is not explicitly stated that results are mapped to Beans. The core fact about SQL file creation and SQL ID specification is clearly covered. |
| answer_relevancy | 0.95 | 0.87 | NG | The score is 0.87 because the response mostly addresses how to search a database using UniversalDao, but it loses some points for including irrelevant information about the limitations of UniversalDAO regarding updates and deletions, as well as details about updates and deletions using JDBC wrapper. These statements do not contribute to answering the question about database searching. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | NG | 参照事実「検索結果はBeanにマッピングされる」が回答に明示的に含まれていない。回答②〜⑤はSQLファイル・SQL ID指定の検索を説明しており、コード例で `List<Project>` や `EntityList<Project>` 等の型付き変数に結果を代入しているが、「検索結果をBean（Entity、Form、DTO）にマッピングして取得できる」という事実を文章として明示していない。ナレッジ s3 には「ユニバーサルDAOでは、検索結果をBean（Entity、Form、DTO）にマッピングして取得できる」と明記されているが、その内容が回答本文から欠落している。 |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- SQLファイルを作成してSQL IDを指定した検索ができ、検索結果はBeanにマッピングされる
