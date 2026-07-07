# qa-13 — run-1

## 質問

フォームから受け取ったデータをDBに登録する処理の実装パターンを知りたい

## 回答

**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、Formクラスを作成し、業務アクションメソッドに `@Valid` アノテーションを付けて `UniversalDao.insert()` でDB登録する。

**根拠**:

#### 1. Formクラスの作成

クライアントから受け取るデータをFormクラスとして定義する。プロパティは**すべてString型**で宣言すること（型変換はバリデーション後に行う）。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. 業務アクションメソッドの実装

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付ける
- `@Valid` アノテーションを付けると `JaxRsBeanValidationHandler` がFormに対してBean Validationを自動実行する（バリデーションエラー時は `ApplicationException` を送出）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値はステータスコード `201 Created` を表す `HttpResponse` を返す

#### 3. ユニバーサルDAOの設定

コンポーネント定義ファイルに `BasicDaoContextFactory` を設定する必要がある:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）の**後ろ**に設定すること
- Formのプロパティを `String` 以外の型にすると、不正な値が送信された場合にバリデーション前に変換エラーが発生する

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/handlers/handlers-jaxrs-bean-validation-handler.json:s3, component/libraries/libraries-bean-validation.json:s8, component/libraries/libraries-universal-dao.json:s6

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#制約) (s3)
- [バリデーションルールの設定方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションルールの設定方法) (s8)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output comprehensively covers all the key facts present in the Expected Output: (1) using a Form class to receive values, (2) using @Valid annotation for validation, and (3) using UniversalDao.insert() for DB registration. The Actual Output not only contains all expected facts but provides detailed implementation examples, code snippets, and additional context. All three core facts from the Expected Output checklist are clearly present and correctly represented. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about implementation patterns for registering form data into a database. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- REST APIではFormクラスで値を受け付け、@Validでバリデーション後にUniversalDao.insertで登録する
