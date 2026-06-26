**Bean Validationのカスタムバリデータ内でDBを検索する実装は、Nablarchでは推奨されていません。**

Nablarchの設計指針では、**DBを使った重複チェックなどの相関バリデーションは、業務アクション（リソースクラスのアクションメソッド）側で実装する**ことが求められています。

#### 理由

Bean Validation実行中は、オブジェクトの値が安全であることが保証されません。バリデーション前の未検証の値を使ってDBアクセスを行うと、**SQLインジェクション等の脆弱性の原因**となります。

バリデーションが完了した後、業務アクション側でバリデーション済みの安全な値を使ってDBアクセスすることで、この問題を回避できます。

#### RESTfulウェブサービスでの実装方針

1. **Bean Validationの対象**: 入力値の形式・型・必須チェックなど、DBアクセス不要なバリデーションを `@Valid` アノテーションとBean Validationで実施
2. **DB重複チェック**: リソースクラスのアクションメソッド内で、Bean Validationが通過した後に実施

#### エラーメッセージの項目紐付け

業務アクション側でDB重複チェックをしてエラーが発生した場合、特定のフィールドにエラーを紐づけたい場合は `ValidationUtil#createMessageForProperty` を使用できます。

```java
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

#### まとめ

| やること | 方法 |
|----------|------|
| 形式・必須チェック | Bean Validationのアノテーション（`@NotNull`等） |
| DB重複チェック | 業務アクションのメソッド内でDB検索 |
| エラーメッセージの項目紐付け | `ValidationUtil#createMessageForProperty` |

参照: `component/libraries/libraries-bean-validation.json#データベースとの相関バリデーションを行う`