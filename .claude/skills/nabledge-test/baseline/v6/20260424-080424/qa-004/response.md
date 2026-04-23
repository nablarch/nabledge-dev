**結論**: Nablarchでの二重サブミット防止は、「トークンベース」の仕組みで実装します。具体的には、入力画面側のアクションメソッドに `@UseToken` を付与してトークンを発行し、確定処理側のアクションメソッドに `@OnDoubleSubmission` を付与してトークンを検証することで、同一トークンによる2回目以降のサブミットを防止します。遷移先・メッセージID・ステータスコードなどのデフォルトは `BasicDoubleSubmissionHandler` のコンポーネント定義で指定し、トークンの保管先を HTTP セッションではなくデータベースにしたい場合は `DbTokenManager` + `UUIDV4TokenGenerator` をコンポーネント定義します。

**根拠**:

1. トークン発行側（入力画面を表示するアクション）に `@UseToken` を付与する。

```java
@UseToken
public HttpResponse confirm(HttpRequest req, ExecutionContext ctx) {
    // 省略
}
```

合わせて、フォームに隠しフィールドとしてトークンを埋め込む必要があります（name属性は `nablarch_token`、値はリクエストスコープの `nablarch_request_token`）。

```html
<form th:action="@{/path/to/action}" method="post">
  <input type="hidden" name="nablarch_token" th:value="${nablarch_request_token}" />
```

2. 確定処理側のアクションメソッドに `@OnDoubleSubmission` を付与する。`path` 属性で二重サブミットと判定された場合の遷移先を指定します。

```java
@OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")
public HttpResponse register(HttpRequest req, ExecutionContext ctx) {
    // 省略。
}
```

3. アプリケーション全体のデフォルト値（遷移先リソースパス・メッセージID・ステータスコード）を定義する場合は、`BasicDoubleSubmissionHandler` を `doubleSubmissionHandler` という名前でコンポーネント定義する。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
  <property name="path" value="/WEB-INF/view/error/userError.jsp" />
  <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
  <property name="statusCode" value="200" />
</component>
```

4. トークンをデータベースに保存する場合は、`DOUBLE_SUBMISSION` テーブル（TOKEN(PK), CREATED_AT）を用意し、`tokenManager` として `DbTokenManager`、`tokenGenerator` として `UUIDV4TokenGenerator` をコンポーネント定義する（`tokenManager` は初期化対象に登録する）。

```xml
<component name="tokenManager" class="nablarch.common.web.token.DbTokenManager">
  <property name="dbManager">
    <component class="nablarch.core.db.transaction.SimpleDbTransactionManager">
      <property name="dbTransactionName" value="tokenTransaction"/>
    </component>
  </property>
</component>
<component name="tokenGenerator"
           class="nablarch.common.web.token.UUIDV4TokenGenerator" />
```

5. 振る舞いをカスタマイズしたい場合は、`DoubleSubmissionHandler` インタフェースを実装したクラスを `doubleSubmissionHandler` という名前でコンポーネント定義に追加する。

**注意点**:
- `@OnDoubleSubmission` と `BasicDoubleSubmissionHandler` の **どちらにも `path` 指定がない場合、遷移先不明となりシステムエラー** になります。必ずどちらかに `path` を指定してください。
- `DbTokenManager`（トークンのDB保存）は **テスティングフレームワークのトークン発行機能がDB保存に対応していない** ため、自動テスト実行時は `HttpSessionTokenManager` に差し替える必要があります。
- フォーム内の隠しフィールドは `name="nablarch_token"`、値は `nablarch_request_token` キーで取得する値を設定する必要があります（変更は可能）。

参照:
- `component/handlers/handlers-on-double-submission.json#s1,s3,s4,s5`
- `component/handlers/handlers-use-token.json#s1,s3`
- `component/libraries/libraries-db-double-submit.json#s1,s3`
