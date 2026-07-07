# qa-13 — run-2

## 質問

フォームから受け取ったデータをDBに登録する処理の実装パターンを知りたい

## 回答

**結論**

フォームデータをDBに登録するには、Formクラスを作成してアクションメソッドで受け取り、`BeanUtil.createAndCopy` でエンティティに変換した上で `UniversalDao.insert` でDB登録する。レスポンスとして `HttpResponse.Status.CREATED`（ステータスコード 201）を返す。

**根拠**

**Formクラスの実装**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**アクションクラスの実装**

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

各アノテーション・APIの役割:
- `@Path("/projects")` + `@POST` — URLとHTTPメソッドのマッピングを定義
- `@Consumes(MediaType.APPLICATION_JSON)` — JSONリクエストボディをFormに変換するよう指示
- `@Valid` — リクエストボディ変換後にBean Validationを実行
- `BeanUtil.createAndCopy(Project.class, project)` — FormをエンティティBeanに変換
- `UniversalDao.insert(entity)` — エンティティをDBに登録

**注意点**

- Formクラスのプロパティは**必ずString型**で宣言する。String以外の型があると、不正な値が送信された際にBeanへの変換処理が失敗して予期せぬ例外が発生する（バリデーション前に障害となる）。
- `@Valid` が機能するには `JaxRsBeanValidationHandler` が `BodyConvertHandler` より後ろにハンドラキューに設定されている必要がある。Jersey/RESTEasyアダプタ（`JerseyJaxRsHandlerListFactory` 等）を使用している場合は自動的に正しい順序で設定される。

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-bean-validation-handler.json:s3, libraries-bean-validation.json:s8, adapters-jaxrs-adaptor.json:s2

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [createAndCopy](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md#createandcopy) (s46)
- [バリデーションルールの設定方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#バリデーションルールの設定方法) (s8)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#制約) (s3)
- [Jersey環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#jersey環境下でrestfulウェブサービスを使用する) (s2)
- [マッピングの実装方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#マッピングの実装方法) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers all facts in the Expected Output: it explains using a Form class to receive values, using @Valid for validation, and using UniversalDao.insert for registration. Additionally, the Actual Output provides extensive detail including code examples, annotations, and implementation notes, but the core expected facts are all present. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing the implementation patterns for registering form data into a database. No irrelevant statements were identified! |
| faithfulness | 0.99 | 0.93 | NG | The score is 0.93 because the actual output incorrectly associates JerseyJaxRsHandlerListFactory with RESTEasy adapters, when the retrieval context clearly indicates that JerseyJaxRsHandlerListFactory is specific to the Jersey adapter. No RESTEasy adapter is mentioned in the retrieval context. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「REST APIではFormクラスで値を受け付け、@Validでバリデーション後にUniversalDao.insertで登録する」は、回答の「ProjectFormクラスの実装」「@Validアノテーションの説明」「UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project))」にすべて含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- REST APIではFormクラスで値を受け付け、@Validでバリデーション後にUniversalDao.insertで登録する
