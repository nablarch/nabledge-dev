**結論**: 相関バリデーション（項目間精査）は、`@ValidateFor` アノテーション付きの `validateFor` メソッド内に、複数プロパティの比較・チェック処理をハードコーディングすることで実現する。

---

**根拠**:

**基本的な実装手順**:

1. Formクラスに `@ValidateFor` アノテーション付きの static バリデーションメソッドを実装する。
2. メソッド内で `ValidationUtil.validate` または `ValidationUtil.validateWithout` を呼び出し、単項目精査を先に実行する。
3. `context.isValid()` でエラーなしを確認してから、複数プロパティ間のチェック処理を実装する。
4. エラー発生時は `context.addResultMessage` または `context.addMessage` でエラーメッセージを追加する。

**実装例（パスワードと確認用パスワードの一致チェック）**:

```java
private static final String[] PASSWORD_CHANGE_PROPS
        = new String[] {"id", "prevPassword", "newPassword", "confirmPassword"};

@ValidateFor("changePassword")
public static void validateForChangePassword(ValidationContext<User> context) {
    ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);
    if (!context.isValid()) { return; }  // 単項目精査エラーがあれば終了
    String newPassword = (String) context.getConvertedValue("newPassword");
    String confirmPassword = (String) context.getConvertedValue("confirmPassword");
    if (!newPassword.equals(confirmPassword)) {
        context.addResultMessage("newPassword", "MSG10001");
    }
}
```

**Webアプリケーションでの実装例（W11AC02Form）**:

```java
@ValidateFor("registerUser")
public static void validateForRegister(ValidationContext<W11AC02Form> context) {
    ValidationUtil.validateWithout(context, new String[0]);

    // 単項目精査でエラーの場合はここで戻る
    if (!context.isValid()) {
        return;
    }

    W11AC02Form form = context.createObject();
    // 新パスワードと確認用パスワードのチェック
    if (!form.newPassword.equals(form.confirmPassword)) {
        context.addResultMessage("newPassword", "MSG00003");
    }
}
```

**エラーメッセージの追加メソッド**:

| メソッド | 用途 |
|---|---|
| `context.addResultMessage(String propertyName, String messageId)` | 特定プロパティに紐付けてエラーメッセージを追加（例: 新パスワードフィールドにエラー表示） |
| `context.addMessage(String messageId)` | プロパティに紐付けないエラーメッセージを追加（例: 検索条件が1つも指定されなかった場合） |

**複数フィールドをハイライトしたい場合（nameAlias の使用）**:

携帯電話番号など複数の入力項目が関連するエラーで、全フィールドをハイライト表示するには JSP の `nameAlias` 属性を使用する。

```jsp
<n:text name="users.mobilePhoneNumberAreaCode" nameAlias="users.mobilePhoneNumber" ... />
<n:text name="users.mobilePhoneNumberCityCode" nameAlias="users.mobilePhoneNumber" ... />
<n:text name="users.mobilePhoneNumberSbscrCode" nameAlias="users.mobilePhoneNumber" ... />
```

```java
// エイリアス名でエラーメッセージを登録すると3つ全ての項目がハイライト表示される
context.addResultMessage("mobilePhoneNumber", "MSG00004");
```

---

**注意点**:
- 相関バリデーションのチェック処理は、必ず単項目精査（`ValidationUtil.validate` / `validateWithout`）を呼び出した後、`context.isValid()` でエラーなしを確認してから実施すること。独自精査処理内で `ValidationUtil#validate` または `ValidationUtil#validateWithout` を呼び出さないと、フレームワークが提供するバリデータによる精査が行われない。
- `context.getConvertedValue(String propertyName)` を使用して変換済みの値を取得してから比較すること。

参照: `component/libraries/libraries-08_02_validation_usage.json#s1`, `guide/web-application/web-application-04_validation.json#s2`, `component/libraries/libraries-07_DisplayTag.json#s4`