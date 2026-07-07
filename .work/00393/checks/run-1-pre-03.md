# pre-03 — run-1

## 質問

UniversalDaoでデータベースのデータを検索するにはどうすればいいですか？

## 回答

**結論**: `UniversalDao.findAllBySqlFile()` メソッドにSQLファイルのSQL IDを指定して検索します。条件指定・ページング・大量データの遅延ロードと3つのパターンがあります。

**根拠**:

**1. 基本的な条件指定検索**

SQLファイル（例: `Project.sql`）にSQL IDを定義し、検索条件Beanを渡します。

```sql
-- Project.sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID, PROJECT_NAME, PROJECT_START_DATE
FROM
    PROJECT
WHERE
    $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

```java
// 検索条件Beanを用意（カラム型に合わせた型で定義）
ProjectSearchDto condition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// findAllBySqlFile の第2引数にSQL IDを指定
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

**2. ページング付き検索**

```java
EntityList<Project> projects = UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);

// ページネーション情報の取得
Pagination pagination = projects.getPagination();
```

**3. 大量データの遅延ロード**

```java
// defer() を先に呼び出し、try-with-resources で close する
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

**4. 業務アクションでの実装例（ウェブアプリケーション）**

```java
@InjectForm(form = ProjectSearchForm.class, prefix = "searchForm", name = "searchForm")
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse list(HttpRequest request, ExecutionContext context) {
    ProjectSearchForm searchForm = context.getRequestScopedVar("searchForm");
    ProjectSearchDto searchCondition =
            BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

    EntityList<Project> searchList = UniversalDao
            .page(searchCondition.getPageNumber())
            .per(20L)
            .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);

    context.setRequestScopedVar("searchResult", searchList);
    return new HttpResponse("/WEB-INF/view/project/index.jsp");
}
```

**注意点**:
- 検索条件BeanのプロパティはSQLのカラム型と互換性のある型（`java.sql.Date` 等）で定義すること
- 遅延ロード（`defer()`）使用時は必ず `DeferredEntityList#close` を呼び出すこと（try-with-resources 推奨）
- `batchUpdate` では楽観的ロックは使用できない

参照: libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, web-application-getting-started-project-search.json:s1

## 参照ナレッジ

- [任意のSQL(SQLファイル)で検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#任意のsqlsqlファイルで検索する) (s7)
- [検索結果を遅延ロードする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果を遅延ロードする) (s9)
- [条件を指定して検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#条件を指定して検索する) (s10)
- [ページングを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ページングを行う) (s12)
- [検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-getting-started-project-search.md#検索する) (s1)
- [検索結果をBeanにマッピングできる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果をbeanにマッピングできる) (s3)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)
- [テーブルをJOINした検索結果を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#テーブルをjoinした検索結果を取得する) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Expected Output states one key fact: SQLファイルを作成してSQL IDを指定した検索ができ、検索結果はBeanにマッピングされる (SQL file creation with SQL ID specification for search, with results mapped to Beans). The Actual Output clearly covers this fact - it demonstrates defining SQL IDs in SQL files (e.g., 'SEARCH_PROJECT' in Project.sql), using findAllBySqlFile() with SQL ID specification, and mapping results to Bean classes (Project.class, User.class). The core concept is fully addressed. |
| answer_relevancy | 0.95 | 0.83 | NG | The score is 0.83 because the response generally addresses how to search database data using UniversalDao, including relevant use of findAllBySqlFile. However, it loses points for two issues: an incorrect statement about findAllBySqlFile's argument order (SQL ID is the first argument, not the second), and the inclusion of unrelated information about batchUpdate and optimistic locking, which are irrelevant to the question about database searching. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「SQLファイルを作成してSQL IDを指定した検索ができ、検索結果はBeanにマッピングされる」は回答の「SQLファイル（例: Project.sql）にSQL IDを定義し」「findAllBySqlFile(Project.class, "SEARCH_PROJECT", condition)」「Project.class, User.classへのマッピング」に含まれている |
| answer_relevancy | NG | 回答の注意点に「batchUpdateでは楽観的ロックは使用できない」という記述が含まれているが、これは検索に関する質問と無関係な更新操作に関する内容であり、質問者が知りたい検索方法への回答として的外れである。 |
| faithfulness | OK | findAllBySqlFileの使い方、遅延ロード（defer()とtry-with-resources）、ページング（page()とper()）、DeferredEntityList#closeの必要性など、回答の全ての内容がナレッジMDの記述と一致しており、矛盾は見当たらない。 |

### 参照事実（expected_facts）

- SQLファイルを作成してSQL IDを指定した検索ができ、検索結果はBeanにマッピングされる
