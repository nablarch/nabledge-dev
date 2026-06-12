**Step 4:** `read_sections` = `["libraries-bean-validation.json:s12", "libraries-bean-validation.json:s13", "handlers-jaxrs-bean-validation-handler.json:s4"]`

**Step 5: 回答生成**

---

**結論**: Bean Validationのカスタムバリデータ内でDB検索するのは**推奨されない**。データベースとの相関バリデーションは、Bean Validation完了後に業務アクション側で実装すること。

**根拠**:

Bean Validationの実行中は、オブジェクトの値が安全であることが保証されない。この状態でDBアクセスを行うと、バリデーション前の安全ではない値でSQL発行することになり、**SQLインジェクションなどの脆弱性の原因**となる。

推奨される実装パターンは以下のとおり：

1. **リソースクラスに `@Valid` を付与してBean Validationを実行**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // この時点でBean Validationは完了しており、personの値は安全
    // ここでDB重複チェックを実施する
    long count = UniversalDao.countBySqlFile(Person.class, "CHECK_DUPLICATE", person);
    if (count > 0) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.email", "duplicate.email"));
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

2. **エラーを特定の項目に紐付けたい場合**は `ValidationUtil#createMessageForProperty` を使って `ApplicationException` を送出することで、対象フィールドに紐づいたバリデーションエラーとして扱える。

**注意点**:
- Bean Validation（`@Valid`）の実行はハンドラが自動で行うため、アクションメソッドに到達した時点ではBean Validationは完了済みで値は安全
- DB重複チェックはBean Validationとは別フェーズで行う設計にすること

参照: `libraries-bean-validation.json:s12`, `libraries-bean-validation.json:s13`, `handlers-jaxrs-bean-validation-handler.json:s4`

---