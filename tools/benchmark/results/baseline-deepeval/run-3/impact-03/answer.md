Step 5-7: 回答を生成し、verify を実行します。

s12が質問の核心に直接答えています。カスタムバリデータでのDB検索は**推奨されない**ことが明示されており、理由も記載されています。

---

**結論**: カスタムバリデータ内でのDB検索は実装してはならない。DB重複チェックはBean Validationの後、業務アクション側で実装すること。

**根拠**:

Bean Validation実行中はオブジェクトの値が安全である保証がないため、バリデータ内でDBアクセスを行うとSQLインジェクション等の脆弱性の原因となる（s12）。

```
Bean Validation実行中のオブジェクトの値は、安全である保証がない。
これは、SQLインジェクションなどの脆弱性の原因となるため、さけるべき実装である。
```

正しいアプローチは以下の流れ：

**① Bean Validationを @Valid アノテーションで実行**（リソースクラスのメソッドに付与）

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    // ここに来た時点で person の値はバリデーション済みで安全
    // ② DB重複チェックをここで行う
    ...
}
```

**② アクションメソッド内でDB重複チェックを実装**

バリデーション済みの安全な値を使ってDBアクセスできる。重複が見つかった場合は `ValidationUtil#createMessageForProperty` を使って対象項目のエラーメッセージを構築し、`ApplicationException` を送出する（s13）：

```java
throw new ApplicationException(
        ValidationUtil.createMessageForProperty("form.mailAddress", "duplicate.mailAddress"));
```

**注意点**:

- カスタムバリデータはプロジェクト固有のアノテーション・ロジックとして追加できるが（s24）、DBアクセスを伴う処理には適用してはならない。この制約はNablarchの設計上の安全要件であり、RESTfulウェブサービスも例外ではない。

参照: `libraries-bean-validation.json:s12`, `libraries-bean-validation.json:s13`, `handlers-jaxrs-bean-validation-handler.json:s4`

---