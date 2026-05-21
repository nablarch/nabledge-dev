**結論**: Bean ValidationのカスタムバリデータでDB検索する実装は**推奨されない**。DB重複チェックはバリデーション後に**業務アクション（リソースクラス）側**で実装すること。

**根拠**:

Nablarchのドキュメントに明確な理由が記載されている：

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装である。

推奨される実装パターン（RESTfulウェブサービスの場合）：

**1. 入力値バリデーション**はリソースクラスのメソッドに `@Valid` アノテーションを付けて実行する：

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**2. DB重複チェック**は `@Valid` によるバリデーション通過後、リソースクラスのメソッド本体で実装する。エラー時は `ValidationUtil#createMessageForProperty` で特定項目に紐づいたエラーメッセージを生成し、`ApplicationException` を送出する：

```java
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**:

- Bean Validation（`@Valid`）通過後にDB検索を行うことで、バリデーション済みの安全な値でDBアクセスできる。カスタムバリデータ内でのDB検索はSQLインジェクションリスクがあるため実装してはならない。
- 要件を満たす既存バリデータがない場合にカスタムバリデータを追加することは可能だが、DB検索をカスタムバリデータに含めることは上記理由により不可。

参照: `libraries-bean-validation.json:s12`, `libraries-bean-validation.json:s13`, `libraries-bean-validation.json:s17`, `handlers-jaxrs-bean-validation-handler.json:s4`

---