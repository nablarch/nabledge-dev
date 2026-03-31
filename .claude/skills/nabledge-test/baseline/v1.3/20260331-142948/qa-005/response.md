**結論**: 相関バリデーション（項目間精査）は、`@ValidateFor` アノテーションを付けたバリデーションメソッド内に実装します。まず `ValidationUtil.validate` または `ValidationUtil.validateWithout` で単項目精査を実行し、`context.isValid()` でエラーがないことを確認してから、複数プロパティを取得して比較・チェックロジックを記述します。

**根拠**:

```java
@ValidateFor("changePassword")
public static void validateForChangePassword(ValidationContext<User> context) {
    ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);
    if (!context.isValid()) {
        return;
    }
    String newPassword = (String) context.getConvertedValue("newPassword");
    String confirmPassword = (String) context.getConvertedValue("confirmPassword");
    if (!newPassword.equals(confirmPassword)) {
        context.addResultMessage("newPassword", "MSG10001");
    }
}
```

| メソッド | 用途 |
|---|---|
| `context.addResultMessage("propertyName", "msgId")` | 特定プロパティに紐付くエラー |
| `context.addMessage("msgId")` | 全体に跨るエラー |

参照: `guide/web-application/web-application-04_validation.json#s3`, `component/libraries/libraries-08_02_validation_usage.json#s1`
