**結論**: カスタムバリデータ内でDB検索する実装は避けること。データベースとの重複チェックは、Bean Validationではなく**業務アクション側**でBeanのバリデーション完了後に実装する。

**根拠**:

Nablarchのドキュメントでは、以下の理由からBean Validationの中でDBアクセスを行うことを明確に禁止している。

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。（Bean Validation実行中のオブジェクトの値は、安全である保証がない。）これは、SQLインジェクションなどの脆弱性の原因となるため、避けるべき実装である。

正しい実装方針は以下のとおり。

1. Bean Validationで入力値の形式・必須などの単項目チェックを実施する
2. バリデーションが通った後、業務アクション内でバリデーション済みの安全な値を使ってDB重複チェックを実施する

```java
// リソースクラス（アクション）でのDB重複チェック実装例
public HttpResponse register(@Valid SampleForm form, ExecutionContext context) {
    // ここまで来た時点でformの値はBean Validationで検証済み
    // 安全な値を使ってDB検索（重複チェック）を行う
    if (isDuplicate(form.getMailAddress())) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
    }
    // 登録処理...
}
```

**注意点**:
- 重複エラーを特定フィールドのエラーとして画面に表示したい場合は、`ValidationUtil#createMessageForProperty`でエラーメッセージを構築し、`ApplicationException`を送出すること
- RESTfulウェブサービスでBean Validationを動作させるには、リソースクラスのメソッド引数に`@Valid`アノテーションを設定すること

参照: component/libraries/libraries-bean-validation.json:s12, component/libraries/libraries-bean-validation.json:s13, component/libraries/libraries-bean-validation.json:s17