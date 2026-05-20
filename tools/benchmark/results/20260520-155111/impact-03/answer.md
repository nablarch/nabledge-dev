**結論**: RESTfulウェブサービスにおいてBean Validationのカスタムバリデータ内でDBに問い合わせて重複チェックを行う実装は**推奨されません**。データベースとの相関バリデーションは業務アクション側で実装してください。

**根拠**: Bean Validation実行中のオブジェクトは安全であることが保証されていないため、その値を使ったDB検索はSQLインジェクション等の脆弱性の原因になります。バリデーション済みの安全な値を使ってDBアクセスできるよう、業務アクション（リソースクラス）でBean Validationが完了した後に重複チェックを行うのが正しい実装です。

```java
// リソースクラスでの実装例
@POST
@Valid  // Bean Validationはここで実施
public HttpResponse create(SampleForm form, ExecutionContext context) {
    // Bean Validationが通過済み = バリデーション済みの安全な値が使える
    // DBへの重複チェックはここで実施
    if (isDuplicate(form.getMailAddress())) {
        // 特定の項目に紐づくエラーメッセージを生成してApplicationExceptionをスロー
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
    }
    // 登録処理...
}
```

エラーメッセージを特定の項目に紐付けてクライアントに返すには、`ValidationUtil#createMessageForProperty` を使って `ApplicationException` をスローします。

**注意点**: Bean Validationと業務アクション側の重複チェックは実行タイミングが異なります。Bean Validationエラーがある場合は重複チェックまで到達しないため、バリデーション通過後に確実にDBチェックを行うことが前提です。

参照: `component/libraries/libraries-bean-validation.json:s12`, `component/libraries/libraries-bean-validation.json:s13`