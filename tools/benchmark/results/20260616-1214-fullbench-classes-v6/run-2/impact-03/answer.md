**結論**: Bean Validation（カスタムバリデータ含む）の中でDBに問い合わせる重複チェックの実装は推奨されません。DB検索による重複チェックは**業務アクション側**で実装してください。

**根拠**: Nablarchの公式設計方針として、Bean Validationでデータベースとの相関バリデーションを行うことが明示的に禁止されています。

> データベースとの相関バリデーションは、以下理由により業務アクション側で実装すること。
> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)
> これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。

推奨する実装パターンは、RESTfulウェブサービスの場合:

1. `@Valid` アノテーションによるBean Validationで入力値の形式チェックを実施
2. バリデーション通過後、業務アクションメソッド内でUniversalDaoなどを使ってDB検索し、重複チェックを実行
3. 重複が見つかった場合は、特定の項目にエラーを紐付けたい場合は `ValidationUtil#createMessageForProperty` を使用して `ApplicationException` を送出

```java
// アクションメソッド内での重複チェック実装例
public HttpResponse create(JaxRsHttpRequest request, ExecutionContext context) {
    SampleForm form = ...; // @Valid でバリデーション済み

    // バリデーション済みの安全な値を使ってDB検索
    if (isDuplicate(form.getMailAddress())) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
    }
    // 業務処理...
}
```

**注意点**: Bean Validationのカスタムバリデータ（`ConstraintValidator`実装）内でもDBアクセスは同じ理由で避けるべきです。バリデーション実行中はオブジェクトの値の安全性が保証されておらず、セキュリティ上のリスクがあります。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13