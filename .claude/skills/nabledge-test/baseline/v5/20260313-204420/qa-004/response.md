**結論**: Nablarch 5でのウェブアプリケーションにおける二重サブミット防止は、**クライアント側**と**サーバ側**の両方を組み合わせて実装する。データベースコミットを伴う処理では必ず両方を使用すること。

**根拠**:

## クライアント側の二重サブミット防止

JavaScriptで実現。1回目のサブミット時に対象要素のonclick属性を書き換え、2回目以降のサブミットをサーバに送信しない（ボタンの場合はdisabled属性も設定）。

Nablarchのカスタムタグ（`n:submit`、`n:button`、`n:submitLink` など）はデフォルトで二重サブミット防止が有効。

特定のボタン/リンクのみ防止を無効にする場合は `allowDoubleSubmission="false"` を指定：

```jsp
<!-- 戻るボタンは二重サブミット防止を無効化 -->
<n:submit type="button" name="back" value="戻る" uri="./back" />
<!-- 登録ボタンは二重サブミット防止を有効に（デフォルト）-->
<n:submit type="button" name="register" value="登録" uri="./register"
          allowDoubleSubmission="false" />
```

## サーバ側の二重サブミット防止

サーバ側で発行した一意なトークンをセッション（サーバ側）とhiddenタグ（クライアント側）に保持し、サーバ側で突合して実現。トークンは1回のチェックに限り有効。

### JSPでのトークン設定

`n:form` タグの `useToken` 属性を `true` に指定：

```jsp
<n:form useToken="true">
  ...
</n:form>
```

### トークンチェック（アクション側）

`@OnDoubleSubmission` インターセプタ（`nablarch.common.web.token.OnDoubleSubmission`）をアクションメソッドに設定：

```java
@OnDoubleSubmission
public HttpResponse register(HttpRequest request, ExecutionContext context) {
    // 登録処理
    return new HttpResponse(303, "/success");
}
```

### JSP以外のテンプレートエンジンを使用する場合

`@UseToken` インターセプタ（`nablarch.common.web.token.UseToken`）を使用してトークンを発行し、テンプレートでトークンをhiddenへ明示的に埋め込む：

```java
@UseToken
public HttpResponse input(HttpRequest request, ExecutionContext context) {
    return new HttpResponse("/WEB-INF/view/register.html");
}
```

### セッションキー/hiddenパラメータ名のカスタマイズ

コンポーネント定義ファイルで変更可能（デフォルト値）：

| 変更対象 | プロパティ名 | デフォルト値 |
|---|---|---|
| セッションスコープのキー | `doubleSubmissionTokenSessionAttributeName` | `/nablarch_session_token` |
| リクエストスコープのキー | `doubleSubmissionTokenRequestAttributeName` | `nablarch_request_token` |
| hiddenのname属性値 | `doubleSubmissionTokenParameterName` | `nablarch_token` |

## スケールアウト環境での対応（DBトークン管理）

スティッキーセッションやセッションレプリケーションを使わずに複数サーバ間でトークンを共有したい場合は、データベースにトークンを保存する `DbTokenManager` を使用する（`nablarch-fw-web-doublesubmit-jdbc` モジュール）。

**注意点**:
- クライアント側・サーバ側の両方を必ず組み合わせること（片方のみでは不十分）
- DBトークン管理を使う場合はCSRF対策を別途実施すること

参照: `component/libraries/libraries-tag.json#s1`, `component/handlers/handlers-on_double_submission.json#s1`, `component/handlers/handlers-use_token.json#s1`, `component/libraries/libraries-db_double_submit.json#s1`
