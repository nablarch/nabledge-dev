**結論**: 相関バリデーション（複数プロパティ間のチェック）は、Formクラスの `@ValidateFor` アノテーション付き static メソッド内で実装します。単項目精査を実行後、`context.isValid()` で成功を確認してからプロパティ間の比較を行い、エラー時は `context.addResultMessage()` または `context.addMessage()` でエラーメッセージを追加します。

---

**根拠**:

#### 実装手順

1. Formクラスに `@ValidateFor` アノテーション付きの static バリデーションメソッドを追加する
2. メソッド内で `ValidationUtil.validate()` を呼び出して単項目精査を実行する
3. `context.isValid()` で単項目精査が全て成功していることを確認する
4. プロパティ間の比較ロジックを実装し、エラーがあれば `context.addResultMessage()` を呼び出す

#### コード例（パスワード確認チェック）

```java
private static final String[] PASSWORD_CHANGE_PROPS
        = new String[] {"id", "prevPassword", "newPassword", "confirmPassword"};

@ValidateFor("changePassword")
public static void validateForChangePassword(ValidationContext<User> context) {
    // まず単項目精査を実行
    ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);

    // 単項目精査が失敗していれば、相関バリデーションはスキップ
    if (!context.isValid()) return;

    // プロパティ間の比較（相関バリデーション）
    String newPassword = (String) context.getConvertedValue("newPassword");
    String confirmPassword = (String) context.getConvertedValue("confirmPassword");
    if (!newPassword.equals(confirmPassword)) {
        // 特定プロパティに紐付くエラーメッセージを追加
        context.addResultMessage("newPassword", "MSG10001");
        // プロパティに関連付けない場合: context.addMessage("MSG10001");
    }
}
```

#### バリデーション実行

```java
ValidationContext result = ValidationUtil.validateAndConvertRequest(
    "user", User.class, req, "changePassword");
result.abortIfInvalid();
```

#### Webアプリケーションでの実装例（新旧パスワード不一致、携帯電話番号チェック）

```java
@ValidateFor("insert")
public static void validate(ValidationContext<W11AC02Form> context) {
    ValidationUtil.validateWithout(context, new String[0]);

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

#### エラーメッセージ追加メソッドの使い分け

| メソッド | 用途 |
|---|---|
| `context.addResultMessage(propertyName, messageId)` | 特定の項目に対するエラー（例: 新パスワードと確認用パスワードが不一致） |
| `context.addMessage(messageId)` | 全体に跨るエラー（例: 検索条件が1つも指定されなかった） |

---

**注意点**:
- 相関バリデーションは必ず単項目精査の後に実行すること。`context.isValid()` で単項目精査の成功を確認してから実施しないと、変換前の不正な値を比較することになる
- `ValidationUtil.validate()` または `ValidationUtil.validateWithout()` をバリデーションメソッド内で呼び出さないと、フレームワーク提供のバリデータによる単項目精査は実行されない（警告）
- `context.getConvertedValue()` を使用すると、アノテーション変換後の値を取得できる

参照: `component/libraries/libraries-08_02_validation_usage.json#s1`, `guide/web-application/web-application-04_validation.json#s7`, `guide/web-application/web-application-04_validation.json#s3`
