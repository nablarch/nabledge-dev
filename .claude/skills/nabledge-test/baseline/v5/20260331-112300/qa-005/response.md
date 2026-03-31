**結論**: 相関バリデーションは、Formクラスの `@ValidateFor` アノテーション付きstaticメソッド内で `ValidationContext` を使用して実装する。

**根拠**:

相関バリデーションの実装手順は以下の通り。

**1. @ValidateFor メソッドの実装**

FormクラスにstaticメソッドとArraylistを作成し、`@ValidateFor` アノテーションを付与する。

```java
@ValidateFor("validate")
public static void validate(ValidationContext<SampleForm> context) {
  // Step 1: 各項目のバリデーションを実施
  ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});
  
  // Step 2: エラーがある場合は相関バリデーションをスキップ
  if (!context.isValid()) {
    return;
  }
  
  // Step 3: Formオブジェクトを生成して複数項目を検証
  SampleForm form = context.createObject();
  
  // Step 4: 相関バリデーションのロジック
  if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
    context.addMessage("compareMailAddress");
  }
}
```

**実装パターン（ポイント）**:
1. `ValidationUtil.validate()` で各項目の単項目バリデーションを先に実施する
2. `context.isValid()` でエラーを確認し、エラーがある場合は相関バリデーションをスキップする（不完全な値での比較を防ぐ）
3. `context.createObject()` でFormオブジェクトを生成し、複数項目の値を取得する
4. 相関バリデーションでエラーの場合は `context.addMessage("メッセージID")` でエラーメッセージを追加する

**2. 条件付き相関バリデーション（ウェブアプリケーションのみ）**

ラジオボタンやリストボックスの選択値に応じてバリデーション項目を切り替える場合は、`WebUtil` を使用する。

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

**3. データベースとの相関バリデーション**

データベースとの相関バリデーション（DB照合が必要な場合）は、フォームクラスではなく**業務アクション**で実施する。

**注意点**:
- 相関バリデーションロジックが複数フォームクラスで共通となる場合は、別クラスに抽出して共通化する（Webアプリ・RESTfulウェブサービス共通）
- 各項目のバリデーションが完了するより前に `context.createObject()` を呼ぶと不正な値が含まれる可能性があるため、必ず `context.isValid()` でチェックしてからオブジェクトを生成すること
- `@ValidateFor` 付きのstaticメソッドは、`EntityTestSupport.testSingleValidation()` ではテストされない。独自に実装した相関バリデーションメソッドは別途ユニットテストを作成する必要がある

参照: `libraries-nablarch_validation.json#s4`, `libraries-nablarch_validation.json#s10`, `libraries-nablarch_validation.json#s6`