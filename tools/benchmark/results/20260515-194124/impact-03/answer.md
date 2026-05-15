**結論**: カスタムバリデータ（`ConstraintValidator`）の中からDBにアクセスする実装は**推奨されない（避けるべき）**。重複チェックのようなデータベースとの相関バリデーションは、業務アクション側で実装すること。

**根拠**:

Nablarchの公式ドキュメントでは、Bean ValidationでDBアクセスを行う実装を明確に禁止している。

> 「Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、**SQLインジェクションなどの脆弱性の原因となる**ため、さけるべき実装であるため。」

正しい実装パターン：

1. **Bean ValidationでFormの単項目チェックを行う**（入力値の安全性を確保）
2. **業務アクションで、バリデーション済みの安全な値を使ってDBアクセス（重複チェック）を行う**

アクション側でエラーが発生した場合、特定の項目をエラーとして画面にハイライト表示したいときは `ValidationUtil#createMessageForProperty` を使って `ApplicationException` を送出する:

```java
// 業務アクション内でバリデーション済みの値でDB検索して重複チェック
if (duplicateExists(form.getMailAddress())) {
    throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
}
```

Nablarch Validationでも同じ方針が取られており、「データベースとの相関バリデーションは業務アクションで行う」と明記されている。

**注意点**:
- Bean Validationの実行中はオブジェクトの値が安全であることが保証されていないため、この状態でのDB検索は**SQLインジェクション等のセキュリティリスク**を引き起こす可能性がある
- バリデーション後に業務アクションでDBチェックを行うことで、安全な値のみがDBアクセスに使われることが保証される
- アクション側でエラーを返す場合、`ValidationUtil#createMessageForProperty` を使うと画面上で対象項目をエラーとしてハイライト表示できる

参照: `component/libraries/libraries-bean-validation.json#s12`, `component/libraries/libraries-bean-validation.json#s13`, `component/libraries/libraries-nablarch-validation.json#s20`