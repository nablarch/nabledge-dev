**結論**: カスタムバリデータ内でのDB検索による重複チェックは推奨されません。DBとの相関バリデーションは、Bean Validation完了後に**業務アクション側**で実装してください。

**根拠**:

Nablarchの公式ガイドラインでは、Bean Validationの中でデータベースとの相関バリデーションを行うことを明示的に禁止しています。

理由は以下のとおりです：

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)
> これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。

推奨される実装パターンは次のとおりです：

1. Bean Validationで入力値の形式・単項目チェックを実施する（`@Valid` アノテーションでハンドラが自動実行）
2. Bean ValidationがPASSした後、業務アクションのメソッド内でバリデーション済みの安全な値を使ってDBへアクセスし重複チェックを行う

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid  // ← ここでBean Validationが実行される（形式チェックのみ）
public HttpResponse save(Person person) {
    // バリデーション済みの安全な値でDB重複チェックを行う
    long count = UniversalDao.countBySqlFile(Person.class, "CHECK_DUPLICATE", person);
    if (count > 0) {
        throw new ApplicationException(/* 重複エラーメッセージ */);
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**注意点**: `@Valid` アノテーションによってBean Validation（形式チェック等）が実行されてからアクションメソッドに入るため、業務アクション内の値は安全であることが保証されています。この順序を守ることがセキュリティ上重要です。

参照: libraries-bean-validation.json:s12, handlers-jaxrs-bean-validation-handler.json:s4