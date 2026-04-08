**結論**: 相関バリデーションは、フォームクラスに `@ValidateFor` アノテーションを付けた `static` メソッドを実装し、その中で各項目のバリデーション後にエラーがなければ複数項目を組み合わせたチェックを行う形で実装する。

**根拠**:

相関バリデーションの実装手順は以下の通り。

1. **`@ValidateFor` アノテーションを付けた static メソッドをフォームクラスに定義する**

   ```java
   @ValidateFor("validate")
   public static void validate(ValidationContext<SampleForm> context) {
       // まず各項目のバリデーションを実施
       ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});
   
       // エラーがある場合は相関バリデーションを実施しない
       if (!context.isValid()) {
           return;
       }
   
       // 相関バリデーションの実施（フォームオブジェクトを生成して比較）
       SampleForm form = context.createObject();
       if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
           context.addMessage("compareMailAddress");  // エラーメッセージIDを追加
       }
   }
   ```

2. **実装のポイント**:
   - まず `ValidationUtil.validate()` で各項目のバリデーションを実行する
   - `context.isValid()` でエラーなしを確認してから相関バリデーションを実施する
   - 相関バリデーションでエラーが発生した場合は、`ValidationContext.addMessage()` でエラーメッセージIDを追加する

3. **条件付きバリデーション（ラジオボタン・リストボックスの選択値に応じた切り替え）**:

   `WebUtil` を使うことで、選択値に応じてバリデーション項目を切り替えることができる。

   ```java
   @ValidateFor("validate")
   public static void validate(ValidationContext<SampleForm> context) {
       if (WebUtil.containsPropertyKeyValue(context, "form.radio", "ptn1")) {
           ValidationUtil.validate(context, new String[] {"item1"});
       } else {
           ValidationUtil.validate(context, new String[] {"item1", "item2"});
       }
   }
   ```

4. **設計上の配置**:
   - **ウェブアプリケーション**: 相関バリデーションのロジックはフォームクラスに持たせる。複数フォームで共通ロジックがある場合は別クラスに抽出して共通化する。
   - **RESTfulウェブサービス**: 同様に、相関バリデーションロジックはフォームクラスに持たせ、共通ロジックは別クラスに抽出する。

5. **データベースとの相関バリデーション**:
   データベースを使った相関バリデーション（例: 入力値の存在チェックなど）は業務アクションクラスで行う（詳細は `libraries-bean_validation.json#s8` を参照）。

**注意点**:
- 相関バリデーションは、**各項目のバリデーションが全てエラーなしの場合にのみ実行すること**（`context.isValid()` チェックを忘れないこと）
- 個別アノテーション設定はメンテナンスコストが増えるため、ドメインバリデーション（`@Domain`）の使用を推奨する
- OpenAPI Generator を使用する場合、自動生成モデルに相関バリデーションを直接実装できないため、手動実装のフォームクラスを別途作成し、`BeanUtil` でプロパティ値をコピー後にバリデーションを実施するアプローチをとること

参照: `component/libraries/libraries-nablarch_validation.json#s4`, `component/libraries/libraries-nablarch_validation.json#s1`, `component/libraries/libraries-nablarch_validation.json#s6`, `component/libraries/libraries-nablarch_validation.json#s10`, `processing-pattern/web-application/web-application-application_design.json#s1`, `processing-pattern/restful-web-service/restful-web-service-application_design.json#s1`, `development-tools/toolbox/toolbox-NablarchOpenApiGenerator.json#s7`