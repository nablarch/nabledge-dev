**結論**: Bean Validationのカスタムバリデータ内でDBアクセスを行うのは非推奨です。DB重複チェックはBean Validation通過後に**業務アクション（リソースクラスのメソッド）側**で実装してください。

**根拠**: NablarchのBean Validationドキュメントに明記されています。

> 「Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。バリデーション実行後に業務アクションでバリデーションを行うことで、バリデーション済みの安全な値を使用してデータベースへアクセスできる。」

推奨される実装パターン：

```java
// リソースクラスのメソッド内
public HttpResponse register(@Valid UserRegisterForm form, ...) {
    // ここに到達した時点でBean Validationは通過済み（安全な値）
    
    // DB重複チェックをアクション内で実施
    if (isDuplicate(form.getEmail())) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.email", "duplicate.email"));
    }
    
    // 登録処理
    // ...
}
```

`ValidationUtil#createMessageForProperty` を使うことで、特定のフィールド（この例では `form.email`）にエラーメッセージを紐づけてクライアントへ返すことができます。

**注意点**:
- RESTfulウェブサービスでのBean Validationは、リソースクラスのメソッド引数に `@Valid` アノテーションを付与することで実行されます。DB重複チェックはその後（メソッド本体）で行います。
- カスタムバリデータ内でのDBアクセスは「安全ではない値でSQLが実行される」リスクがあるため、Nablarchとして明示的に禁止しています。

参照: `component/libraries/libraries-bean-validation.json:s12`, `component/libraries/libraries-bean-validation.json:s13`, `component/libraries/libraries-bean-validation.json:s17`