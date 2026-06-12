**結論**: Bean ValidationのカスタムバリデータでDB検索する実装は**推奨されない**。DBとの重複チェックは、`@Valid`によるBean Validationが完了した後、業務アクション（リソースクラス）側で実装すること。

**根拠**:

Bean Validation実行中のオブジェクトの値は安全である保証がないため、その値を使ってDBアクセスを行うとSQLインジェクションなどの脆弱性の原因となる。これがカスタムバリデータ内でのDB検索を避けるべき理由。

**RESTfulウェブサービスでの実装フロー:**

① `@Valid`アノテーションでBean Validationを実行する（通常の入力値チェック）:

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // ここに到達した時点でBean Validationは完了しており、
    // personの値はバリデーション済みで安全
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

② Bean Validationが通過した後、アクション内でDB重複チェックを実装する。重複が検出された場合は、特定フィールドへのエラーメッセージを`ValidationUtil#createMessageForProperty`で構築し、`ApplicationException`を送出する:

```java
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**:
- バリデーション実行後の安全な値を使ってDBアクセスすることが重要。Bean Validation内でDBアクセスすると、未検証の値がSQLに渡されるリスクがある。
- `handlers-jaxrs-bean-validation-handler`はリクエストボディ変換ハンドラよりも後ろに設定する必要がある。

参照: `libraries-bean-validation.json:s12`, `libraries-bean-validation.json:s13`, `handlers-jaxrs-bean-validation-handler.json:s4`, `libraries-bean-validation.json:s17`

---