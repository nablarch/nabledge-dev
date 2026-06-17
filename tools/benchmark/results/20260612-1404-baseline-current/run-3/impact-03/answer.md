**結論**: カスタムバリデータでDB検索する実装は**推奨されません**。DB重複チェックは、Bean Validationが完了した後に業務アクション（リソースクラスのメソッド）側で実装してください。

**根拠**:

Bean ValidationでDBアクセスをすべきでない理由は、セキュリティにあります。Bean Validation実行中のオブジェクトの値は安全である保証がなく、その値を使ってDBアクセスを行うとSQLインジェクション等の脆弱性につながるためです。

**正しい実装の流れ**:

**① Bean Validationをリソースクラスで実行（`@Valid`を付与）**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // この時点でBean Validationは完了 → 値は安全
    // ② ここでDB重複チェックを実装する
    ...
}
```

**② アクション内でUniversalDaoを使って重複チェック**

```java
List<Person> duplicates = UniversalDao.findAllBySqlFile(
    Person.class, "CHECK_DUPLICATE_MAIL", person);

if (!duplicates.isEmpty()) {
    // ③ 特定項目に紐づくエラーを発生させる
    throw new ApplicationException(
        ValidationUtil.createMessageForProperty("person.mailAddress", "duplicate.mailAddress"));
}
```

**注意点**:
- Bean Validationの相関バリデーション（`@AssertTrue`）も、バリデーションの実行順序が保証されないため、DB参照には使用しないこと
- `ValidationUtil#createMessageForProperty`を使うことで、エラーを特定の入力項目に紐づけてハイライト表示できる

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s17, handlers-jaxrs-bean-validation-handler.json:s4, libraries-bean-validation.json:s13, libraries-universal-dao.json:s10