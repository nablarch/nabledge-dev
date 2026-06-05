Step 5〜7: 回答を生成し検証します。

セクション内容から回答を生成します。

**クレーム検証 (Step 6):**
- 「Bean ValidationのカスタムバリデータでDB検索はNG」→ s12に直接記載 ✅
- 「SQLインジェクションの脆弱性リスク」→ s12に直接記載 ✅
- 「業務アクション側で実装すること」→ s12に直接記載 ✅
- 「バリデーション済みの安全な値でDBアクセスできる」→ s12に直接記載 ✅
- 「`ValidationUtil#createMessageForProperty` + `ApplicationException`」→ s13に直接記載 ✅
- コード例 → s13から引用 ✅

verify_result = PASS

---

**結論**: Bean ValidationのカスタムバリデータでDB検索するのは**NG**です。DBとの相関バリデーションは、Bean Validation完了後の業務アクション側で実装してください。

**根拠**:

Bean Validation実行中のオブジェクトの値は安全である保証がないため、その状態でDBアクセスを行うとSQLインジェクションなどの脆弱性の原因となります（s12）。

バリデーション実行後に業務アクションで実装することで、バリデーション済みの安全な値を使用してデータベースへアクセスできます。

RESTfulウェブサービスでは、リソースクラスのメソッドに `@Valid` を設定してBean Validationを実行し、その後のアクション処理内でDBチェックを行う流れになります：

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // Bean Validationが先に実行される
    // ↓ ここからは検証済みの安全な値なので、DBチェックを実施できる
    // （例）重複チェック
    if (UniversalDao.countBySqlFile(Person.class, "FIND_BY_EMAIL", person) > 0) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

エラーを特定の項目に紐づけて返したい場合は、`ValidationUtil#createMessageForProperty` でエラーメッセージを構築し、`ApplicationException` を送出します（s13）：

```java
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**: Bean Validationの実行順序は保証されないため、`@AssertTrue` 等を使った相関バリデーション（DB以外）では未入力時にNullPointerExceptionが発生しないよう実装する必要があります（s11）。DBチェックはアクション側で行うため、この問題は回避されます。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13, handlers-jaxrs-bean-validation-handler.json:s4

---