**結論**: 相関バリデーション（複数項目をまたいだバリデーション）は、`@ValidateFor` アノテーションを付けた static メソッド内で `ValidationContext` を使って実装します。

**根拠**:

相関バリデーションの実装手順:

1. フォームクラスに `@ValidateFor("メソッド識別子")` アノテーションを付けた static メソッドを作成する
2. `ValidationUtil.validate()` で各項目の単項目バリデーションを実行する
3. `context.isValid()` でエラーがないか確認し、エラーがある場合は相関バリデーションをスキップする
4. `context.createObject()` でフォームオブジェクトを生成して複数項目の値を比較・検証する
5. 相関バリデーションエラーの場合は `context.addMessage("メッセージID")` でエラーメッセージを追加する

```java
@ValidateFor("validate")
public static void validate(ValidationContext<SampleForm> context) {
    // Step 1: 各項目の単項目バリデーションを実行
    ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

    // Step 2: 単項目バリデーションにエラーがあればスキップ
    if (!context.isValid()) {
        return;
    }

    // Step 3: フォームオブジェクトを生成して複数項目を比較
    SampleForm form = context.createObject();
    if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
        // Step 4: 相関エラーのメッセージを追加
        context.addMessage("compareMailAddress");
    }
}
```

**関連クラス・アノテーション**:
- `nablarch.core.validation.ValidationContext`
- `@ValidateFor`（`nablarch.core.validation`）
- `ValidationUtil.validate()`

**条件付きバリデーション（ラジオボタン等の選択値によって検証項目を切り替える場合）**:

`nablarch.common.web.WebUtil` を使うと、送信値に応じてバリデーション対象項目を切り替えられます。

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

**データベースとの相関バリデーション**:

データベースを使った相関バリデーション（例：重複チェック）は、フォームクラスではなく業務アクションクラスで実施します。

**注意点**:
- 相関バリデーションは単項目バリデーション後に実行すること。`context.isValid()` で単項目エラーを確認してから相関チェックを行うのが基本パターンです。単項目エラーがある状態で `createObject()` を呼んでも正しい値が得られない場合があります。
- `@ValidateFor` を付けた static メソッドはテスティングフレームワークの単項目精査テスト（`testSingleValidation`）ではテストされません。相関バリデーションメソッドは別途テストを作成してください。
- RESTful ウェブサービスのフォームクラスでも同様に相関バリデーションを実装できます。複数フォームクラスで共通ロジックが発生する場合は別クラスに抽出して共通化することを推奨します。
- このバリデーション機能（Nablarch Validation）は利用可能ですが、公式には [Bean Validation](../../component/libraries/libraries-bean_validation.json) の使用が推奨されています。

参照: `libraries-nablarch_validation.json#s4`, `libraries-nablarch_validation.json#s1`, `libraries-nablarch_validation.json#s6`, `libraries-nablarch_validation.json#s10`, `restful-web-service-application_design.json#s1`, `testing-framework-02_entityUnitTestWithNablarchValidation.json#s6`
