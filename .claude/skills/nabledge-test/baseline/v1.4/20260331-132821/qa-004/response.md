**結論**: 二重サブミット防止には、**クライアント側（JavaScript）**と**サーバ側（トークン）**の2つの対策を組み合わせて実施します。DBコミットを伴う画面では両方の実施が必要です。

---

**根拠**:

## 1. クライアント側対策：JavaScriptによる二重サブミット防止

サブミットタグ（`n:submit`、`n:button`、`n:submitLink` 等）の `allowDoubleSubmission` 属性を `false` に設定します。

```jsp
<n:submit cssClass="buttons" type="button" name="register" value="登録"
          uri="./USERS00302" allowDoubleSubmission="false" />
```

| 属性 | デフォルト | 説明 |
|---|---|---|
| `allowDoubleSubmission` | `true` | 二重サブミットを許可するか否か。`false` で防止。 |

**仕組み**: 1回目のサブミット時に対象要素の `onclick` 属性を書き換え、2回目以降のサーバ送信をブロック。ボタンの場合は `disabled` 属性も設定。

> **注意**: 1回目のサブミット後にブラウザの中止ボタンを押した場合、ボタンは `disabled` 状態のまま再サブミット不可となります。

---

## 2. サーバ側対策：トークンによる二重サブミット防止

サーバ側で発行した一意なトークンをセッション（サーバ側）と `hidden` タグ（クライアント側）に保持し、サーバ側で突合することで二重サブミットを検知します。トークンは1回のチェックのみ有効です。

### JSP側：useToken属性の設定

`n:form` タグの `useToken` 属性に `true` を設定します。

```jsp
<n:form useToken="true">
```

> **注意**: 入力画面と確認画面のJSPを共通化する機能（`confirmationPage` タグ）を使用している場合は、`useToken="true"` の設定は不要（自動設定される）。

### Action側：@OnDoubleSubmissionアノテーション

トークンをチェックしたいアクションメソッドに `@OnDoubleSubmission` アノテーションを付与します。

```java
@OnError(type = ApplicationException.class, path = "forward:///action/ss11AC/W11AC02Action/RW11AC0201")
@OnDoubleSubmission(path = "forward:///action/ss11AC/W11AC02Action/RW11AC0201")
public HttpResponse doRW11AC0204(HttpRequest req, ExecutionContext ctx) {
    W11AC02Form form = W11AC02Form.validate(req, "register");
    UsersEntity user = new UsersEntity(form.toMap());
    user.setUserId(IdGeneratorUtil.generateUserId());
    getParameterizedSqlStatement("REGISTER_USERS").executeUpdateByObject(user);
    return new HttpResponse("/ss11AC/W11AC0203.jsp");
}
```

| 属性 | 説明 |
|---|---|
| `path` | 二重サブミットと判定した場合の遷移先リソースパス |
| `messageId` | 遷移先画面に表示するエラーメッセージのメッセージID |
| `statusCode` | レスポンスステータス（デフォルト: 400） |

### コンポーネント設定：BasicDoubleSubmissionHandler（任意）

アノテーションで個別指定しない場合のデフォルト値を `BasicDoubleSubmissionHandler` のプロパティで設定できます。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
    <property name="messageId" value="MSG00022" />
    <property name="statusCode" value="200" />
</component>
```

> **警告**: アノテーション・`BasicDoubleSubmissionHandler` のいずれにも `path` 属性の指定がない場合、二重サブミット判定時に遷移先不明でシステムエラーになります。トークンを使用する場合、必ずどちらか一方に `path` 属性を指定してください。

---

**注意点**:

- **両方の対策を実施すること**: クライアント側（`allowDoubleSubmission="false"`）とサーバ側（`useToken` + `@OnDoubleSubmission`）を組み合わせて使用します。
- **useTokenとアノテーションの対応**:
  - 入力画面と確認画面を共通化している場合 → `useToken` 設定不要（自動設定）、`@OnDoubleSubmission` は必要
  - 共通化していない場合 → `useToken="true"` の設定と `@OnDoubleSubmission` の両方が必要
- **複数ウィンドウの注意**: 同一業務を複数ウィンドウで並行操作した場合、後に確認画面に遷移したウィンドウのみ処理継続可能です。
- **Firefox互換性**: Firefoxの古いバージョン（3.x系）では `n:submitLink` でダブルクリック時に2回送信される場合がありますが、サーバ側トークンチェックと併用することで業務処理の2重実行は防止されます。Firefox 9.01以降にアップデートすることで解消します。

---

参照:
- `guide/web-application/web-application-07_insert.json#s6`（サーバ側トークンによる二重サブミット防止）
- `guide/web-application/web-application-07_insert.json#s5`（JavaScriptによる二重サブミット防止）
- `component/libraries/libraries-07_SubmitTag.json#s2`（トークン設定詳細・BasicDoubleSubmissionHandler）
- `component/libraries/libraries-07_SubmitTag.json#s1`（allowDoubleSubmission属性詳細）
- `guide/web-application/web-application-08_complete.json#s3`（実装コード例）
- `processing-pattern/web-application/web-application-14.json#s1`（Firefox互換性）
