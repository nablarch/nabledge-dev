**結論**: 相関バリデーション（複数項目を比較するバリデーション）は、`@ValidateFor` アノテーションを付けた `static` バリデーションメソッド内にハードコーディングして実装します。

```java
@ValidateFor("changePassword")
public static void validateForChangePassword(ValidationContext<User> context) {
    ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);
    if (!context.isValid()) return;
    String newPassword = (String) context.getConvertedValue("newPassword");
    String confirmPassword = (String) context.getConvertedValue("confirmPassword");
    if (!newPassword.equals(confirmPassword)) {
        context.addResultMessage("newPassword", "MSG10001");
    }
}
```

参照: `component/libraries/libraries-08_02_validation_usage.json#s1`
