Step 5: 回答を生成します。

**結論：** カスタムバリデータ内でDB検索する実装はNablarchでは**推奨されていません**。DB重複チェックは、Bean Validationの後に業務アクション側で実装する必要があります。

**verify:** s12の内容と照合。
- 「Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる」→ 直接記載あり
- 「SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装」→ 直接記載あり
- 「バリデーション実行後に業務アクションでバリデーションを行うことで、バリデーション済みの安全な値を使用してデータベースへアクセスできる」→ 直接記載あり
- `ValidationUtil#createMessageForProperty` と `ApplicationException` → s13に直接記載あり

verify_result = **PASS**

---

**結論**: カスタムバリデータ（Bean Validation）の中でDB検索する実装はNablarchでは**避けるべき**とされており、代わりに業務アクション側でDB重複チェックを実装する必要があります。

**根拠**:

Nablarchのドキュメントに以下の理由が明記されています：

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装である。

**正しい実装パターン**:

1. Bean Validationで入力値の基本チェック（文字種・桁数等）を実施
2. バリデーション通過後、業務アクションのメソッド内でDB重複チェックを実施
3. 重複が検出された場合は `ApplicationException` をスローする

特定の項目のエラーとして表示したい場合は、`ValidationUtil#createMessageForProperty` を使用します：

```java
// 業務アクション内でDB重複チェックを行い、重複があれば例外をスロー
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**: Bean Validationの実行順序は保証されないため、カスタムバリデータ内で他の項目のバリデーション済みを前提とした処理は行えません。DB重複チェックを業務アクション側に置くことで、入力値が安全であることを保証した上でDBアクセスできます。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13

---