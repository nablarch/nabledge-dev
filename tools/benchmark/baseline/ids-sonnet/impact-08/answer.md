**結論**: Bean Validation（入力チェック）の中でDBへのメールアドレス重複チェックを行うのはセキュリティ上問題がある。ビジネスアクション側で実施すること。

**根拠**:

`component/libraries/libraries-bean_validation.json:s9` に明確な警告がある：

> Bean Validationでデータベースアクセスを行うと、まだバリデーションされていない不正な値をDB問い合わせに使用するため、**SQLインジェクションの脆弱性につながる可能性がある**。

つまり、Bean Validationの実行タイミングでは入力値がまだ完全にバリデーションされていない状態であり、そのままDB問い合わせに渡すと不正な値が混入する危険性がある。

同セクションでは正しいアプローチも明示されている：

> データベースとの相関チェック（例：メールアドレスの重複チェック）は、**Bean Validationを通過した後のビジネスアクション内で実施すること**。

`component/libraries/libraries-nablarch_validation.json:s10` でも同様の指針が示されており、「データベースとの相関バリデーションは業務アクションで行う」と統一されている。

**注意点**:

- Bean Validation は「入力値が安全かどうか」をチェックする層。DBアクセスはその後の業務ロジック層で行うのが正しい設計。
- Nablarchが提供するJDBCラッパー・ユニバーサルDAOはPreparedStatementを使用しSQLインジェクションを排除できるが（`check/security-check/security-check.json:s1`）、問題はDBアクセスのタイミング（未検証値を渡す）にある。
- Bean Validationのバリデーション順序や実行タイミングに依存するため、「どのアノテーションより後に実行されるか」を制御することは難しい。ビジネスアクション側で行う方が安全かつ明確。

参照: component/libraries/libraries-bean_validation.json:s9, component/libraries/libraries-nablarch_validation.json:s10, check/security-check/security-check.json:s1