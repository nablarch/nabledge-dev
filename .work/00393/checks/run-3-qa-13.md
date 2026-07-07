# qa-13 — run-3

## 質問

フォームから受け取ったデータをDBに登録する処理の実装パターンを知りたい

## 回答

**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、Formクラスを作成してJSONリクエストを受け取り、`BeanUtil.createAndCopy()`でEntityに変換した後、`UniversalDao.insert()`でDB登録します。バリデーションは`@Valid`アノテーションで行います。

**根拠**:

**1. Formクラスの作成**

クライアントから送信された値を受け付けるFormを作成します。プロパティは必ず全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. 業務アクションメソッドの実装**

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
- `@Valid` アノテーションを付けることで、`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する（バリデーションエラー時は`ApplicationException`が送出され、登録処理は実行されない）
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換する
- `UniversalDao.insert(entity)` でDB登録する
- 戻り値にステータスコード201（Created）を表す`HttpResponse`を返す
- `@Path("/projects")` + `@POST` でURLとのマッピングを定義する

**3. コンポーネント定義（ユニバーサルDAOの設定）**

`UniversalDao`を使用するには、コンポーネント定義に以下を追加します。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは必ずすべて`String`型で宣言すること。String以外の型を使うと、不正な値が送信された場合にバリデーション前のBean変換処理で予期せぬ例外が発生する
- RESTfulウェブサービスでは `ETag` / `If-Match` を使った楽観的ロックには対応していないため、楽観的ロックが必要な場合はリクエストボディにバージョン番号を含めること

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6, libraries-bean-validation.json:s8

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)
- [バリデーションルールの設定方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションルールの設定方法) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output contains all key facts from the Expected Output: (1) using a Form class to receive values, (2) using @Valid for validation, and (3) using UniversalDao.insert for registration in a REST API context. The Actual Output not only covers all expected facts but provides significantly more detail, including code examples, implementation notes, and additional considerations. Full coverage of the expected facts is achieved. |
| answer_relevancy | 0.95 | 0.94 | NG | The score is 0.94 because the response mostly addresses the implementation pattern for registering form data in a DB, but includes a mention of optimistic locking with ETag and If-Match, which is beyond the scope of the basic implementation pattern being asked about. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「REST APIではFormクラスで値を受け付け、@Validでバリデーション後にUniversalDao.insertで登録する」は回答の「クライアントから送信された値を受け付けるFormを作成します」「@Valid アノテーションを付けることで…バリデーションを実行する」「UniversalDao.insert(entity) でDB登録する」に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6, libraries-bean-validation.json:s8」という内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ（restful-web-service-getting-started-create.md）の記述（Formのプロパティ全String型、@Consumes(APPLICATION_JSON)、@Valid、BeanUtil.createAndCopy、UniversalDao.insert、HttpResponse 201）と矛盾なし |

### 参照事実（expected_facts）

- REST APIではFormクラスで値を受け付け、@Validでバリデーション後にUniversalDao.insertで登録する
