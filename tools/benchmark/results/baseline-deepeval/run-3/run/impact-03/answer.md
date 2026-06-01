**結論**: カスタムバリデータでDB検索する実装はNablarchでは推奨されない。データベースとの相関バリデーション（重複チェック含む）は、**Bean Validationによるチェックが終わった後、業務アクション側で実装する**こと。

**根拠**:

Nablarchのドキュメントには次のように明記されている：

> データベースとの相関バリデーションは、以下理由により業務アクション側で実装すること。
>
> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の**安全ではない値**を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、SQLインジェクションなどの脆弱性の原因となるため、避けるべき実装である。
>
> バリデーション実行後に業務アクションでバリデーションを行うことで、バリデーション済みの安全な値を使用してデータベースへアクセスできる。

RESTfulウェブサービスでの実装フロー：

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid  // ← ここでBean Validationが実行される（形式チェック等）
public HttpResponse save(Person person) {
    // Bean Validationが通過した後、ここでDB重複チェックを行う
    if (UniversalDao.exists(Person.class, /* 重複条件 */)) {
        // 重複エラー処理（業務例外をスローするなど）
        throw new ApplicationException(...);
    }
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

**注意点**: Bean Validationのカスタムバリデータ（`ConstraintValidator`の実装）内でDBアクセスを行うことは、セキュリティ上の理由からNablarchでは明示的に禁止されている。「カスタムバリデータでDB検索」という実装方針は採用しないこと。

参照: libraries-bean-validation.json:s12

---