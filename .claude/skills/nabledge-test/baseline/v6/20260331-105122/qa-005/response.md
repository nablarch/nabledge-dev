**結論**: 相関バリデーション（複数項目を組み合わせたバリデーション）は、フォームクラスに `@ValidateFor` アノテーションを付けたstaticメソッドを実装することで行います。まず項目ごとのバリデーションを実施し、エラーがなかった場合にのみ相関バリデーションを実行します。

**根拠**:

実装手順は以下の通りです。

1. フォームクラスにstaticメソッドを作成し、`@ValidateFor` アノテーションを付ける
2. メソッド内で `ValidationUtil.validate()` を呼び出して個別項目のバリデーションを実行する
3. `context.isValid()` でエラーがないか確認してから相関バリデーションを実行する
4. 相関バリデーションでエラーとなった場合は `context.addMessage()` でメッセージIDを追加する

```java
@ValidateFor("validate")
public static void validate(ValidationContext<SampleForm> context) {
    // まず個別項目のバリデーションを実施
    ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});

    // エラーがある場合は相関バリデーションを実施しない
    if (!context.isValid()) {
        return;
    }

    // 相関バリデーションの実施
    SampleForm form = context.createObject();
    if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
        context.addMessage("compareMailAddress");  // エラーメッセージIDを追加
    }
}
```

**エラー表示（Webアプリケーションの場合）**:

相関バリデーションのエラーメッセージを特定の入力項目の近くに表示する場合は、JSPで `<n:error>` タグの `name` 属性に相関バリデーションで設定されるプロパティ名を指定します。また、`nameAlias` 属性を指定することで複数の入力項目をハイライト表示できます。

```jsp
<n:password name="form.password" nameAlias="form.comparePassword" />
<n:error name="form.password" messageFormat="span" errorCss="alert alert-danger" />
<!-- 相関バリデーションで指定されるプロパティ名をname属性に指定 -->
<n:error name="form.comparePassword" messageFormat="span" errorCss="alert alert-danger" />
```

**データベースとの相関バリデーション**:

データベースとの相関バリデーション（DBの既存データとの照合など）は、フォームクラスではなく業務アクションで実施します。

**注意点**:
- 相関バリデーションは必ず個別項目バリデーション（`ValidationUtil.validate()`）が正常に完了した後に実行すること。`context.isValid()` で確認しないと、変換前の不正な値でオブジェクトを生成しようとしてエラーになる可能性があります。
- 相関バリデーションのロジックが複数のフォームクラスで共通になる場合は、別クラスに抽出して共通化すること（Webアプリケーション/RESTful Webサービスの設計ルール）。
- OpenAPI Generatorを使用する場合、自動生成モデルへの相関バリデーション実装は不可。同じプロパティ定義を持つ手動実装フォームクラスを作成し、`BeanUtil` でプロパティ値をコピーした後にバリデーションを実施するアプローチを使用すること。

参照: `component/libraries/libraries-nablarch_validation.json#s4`, `component/libraries/libraries-nablarch_validation.json#s10`, `processing-pattern/web-application/web-application-application_design.json#s1`, `processing-pattern/restful-web-service/restful-web-service-application_design.json#s1`, `component/libraries/libraries-tag.json#s2`
