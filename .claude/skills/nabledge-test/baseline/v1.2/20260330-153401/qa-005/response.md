**結論**: 相関バリデーション（項目間精査）は、`@ValidateFor` アノテーションを付与したバリデーションメソッド内に実装します。単項目精査の実行後、`ValidationContext#getConvertedValue` で変換済みの値を取得し、項目間のチェックロジックを記述して、エラー時は `context.addResultMessage` または `context.addMessage` でエラーメッセージを設定します。

---

**根拠**:

## 基本的な実装パターン

相関バリデーションは `@ValidateFor` アノテーションのバリデーションメソッド内でハードコーディングします。

```java
@ValidateFor("changePassword")
public static void validateForChangePassword(ValidationContext<User> context) {
    ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);
    if (!context.isValid()) { return; }

    String newPassword = (String) context.getConvertedValue("newPassword");
    String confirmPassword = (String) context.getConvertedValue("confirmPassword");
    if (!newPassword.equals(confirmPassword)) {
        context.addResultMessage("newPassword", "MSG10001");
    }
}
```

**注意点**:
1. **単項目精査を先に実行すること**
2. **単項目精査エラー時は早期リターン**: `!context.isValid()` のチェックを入れる
3. **エラーメッセージの登録方法**:
   - `context.addResultMessage(propertyName, messageId)` — 特定プロパティに紐付けてエラーを設定
   - `context.addMessage(messageId)` — プロパティに紐付けないエラー

**Validation**利用例:
```java
ValidationContext result = ValidationUtil.validateAndConvertRequest("user", User.class, req, "changePassword");
```

参照: `component/libraries/libraries-08_02_validation_usage.json#s1`, `guide/web-application/web-application-04_validation.json#s2`
