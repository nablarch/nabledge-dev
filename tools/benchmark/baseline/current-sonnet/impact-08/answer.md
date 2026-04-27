**結論**: メールアドレスの DB 重複チェックを Bean Validation の中で実装するのはセキュリティ上問題がある。Bean Validation を通過した後、ビジネスアクション内で実施すること。

**根拠**:

`component/libraries/libraries-bean_validation.json:s9` に明確な警告がある：

> 「Bean Validationでデータベースアクセスを行うと、**まだバリデーションされていない不正な値をDB問い合わせに使用するため、SQLインジェクションの脆弱性につながる可能性がある**。データベースとの相関チェック（例：メールアドレスの重複チェック）は、Bean Validationを通過した後のビジネスアクション内で実施すること。」

つまり問題の構造は次のとおり：

- Bean Validation のカスタムバリデータ内で DB クエリを発行すると、そのクエリには**まだ検証されていない生の入力値**が使われる
- フォーマット・文字種などの基本チェックが終わっていない値を DB に渡すことになり、悪意ある入力がそのままクエリに乗るリスクがある
- Nablarch（および Jakarta Bean Validation）はバリデーション実行順序を保証しないため、「他のバリデーションが先に終わっている」と仮定することも危険

**正しい実装パターン**（`component/libraries/libraries-bean_validation.json:s9` より）:

1. Bean Validation でメールアドレスの形式・文字種・必須などを検証する
2. Bean Validation をすべて通過した後、ビジネスアクションの処理内で DB を参照して重複チェックを行う
3. 重複があれば業務例外としてエラーを返す（入力チェックエラーと区別することも検討）

**注意点**:

- セキュリティチェックリスト（`check/security-check/security-check.json:s1`）でも、SQLインジェクション対策として「SQL文はプレースホルダで実装」「ウェブアプリのパラメータにSQL文を直接指定しない」が挙げられている。ビジネスアクションで DB 重複チェックを行う際も、UniversalDAO や JDBCラッパーを使い、入力値を直接文字列連結しないこと
- Bean Validation のフレームワーク内（カスタム `ConstraintValidator`）で DI を使って DB アクセスすること自体、Nablarch では明示的に禁止されている

参照: component/libraries/libraries-bean_validation.json:s9, component/libraries/libraries-bean_validation.json:s1, check/security-check/security-check.json:s1