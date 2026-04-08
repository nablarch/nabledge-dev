**結論**: 相関バリデーション（項目間精査）は、Formクラスの `@ValidateFor` アノテーション付きバリデーションメソッド内で、単項目精査の実行後に複数プロパティの値を比較し、不一致時に `ValidationContext#addResultMessage` または `addMessage` でエラーメッセージを追加することで実装します。

---

**根拠**:

### 実装手順

1. Formクラスのセッタにバリデーションアノテーションとプロパティ名アノテーションを付与する
2. `@ValidateFor` アノテーション付きのstaticバリデーションメソッドを実装する
3. メソッド内で `ValidationUtil.validate` または `ValidationUtil.validateWithout` で単項目精査を実行する
4. `context.isValid()` で単項目精査の成功を確認後、プロパティ間の比較チェックを行う
5. 不一致の場合は `context.addResultMessage(プロパティ名, メッセージID)` でエラーを追加する

### コード例（パスワード確認チェック）

```java
private static final String[] PASSWORD_CHANGE_PROPS
        = new String[] {"id", "prevPassword", "newPassword", "confirmPassword"};

@ValidateFor("changePassword")
public static void validateForChangePassword(ValidationContext<User> context) {
    // まず単項目精査を実行
    ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);
    if (!context.isValid()) return;  // 単項目精査失敗時は相関チェックをスキップ

    // 相関バリデーション: 新パスワードと確認用パスワードの一致チェック
    String newPassword = (String) context.getConvertedValue("newPassword");
    String confirmPassword = (String) context.getConvertedValue("confirmPassword");
    if (!newPassword.equals(confirmPassword)) {
        context.addResultMessage("newPassword", "MSG10001");  // プロパティに紐付くエラー
        // 全体に跨るエラーの場合: context.addMessage("MSG10001");
    }
}
```

### バリデーション実行（Actionクラス）

```java
ValidationContext result = ValidationUtil.validateAndConvertRequest(
        "user", User.class, req, "changePassword");
result.abortIfInvalid();  // エラー時はApplicationExceptionをthrow
User user = result.createObject();
```

### Webアプリ実装例（ガイドの具体例）

```java
@ValidateFor("insert")
public static void validate(ValidationContext<W11AC02Form> context) {
    ValidationUtil.validateWithout(context, new String[0]);  // 全プロパティを精査

    if (!context.isValid()) {
        return;
    }

    W11AC02Form form = context.createObject();
    // 新パスワードと確認用パスワードのチェック
    if (!form.matchConfirmPassword()) {
        context.addResultMessage("newPassword", "MSG00003");
    }
    // 携帯電話番号が全項目入力またはひとつも入力されていないことのチェック
    if (!form.isValidateMobilePhoneNumbers()) {
        context.addResultMessage("mobilePhoneNumber", "MSG00004");
    }
}
```

---

**注意点**:
- 相関バリデーションは必ず単項目精査後に実施すること。`context.isValid()` で単項目精査成功を確認してからプロパティ間チェックに進む
- `@ValidateFor` メソッド内で `ValidationUtil#validate` または `ValidationUtil#validateWithout` を呼び出さないと、フレームワーク提供のバリデータによる精査が行われない
- エラーメッセージの追加方法:
  - 特定プロパティに紐付けるエラー: `context.addResultMessage(propertyName, messageId)`
  - 全体に跨るエラー（プロパティ非関連）: `context.addMessage(messageId)`

参照: `component/libraries/libraries-08_02_validation_usage.json#s1`, `guide/web-application/web-application-04_validation.json#s7`, `guide/web-application/web-application-04_validation.json#s3`