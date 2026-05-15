**結論**: Bean Validationのカスタムバリデータ内でDB検索する実装は**避けるべき**です。DBとの相関バリデーションは**業務アクション側**で実装してください。

**根拠**:

Nablarchの公式ドキュメントでは明確に以下のように定めています。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の**安全ではない値**を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、**SQLインジェクションなどの脆弱性の原因**となるため、避けるべき実装である。

推奨される実装パターンは以下の通りです：

1. **まずBean Validationを実行**して入力値を安全な状態にする
2. **バリデーション通過後、業務アクションのメソッド内**で重複チェックのDBアクセスを行う

```java
// 業務アクション内での実装例（概念）
public HttpResponse register(HttpRequest request, ExecutionContext context) {
    // 1. Bean Validationでフォームの入力値を検証（安全な値になる）
    SampleForm form = EntityUtil.setProperty(request.getParamMap(), SampleForm.class);
    ValidatorUtil.validate(form);  // バリデーション後は安全な値が保証される

    // 2. バリデーション済みの安全な値でDB重複チェック
    if (userRepository.existsByEmail(form.getMailAddress())) {
        // 重複エラー処理
    }
    // 3. 業務処理続行
}
```

**注意点**:

- `ConstraintValidator`の`isValid()`メソッド内でUniversalDaoやJDBCを使ってDBアクセスする実装は、Nablarchでは**明示的に禁止**されています
- Bean Validation実行中の値はバリデーション未完了のため、SQLインジェクションなどのセキュリティリスクがあります
- 「カスタムバリデータを作れば実現できる」と考えがちですが、それ自体がアーキテクチャ上の脆弱性になります
- プロジェクト固有のバリデーションアノテーション追加は可能ですが（`s24`参照）、その中でのDB検索は同様の理由で避けてください

参照: `component/libraries/libraries-bean-validation.json#s12`