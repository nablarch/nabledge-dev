**結論**: 相関バリデーション（項目間精査）は、`@ValidateFor` アノテーションを付けたstaticメソッド内に、複数プロパティを比較するロジックをハードコーディングして実現する。

**根拠**:

### 1. Formクラスへの実装

相関バリデーションは `@ValidateFor` メソッド内で実装する。単項目精査を先に実行し、エラーがない場合に項目間チェックを行う。

```java
private static final String[] PASSWORD_CHANGE_PROPS
        = new String[] {"id", "prevPassword", "newPassword", "confirmPassword"};

@ValidateFor("changePassword")
public static void validateForChangePassword(ValidationContext<User> context) {
    // まず単項目精査を実行
    ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);
    if (!context.isValid()) {
        return;  // 単項目精査エラーがあれば相関チェックをスキップ
    }
    // 相関チェック: 新パスワードと確認パスワードの一致確認
    String newPassword = (String) context.getConvertedValue("newPassword");
    String confirmPassword = (String) context.getConvertedValue("confirmPassword");
    if (!newPassword.equals(confirmPassword)) {
        context.addResultMessage("newPassword", "MSG10001");
    }
}
```

### 2. エラーメッセージの追加方法

| メソッド | 用途 |
|---|---|
| `context.addResultMessage("propertyName", "msgId")` | 特定項目に紐付くエラー（例: パスワード不一致） |
| `context.addMessage("msgId")` | 全体に跨るエラー（例: 検索条件が1つ以上必要） |

### 3. 全プロパティを精査対象にする場合

`validateWithout` に空配列を渡すことで全プロパティを精査対象にできる:

```java
@ValidateFor("registerUser")
public static void validateForRegister(ValidationContext<W11AC02Form> context) {
    ValidationUtil.validateWithout(context, new String[0]);  // 全プロパティ対象

    if (!context.isValid()) {
        return;
    }
    W11AC02Form form = context.createObject();
    if (!form.getNewPassword().equals(form.getConfirmPassword())) {
        context.addResultMessage("newPassword", "MSG00003");
    }
}
```

### 4. Actionからの呼び出し

バリデーション名（`@ValidateFor` の値）を `validateAndConvertRequest` の第4引数に指定して実行:

```java
ValidationContext<W11AC02Form> context = ValidationUtil.validateAndConvertRequest(
    "W11AC02", W11AC02Form.class, req, "registerUser");
context.abortIfInvalid();
W11AC02Form form = context.createObject();
```

**注意点**:
- `@ValidateFor` メソッド内で `ValidationUtil#validate` または `ValidationUtil#validateWithout` を呼び出さないと、フレームワーク提供バリデータによる精査（単項目精査）が行われない
- 相関チェックは `context.isValid()` で単項目精査のエラー確認後に実施すること（エラーがある状態でプロパティ値を参照すると予期しない動作になる可能性がある）
- 項目間精査の実装はバリデーションメソッド内への**ハードコーディング**が Nablarch 1.3 における実現方法

参照: `component/libraries/libraries-08_02_validation_usage.json#s1`, `guide/web-application/web-application-04_validation.json#s3`
