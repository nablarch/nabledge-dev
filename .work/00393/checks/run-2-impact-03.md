# impact-03 — run-2

## 質問

Bean Validationの中でDBに問い合わせて重複チェックしたい。カスタムバリデータでDB検索する実装でいいのか？

## 回答

**結論**: Bean Validation（カスタムバリデータ含む）の中でDBに問い合わせる重複チェックの実装は推奨されません。DB検索による重複チェックは**業務アクション側**で実装してください。

**根拠**: Nablarchの公式設計方針として、Bean Validationでデータベースとの相関バリデーションを行うことが明示的に禁止されています。

> データベースとの相関バリデーションは、以下理由により業務アクション側で実装すること。
> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)
> これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。

推奨する実装パターンは、RESTfulウェブサービスの場合:

1. `@Valid` アノテーションによるBean Validationで入力値の形式チェックを実施
2. バリデーション通過後、業務アクションメソッド内でUniversalDaoなどを使ってDB検索し、重複チェックを実行
3. 重複が見つかった場合は、特定の項目にエラーを紐付けたい場合は `ValidationUtil#createMessageForProperty` を使用して `ApplicationException` を送出

```java
// アクションメソッド内での重複チェック実装例
public HttpResponse create(JaxRsHttpRequest request, ExecutionContext context) {
    SampleForm form = ...; // @Valid でバリデーション済み

    // バリデーション済みの安全な値を使ってDB検索
    if (isDuplicate(form.getMailAddress())) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
    }
    // 業務処理...
}
```

**注意点**: Bean Validationのカスタムバリデータ（`ConstraintValidator`実装）内でもDBアクセスは同じ理由で避けるべきです。バリデーション実行中はオブジェクトの値の安全性が保証されておらず、セキュリティ上のリスクがあります。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13

## 参照ナレッジ

- [データベースとの相関バリデーションを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#データベースとの相関バリデーションを行う) (s12)
- [特定の項目に紐づくバリデーションエラーのメッセージを作りたい](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#特定の項目に紐づくバリデーションエラーのメッセージを作りたい) (s13)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers all key facts from the Expected Output: (1) database correlation validation should be implemented in the business action side, not Bean Validation — explicitly stated; (2) the reason that object values during Bean Validation execution are not guaranteed to be safe — directly quoted from official documentation. The Actual Output not only covers these facts but provides additional context, code examples, and references without contradicting any expected facts. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant to the question about implementing duplicate checks with DB queries in Bean Validation using custom validators. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「データベースとの相関バリデーションはBean Validationではなく業務アクション側で実装する」は回答の「DB検索による重複チェックは**業務アクション側**で実装してください」に含まれている。参照事実「Bean Validation実行中のオブジェクトの値は安全である保証がない」は回答の引用部分「Bean Validation実行中のオブジェクトの値は、安全である保証がない。」に含まれている |
| answer_relevancy | OK | 回答はBean Validationのカスタムバリデータ内でのDB重複チェックについての質問に直接答えており、推奨しない理由・推奨する実装パターン・コード例をすべて質問に関連した内容で構成している。的外れな情報は含まれていない。 |
| faithfulness | OK | 回答が引用するナレッジの内容「データベースとの相関バリデーションは業務アクション側で実装すること」「Bean Validation実行中のオブジェクトの値は安全である保証がない」「SQLインジェクションなどの脆弱性の原因となる」はすべてlibaries-bean-validation.md(s12)の記述と一致している。また`ValidationUtil#createMessageForProperty`と`ApplicationException`の使用例もs13の記述と一致しており、矛盾はない。 |

### 参照事実（expected_facts）

- データベースとの相関バリデーションはBean Validationではなく業務アクション側で実装する。Bean Validation実行中のオブジェクトの値は安全である保証がない
