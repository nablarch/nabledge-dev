**結論**: 相関バリデーション（項目間精査）は、Formクラスの `@ValidateFor` アノテーション付き static メソッド内で、単項目精査実行後に複数プロパティ間の整合性チェックを実装する。エラー時は `ValidationContext#addResultMessage` または `ValidationContext#addMessage` でエラーメッセージを追加する。

**根拠**:

1. **基本的な実装パターン**

   `@ValidateFor` メソッド内で `ValidationUtil.validate` を呼び出して単項目精査を行い、成功後に複数プロパティ値を取得して比較する。

   ```java
   private static final String[] PASSWORD_CHANGE_PROPS
           = new String[] {"id", "prevPassword", "newPassword", "confirmPassword"};

   @ValidateFor("changePassword")
   public static void validateForChangePassword(ValidationContext<User> context) {
       // 1. まず単項目精査を実行
       ValidationUtil.validate(context, PASSWORD_CHANGE_PROPS);
       if (!context.isValid()) return;  // 単項目精査エラー時は中断

       // 2. 精査成功後、複数プロパティ間の整合性チェック
       String newPassword = (String) context.getConvertedValue("newPassword");
       String confirmPassword = (String) context.getConvertedValue("confirmPassword");
       if (!newPassword.equals(confirmPassword)) {
           // プロパティ関連エラー（特定項目にエラーを関連付ける）
           context.addResultMessage("newPassword", "MSG10001");
           // プロパティ非関連エラー（全体エラーの場合）: context.addMessage("MSG10001");
       }
   }
   ```

2. **エラーメッセージ追加メソッドの使い分け**

   | メソッド | 用途 | 例 |
   |---|---|---|
   | `addResultMessage(String propertyName, String messageId, Object... params)` | 特定の項目に対する精査エラー | 新パスワードと確認用パスワードが異なる場合 |
   | `addMessage(String messageId, Object... params)` | 全体に跨るエラー | 検索条件が1つも指定されなかった場合 |

3. **バリデーション実行方法**

   ```java
   ValidationContext<User> result = ValidationUtil.validateAndConvertRequest(
       "user", User.class, req, "changePassword");
   result.abortIfInvalid();
   User user = result.createObject();
   ```

4. **Webアプリケーションでの項目間精査実装例**

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

**注意点**:
- `ValidationUtil#validate` または `ValidationUtil#validateWithout` を呼び出さないと、フレームワーク提供のバリデータによる単項目精査は行われない。相関バリデーション処理前に必ず単項目精査を実施すること。
- 単項目精査失敗（`!context.isValid()`）の場合は早期リターンし、相関バリデーション処理をスキップすること（変換前の値を参照するとエラーになる可能性がある）。
- 処理ごとに精査内容が異なる場合は `@ValidateFor` の値を変えて複数の validateFor メソッドを定義し、呼び出し側で使い分ける。

参照: `component/libraries/libraries-08_02_validation_usage.json#s1`, `guide/web-application/web-application-04_validation.json#s7`, `component/libraries/libraries-08_02_validation_usage.json#s2`, `guide/web-application/web-application-04_validation.json#s3`
