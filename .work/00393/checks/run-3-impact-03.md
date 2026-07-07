# impact-03 — run-3

## 質問

Bean Validationの中でDBに問い合わせて重複チェックしたい。カスタムバリデータでDB検索する実装でいいのか？

## 回答

**結論**: カスタムバリデータの中でDB検索を行う実装はNablarchでは**禁止されています**。DB重複チェックは、Bean Validation完了後に**業務アクション側**で実装してください。

**根拠**:

Bean Validationの中でDBアクセスを行ってはいけない理由は、Bean Validation実行中はオブジェクトの値が安全である保証がないためです。バリデーション前の安全でない値でDBアクセスを行うと、SQLインジェクションなどの脆弱性の原因となります。

正しい実装の流れ（RESTfulウェブサービスの場合）:

**Step 1: リソースクラスで `@Valid` を設定してBean Validationを実行する**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // ここに来た時点でBean Validationは完了済み（安全な値）
    // Step 2: 業務アクション内でDB重複チェックを実施する
    checkDuplicate(person);
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**Step 2: 業務アクション内でDB重複チェックを実施する**

バリデーション済みの安全な値を使ってDBアクセスできます。重複エラーを特定フィールドのエラーとして返したい場合は `ValidationUtil#createMessageForProperty` を使います。

```java
private void checkDuplicate(Person person) {
    // バリデーション済みの安全な値でDB検索
    if (UniversalDao.exists(...)) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("person.email", "duplicate.email"));
    }
}
```

**注意点**:
- `@Valid` を設定したリソースメソッドでは `JaxRsBeanValidationHandler` が自動的にBean Validationを実行します。バリデーションエラー時は `ApplicationException` が送出され、後続処理は実行されません。
- DB重複チェックは必ずBean Validation完了後（アクションメソッドの中）で行うこと。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13, handlers-jaxrs-bean-validation-handler.json:s4

## 参照ナレッジ

- [データベースとの相関バリデーションを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#データベースとの相関バリデーションを行う) (s12)
- [特定の項目に紐づくバリデーションエラーのメッセージを作りたい](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#特定の項目に紐づくバリデーションエラーのメッセージを作りたい) (s13)
- [RESTfulウェブサービスのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#restfulウェブサービスのユーザ入力値のチェックを行う) (s17)
- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both key facts from the Expected Output: (1) DB/correlation validation should be implemented in the business action side rather than Bean Validation, and (2) object values during Bean Validation execution are not guaranteed to be safe. Both facts are explicitly stated in the Actual Output, with additional context and code examples provided. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant to the question about implementing duplicate checks using database queries within Bean Validation via a custom validator. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「データベースとの相関バリデーションはBean Validationではなく業務アクション側で実装する」は回答の「DB重複チェックは、Bean Validation完了後に業務アクション側で実装してください」に含まれている。参照事実「Bean Validation実行中のオブジェクトの値は安全である保証がない」は回答の「Bean Validation実行中はオブジェクトの値が安全である保証がないためです」に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- データベースとの相関バリデーションはBean Validationではなく業務アクション側で実装する。Bean Validation実行中のオブジェクトの値は安全である保証がない
