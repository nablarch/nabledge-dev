**結論**: カスタムバリデータ（Bean Validation）の中でDB検索を行う実装は**不可**です。DB重複チェックは Bean Validation ではなく、業務アクション側（バリデーション実行後）で実装してください。

**根拠**: Nablarch の Bean Validation ドキュメントに明示的な禁止理由が記載されています。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、**バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる**。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)  
> これは、**SQLインジェクションなどの脆弱性の原因となる**ため、避けるべき実装である。

正しい実装フローは以下のとおりです。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid  // ← まずBean Validationで入力値の妥当性チェック（形式・必須など）
public HttpResponse register(UserForm form) {

    // Bean Validationが完了した時点で form の値は安全な状態
    // ここでDB重複チェックを実装する
    int count = UniversalDao.countBySqlFile(User.class, "FIND_BY_EMAIL",
                    new Object[]{ form.getEmail() });
    if (count > 0) {
        // 重複エラーの場合は ApplicationException を送出
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.email", "duplicate.email"));
    }

    UniversalDao.insert(BeanUtil.createAndCopy(User.class, form));
    return new HttpResponse();
}
```

RESTful ウェブサービスでは `@Valid` アノテーションをリソースメソッドに設定すると `JaxRsBeanValidationHandler` が Bean Validation を実行します。そのバリデーション完了後のアクション本体で、安全になった値を使って DB アクセス（重複チェック）を行うのが正しい実装パターンです。

**注意点**:
- Bean Validation 実行中の値は未検証であり、SQLインジェクション対策のエスケープも保証されません
- バリデーション済みの値で DB アクセスすることで、安全性と整合性が保たれます
- エラー発生時は `ValidationUtil.createMessageForProperty` で特定フィールドに紐づくエラーメッセージを生成できます

参照: libraries-bean-validation.json:s12, handlers-jaxrs-bean-validation-handler.json:s4