**結論**: 相関バリデーションは`@ValidateFor`アノテーションを設定したstaticメソッドで実装します。複数項目の値を比較検証する必要がある場合に使用します。

**根拠**: 

相関バリデーション実装パターンは以下の4ステップです:

1. `ValidationUtil.validate()`で各項目の単項目バリデーションを実施
2. `context.isValid()`でエラー確認し、エラーがある場合は相関バリデーションをスキップ
3. `context.createObject()`でFormを生成して複数項目を検証
4. 相関バリデーションエラーの場合は`context.addMessage("メッセージID")`でメッセージを追加

実装例:
```java
@ValidateFor("validate")
public static void validate(ValidationContext<SampleForm> context) {
  ValidationUtil.validate(context, new String[] {"mailAddress", "confirmMailAddress"});
  if (!context.isValid()) {
    return;
  }
  SampleForm form = context.createObject();
  if (!Objects.equals(form.mailAddress, form.confirmMailAddress)) {
    context.addMessage("compareMailAddress");
  }
}
```

このパターンにより、メールアドレスと確認メールアドレスが一致するか複数項目を検証できます。
