**結論**: 相関バリデーション（複数プロパティ間の整合性チェック）は、`@ValidateFor` アノテーションを付与したバリデーションメソッド内で、単項目精査実行後に手動で項目間のチェック処理をハードコーディングすることで実現します。

**根拠**:

#### 基本的な実装手順

1. **単項目精査を実施する**  
   `ValidationUtil.validate(context, props)` または `ValidationUtil.validateWithout(context, skipProps)` で単項目精査を実行します。

2. **単項目精査エラーがないことを確認する**  
   `context.isValid()` が `false` の場合は早期リターンします（単項目エラーがあれば相関チェックは不要）。

3. **項目間の値を取得して比較する**  
   `context.getConvertedValue("プロパティ名")` で変換済みの値を取得します。

4. **エラーメッセージを登録する**  
   - 特定プロパティに紐付ける場合: `context.addResultMessage("propertyName", "MSG10001")`  
   - どのプロパティにも紐付けない場合: `context.addMessage("MSG10001")`

#### 実装例: 新パスワードと確認用パスワードの一致チェック

```java
private static final String[] PASSWORD_CHANGE_PROPS
        = new String[] {"id", "prevPassword", "newPassword", "confirmPassword"};

@ValidateFor("changePassword")
public static void validateForChangePassword(ValidationContext<User> context) {
    // Step 1: 単項目精査を実施
    ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);

    // Step 2: 単項目エラーがあれば早期リターン
    if (!context.isValid()) { return; }

    // Step 3: 変換済みの値を取得して比較
    String newPassword = (String) context.getConvertedValue("newPassword");
    String confirmPassword = (String) context.getConvertedValue("confirmPassword");

    // Step 4: 不一致の場合エラーメッセージを登録
    if (!newPassword.equals(confirmPassword)) {
        context.addResultMessage("newPassword", "MSG10001");
    }
}
```

バリデーションの実行（Actionクラス側）:
```java
ValidationContext result = ValidationUtil.validateAndConvertRequest(
    "user", User.class, req, "changePassword");
```

#### 実装例: 複数フィールドの入力有無チェック（携帯電話番号）

3フィールドがすべて入力済み、またはすべて未入力かをチェックする例:

```java
@ValidateFor("registerUser")
public static void validateForRegisterUser(ValidationContext<UsersEntity> context) {
    ValidationUtil.validateWithout(context, REGISTER_USER_SKIP_PROPS);
    if (!context.isValid()) { return; }

    String areaCode   = (String) context.getConvertedValue("mobilePhoneNumberAreaCode");
    String cityCode   = (String) context.getConvertedValue("mobilePhoneNumberCityCode");
    String sbscrCode  = (String) context.getConvertedValue("mobilePhoneNumberSbscrCode");

    boolean allFilled = areaCode.length() != 0 && cityCode.length() != 0 && sbscrCode.length() != 0;
    boolean allEmpty  = areaCode.length() == 0 && cityCode.length() == 0 && sbscrCode.length() == 0;

    if (!(allFilled || allEmpty)) {
        context.addResultMessage("mobilePhoneNumberAreaCode", "MSG00004");
    }
}
```

#### 複数項目をまとめてハイライトする（JSPのnameAlias）

相関バリデーションエラーで複数の入力項目をまとめてハイライト表示したい場合は、JSP側で `nameAlias` 属性を使用します。

JSP:
```jsp
<n:text name="users.mobilePhoneNumberAreaCode" nameAlias="users.mobilePhoneNumber" ... />
<n:text name="users.mobilePhoneNumberCityCode" nameAlias="users.mobilePhoneNumber" ... />
<n:text name="users.mobilePhoneNumberSbscrCode" nameAlias="users.mobilePhoneNumber" ... />
```

Java（エイリアス名でメッセージ登録）:
```java
context.addResultMessage("mobilePhoneNumber", "MSG00004");
```

これにより3つの入力項目がすべてハイライト表示されます。

**注意点**:
- バリデーションメソッド内で `ValidationUtil#validate` または `ValidationUtil#validateWithout` を必ず呼び出すこと。呼び出さないと、フレームワークが提供する単項目バリデータによる精査が行われません。
- 相関バリデーションは単項目精査が成功した後（`context.isValid()` が `true` の場合）に実施すること。
- `addResultMessage` は特定のプロパティに紐付けてエラーを表示したい場合に使用し、全体エラーは `addMessage` を使用します。

参照: `component/libraries/libraries-08_02_validation_usage.json#s1`, `guide/web-application/web-application-04_validation.json#s2`, `component/libraries/libraries-07_DisplayTag.json#s4`

###