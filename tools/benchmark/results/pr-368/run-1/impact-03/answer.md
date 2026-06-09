**結論**: Bean ValidationのカスタムバリデータでDB検索する実装は**Nablarchでは明示的に禁止されています**。DBとの相関バリデーション（重複チェック等）は、Bean Validationが完了した後に**業務アクション側で実装**してください。

**根拠**:

Bean Validationの実行中は、オブジェクトの値がバリデーション済みである保証がありません。その安全でない値を使ってDB検索を行うと、SQLインジェクションなどの脆弱性の原因となります。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装である。

**推奨実装パターン**:

1. Bean Validationで通常の単項目チェック（必須、文字種、桁数など）を実施
2. Bean Validationが通過した後、業務アクションのメソッド内で重複チェックのDBアクセスを実施
3. 重複が見つかった場合は `ValidationUtil.createMessageForProperty` でエラーメッセージを構築し、`ApplicationException` をスローする

```java
// RESTful ウェブサービスのアクション内での重複チェック実装例
public HttpResponse create(@Valid UserForm form, ExecutionContext context) {
    // ここに来た時点で form の値はバリデーション済みで安全

    // DBで重複チェック
    if (isEmailDuplicate(form.getEmail())) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.email", "duplicate.email"));
    }

    // 正常処理
    // ...
}
```

**注意点**: アクション側でエラーを投げると、RESTfulウェブサービスでは `JaxRsBeanValidationHandler` ではなく `JaxRsResponseHandler` がエラーハンドリングします。エラーレスポンスの形式がBean Validationエラーと異なる場合があるため、レスポンス形式の統一が必要な場合は `ErrorResponseBuilder` を拡張してください。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13