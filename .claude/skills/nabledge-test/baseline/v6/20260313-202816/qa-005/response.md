**結論**: 相関バリデーション（複数フィールド間のバリデーション）は、フォームクラスに `@AssertTrue` アノテーションを付けたメソッドを定義することで実装する。

**根拠**:

フォームクラスに `@AssertTrue` を使ったメソッドを実装する：

```java
public class SampleForm {
    private String mailAddress;
    private String confirmMailAddress;

    @AssertTrue(message = "{compareMailAddress}")
    public boolean isEqualsMailAddress() {
        if (StringUtil.isNullOrEmpty(mailAddress) || StringUtil.isNullOrEmpty(confirmMailAddress)) {
            // どちらかが未入力の場合は相関バリデーションを実施しない（単体バリデーションに任せる）
            return true;
        }
        return Objects.equals(mailAddress, confirmMailAddress);
    }
}
```

相関バリデーションロジックは、フォームクラスが持つ責務であり、ウェブアプリケーションではHTMLのform単位、RESTful WebサービスではAPI単位で作成するフォームクラスに実装する。複数のフォームクラスで共通のロジックになる場合は、別クラスに抽出して共通化する。

**データベースとの相関バリデーション**の場合（例：メールアドレスの重複チェック）は、Bean Validationではなくビジネスアクション内で実施する：

```
(概念図)
1. Bean Validationでフィールド単体チェック
2. バリデーション通過後、ビジネスアクション内でDBアクセスして相関チェック実施
```

**注意点**:

1. **バリデーション実行順序が保証されない**: Jakarta Bean Validationはバリデーションの実行順序を保証しない。相関バリデーションは、フィールド単体のバリデーションより先に呼び出される可能性がある。
2. **null/空チェックを必ず行う**: 対象フィールドがnull/空の状態で呼び出される可能性があるため、その場合は `true` を返して処理をスキップすること（スキップしないと予期せぬ `NullPointerException` が発生する）。
3. **DBアクセスは行わない（セキュリティ）**: Bean Validationの中でデータベースアクセスを行うと、バリデーション前の不正な値でDBアクセスすることになり、SQLインジェクションの脆弱性につながる。

参照: `component/libraries/libraries-bean_validation.json#s8`, `component/libraries/libraries-bean_validation.json#s1`, `component/libraries/libraries-bean_validation.json#s9`
