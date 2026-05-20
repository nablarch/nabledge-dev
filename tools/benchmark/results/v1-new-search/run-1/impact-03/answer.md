**結論**: RESTfulウェブサービスでも、Bean Validationのカスタムバリデータ内でのDB検索実装は **NG**。データベースとの重複チェックは業務アクション側で、バリデーション完了後に実装すること。

**根拠**:

Bean Validation実行中はオブジェクトの値が「安全である保証がない」状態です。その状態でDB検索を行うとSQLインジェクション等の脆弱性につながるため、Nablarchでは明示的に禁止しています。

推奨実装は、リソースクラス（業務アクション）でBean Validationが完了した後にDB問い合わせを行う方法です。

重複エラーを特定フィールドに紐付けてクライアントへ返却したい場合は、`ValidationUtil#createMessageForProperty` で項目指定のエラーメッセージを構築し `ApplicationException` を送出します。

```java
// アクションメソッド内（Bean Validation完了後）でDB重複チェックを実施
@Valid  // ← Bean Validationはここで実行される
public HttpResponse create(UserForm form, ExecutionContext context) {
    // バリデーション済みの安全な値でDBを検索
    if (isDuplicate(form.getMailAddress())) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
    }
    // 正常処理 ...
}
```

**注意点**: `ValidationUtil#createMessageForProperty` の第1引数はフィールドパス（例: `"form.mailAddress"`）、第2引数はエラーメッセージID（プロパティファイルで定義）です。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13