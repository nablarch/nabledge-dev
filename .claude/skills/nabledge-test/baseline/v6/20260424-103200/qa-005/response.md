**結論**: 相関バリデーション（複数項目を使った検証）は、Nablarch 6 では主に **Jakarta Bean Validation の `@AssertTrue` アノテーションを使う方法**で実装します。従来の Nablarch Validation を使う場合は、Beanクラスに `@ValidateFor` アノテーションを付けた静的メソッドを実装し、`ValidationContext` にメッセージを追加する方法で実装します。

**根拠**:

1. **Bean Validationによる相関バリデーション（推奨）**

   Beanのboolean型getterに `@AssertTrue` を付け、項目間の整合性を判定します。

   ```java
   public class SampleForm {
     private String mailAddress;
     private String confirmMailAddress;

     @AssertTrue(message = "{compareMailAddress}")
     public boolean isEqualsMailAddress() {
       return Objects.equals(mailAddress, confirmMailAddress);
     }
   }
   ```

   任意項目の場合は、未入力時に `true` を返してスキップするロジックを入れる必要があります。

2. **Nablarch Validationによる相関バリデーション**

   `@ValidateFor` を付けた static メソッドで、項目単体のバリデーション後に相関チェックを実施します。エラー時は `ValidationContext#addMessage` でメッセージIDを追加します。

   ```java
   @ValidateFor("validate")
   public static void validate(ValidationContext<SampleForm> context) {
     ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});
     if (!context.isValid()) { return; }
     SampleForm form = context.createObject();
     if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
       context.addMessage("compareMailAddress");
     }
   }
   ```

3. **画面へのエラー表示**

   相関バリデーションのエラーを特定項目の近くに表示したい場合は、`<n:password>` などの入力項目タグで `nameAlias` 属性に相関バリデーションのプロパティ名を指定し、`<n:error>` タグで表示します。ハイライト表示も `nameAlias` 経由で有効化できます。

**注意点**:

- **Jakarta Bean Validation ではバリデーションの実行順序が保証されない**ため、項目単体のバリデーションより前に相関バリデーションが呼ばれる可能性があります。未入力チェックなどを相関バリデーション側にも入れる必要があります。
- **データベースとの相関バリデーションは Bean Validation では行わず、業務アクション側で実装すること**。Bean Validation 実行中の値は安全性が保証されておらず、SQLインジェクションなどの脆弱性の原因になるためです。アクション側でエラーとなった場合は `ValidationUtil.createMessageForProperty` でメッセージを構築し `ApplicationException` を送出します。

参照:
- `component/libraries/libraries-bean-validation.json#s11`
- `component/libraries/libraries-bean-validation.json#s12`
- `component/libraries/libraries-bean-validation.json#s13`
- `component/libraries/libraries-nablarch-validation.json#s14`
- `component/libraries/libraries-tag.json#s29`
