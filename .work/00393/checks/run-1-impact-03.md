# impact-03 — run-1

## 質問

Bean Validationの中でDBに問い合わせて重複チェックしたい。カスタムバリデータでDB検索する実装でいいのか？

## 回答

**結論**: Bean Validation（カスタムバリデータ）内でDBに問い合わせて重複チェックするのは**NG**。DB重複チェックは業務アクション側で、Bean Validationが完了した後に実装すること。

**根拠**:

Bean Validationの仕様では、バリデーション実行中のオブジェクトの値は「安全である保証がない」。この状態でDBアクセスを行うと、SQLインジェクションなどの脆弱性の原因となるため、避けるべき実装とされている。

**正しい実装方針（RESTfulウェブサービスの場合）**:

1. **Formのバリデーション**: `@Valid` アノテーションで通常のBean Validationを実行

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // この時点でBean Validationは完了 → 安全な値のみが渡ってくる
    
    // DB重複チェックはここで行う
    if (UniversalDao.exists(Person.class, condition)) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("person.mailAddress", "duplicate.mailAddress"));
    }
    
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

2. **エラー表示**: アクション側でエラーが発生した場合、`ValidationUtil#createMessageForProperty` を使ってエラーメッセージを構築し、`ApplicationException` を送出することで、特定フィールドのエラーとしてクライアントに返せる。

```java
throw new ApplicationException(
    ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**: Bean Validationのカスタムバリデータ（`ConstraintValidator` 実装クラス）でDBアクセスするコードを書くことは、NablarchのBean Validationの設計方針に反する。必ずバリデーション後の業務アクション内でDB検索を行うこと。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13, handlers-jaxrs-bean-validation-handler.json:s4

## 参照ナレッジ

- [データベースとの相関バリデーションを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#データベースとの相関バリデーションを行う) (s12)
- [特定の項目に紐づくバリデーションエラーのメッセージを作りたい](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#特定の項目に紐づくバリデーションエラーのメッセージを作りたい) (s13)
- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both key facts from the Expected Output: (1) DB重複チェック（相関バリデーション）はBean Validationではなく業務アクション側で実装すべきという点、and (2) Bean Validation実行中のオブジェクトの値は安全である保証がないという根拠。Both expected facts are clearly present, with additional detail and code examples provided. |
| answer_relevancy | 0.95 | 0.93 | NG | The score is 0.93 because the response is largely relevant and addresses the question about implementing duplicate checks via DB queries in Bean Validation using custom validators. However, it loses a few points for including reference document names/IDs which are metadata about sources rather than substantive content that directly contributes to answering the question. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- データベースとの相関バリデーションはBean Validationではなく業務アクション側で実装する。Bean Validation実行中のオブジェクトの値は安全である保証がない
