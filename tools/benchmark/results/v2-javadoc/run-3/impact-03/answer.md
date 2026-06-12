Step 5〜8の回答生成とVerifyを行います。

---

**結論**: カスタムバリデータでDB検索する実装は**NG**です。DBへの重複チェックは業務アクション側で実装する必要があります。

**根拠**: Nablarchの公式設計方針として、Bean Validationの中でDBアクセスを行うことは禁止されています。

理由は**セキュリティ上の問題**にあります：

> Bean Validationを使ってデータベースに対する相関バリデーションを実施した場合、バリデーション実施前の安全ではない値を使ってデータベースアクセスを行うことになる。(Bean Validation実行中のオブジェクトの値は、安全である保証がない。)これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装であるため。

**正しい実装パターン**：

1. RESTfulウェブサービスの場合は、リソースクラスのメソッドに `@Valid` アノテーションを設定してBean Validationを実行する
2. Validationが通った後、業務アクション内でバリデーション済みの安全な値を使ってDBに重複チェックを行う
3. 重複が見つかった場合は `ApplicationException` を送出する

```java
// アクションクラスでの実装例（概念）
public HttpResponse create(@Valid ProjectForm form, ExecutionContext context) {
    // ここで form はバリデーション済みの安全な値
    
    // DBで重複チェック
    if (isDuplicate(form.getEmail())) {
        throw new ApplicationException(
            ValidationUtil.createMessageForProperty("form.email", "duplicate.email"));
    }
    
    // 登録処理...
}
```

**注意点**: エラーメッセージを特定の項目に紐づけてクライアントに返したい場合は、`ValidationUtil#createMessageForProperty` を使用してエラーメッセージを構築し、`ApplicationException` を送出します。

参照: libraries-bean-validation.json:s12, libraries-bean-validation.json:s13

---