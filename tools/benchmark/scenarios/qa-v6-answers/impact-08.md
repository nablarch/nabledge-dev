**質問**: フォームで入力されたメールアドレスが DB 上ですでに登録済みでないかチェックしたい。入力チェックのところでこれを書きたいんだけど、セキュリティ的に問題ない？

---

**結論**: **セキュリティ上の問題がある**。Bean Validation（入力チェック）で DB アクセスを行うと、**まだバリデーションされていない不正な値を SQL 問い合わせに使う** ことになり、SQL インジェクション脆弱性につながる可能性がある。Nablarch では、DB との相関チェック（例: メールアドレスの重複チェック）は **Bean Validation 通過後のビジネスアクション側で実施** することとされている。 — `component/libraries/libraries-bean_validation.json#s9`

**① 禁止理由**
> データベースとの相関バリデーションは、Bean Validation では行わずビジネスアクション側で実施すること。

Bean Validation で DB アクセスを行うと、未バリデーションの不正値を DB 問い合わせに使うため SQL インジェクションの脆弱性につながる可能性がある。 — `component/libraries/libraries-bean_validation.json#s9`

**② 正しいやり方**
DB との相関チェック（重複チェックなど）は、Bean Validation を通過した後のビジネスアクション内で実施する。 — `component/libraries/libraries-bean_validation.json#s9`

**③ 入力チェック段階で可能な相関バリデーション**
フィールド **同士** の相関チェック（例: メール入力と確認入力の一致など）は `@AssertTrue` で Bean Validation 内に書いてよい。Jakarta Bean Validation は実行順序を保証しないため、対象フィールドが null/空の場合は `true` を返してスキップする。

```java
@AssertTrue(message = "{compareMailAddress}")
public boolean isEqualsMailAddress() {
    if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
        return true;
    }
    return Objects.equals(mailAddress, confirmMailAddress);
}
```
— `component/libraries/libraries-bean_validation.json#s8`
