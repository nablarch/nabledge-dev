**結論**: 二重サブミット防止には、サーバ側のトークンチェック（`useToken` 属性 + `@OnDoubleSubmission` アノテーション）と、JavaScript側のボタン非活性化（`allowDoubleSubmission` 属性）の2つの方法がある。

---

**根拠**:

## 方法1: サーバ側トークンによる二重サブミット防止

サーバ側で発行した一意なトークンをセッション（サーバ側）とhiddenタグ（クライアント側）に保持し、サーバ側で突合することで二重サブミットを検知する。トークンは1回のチェックのみ有効。

### JSPの設定

`n:form` タグの `useToken` 属性に `true` を設定する。

```jsp
<n:form useToken="true">
```

| 条件 | useToken属性の設定 |
|---|---|
| 入力画面と確認画面を共有化している | 設定不要（自動的にトークンが設定される） |
| 共有化していない | `useToken="true"` を設定する |

### Actionクラスの設定

トークンをチェックしたいメソッドに `@OnDoubleSubmission` アノテーションを付与する。

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

`@OnDoubleSubmission` アノテーションの属性:

| 属性 | 説明 |
|---|---|
| `path` | 二重サブミットと判定した場合の遷移先リソースパス |
| `messageId` | 遷移先画面に表示するエラーメッセージのメッセージID |
| `statusCode` | レスポンスステータス（デフォルト: 400） |

### BasicDoubleSubmissionHandler の設定（デフォルト値の一括設定）

アノテーションで個別指定しない場合のデフォルト値は `BasicDoubleSubmissionHandler` のプロパティで設定できる。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
    <property name="messageId" value="MSG00022" />
    <property name="statusCode" value="200" />
</component>
```

### インターセプタ実行順の設定

設定ファイルの `interceptorsOrder` に `OnDoubleSubmission` を定義する（`OnError` より前に定義すること）。

```xml
<list name="interceptorsOrder">
  <value>nablarch.common.web.token.OnDoubleSubmission</value>
  <value>nablarch.fw.web.interceptor.OnErrors</value>
  <value>nablarch.fw.web.interceptor.OnError</value>
</list>
```

---

## 方法2: JavaScriptによる二重サブミット防止（ダブルクリック・ボタン連打防止）

ユーザのダブルクリックやボタン連打でリクエストが複数送信されるのを防ぐ方法。サンプル提供の `button` タグの `allowDoubleSubmission` 属性に `false` を指定する。

```jsp
<n:button uri="..." allowDoubleSubmission="false">登録</n:button>
```

---

**注意点**:

1. **`path` 属性の必須指定**: `@OnDoubleSubmission` アノテーションと `BasicDoubleSubmissionHandler` のいずれにも `path` 属性の指定がない場合、二重サブミット判定時に遷移先不明でシステムエラーになる。トークンを使用する場合、必ずどちらか一方に `path` 属性を指定すること。

2. **複数ウィンドウ並行操作の注意**: 同一業務を複数ウィンドウで並行操作した場合、後に確認画面に遷移したウィンドウのみ処理継続可能。先に遷移したウィンドウのトークンは古くなり、処理実行すると二重サブミットと判定される。

3. **確認画面からの遷移でも再バリデーション必須**: 確認画面からの遷移でも入力データはhiddenタグに保持されているため改ざんの恐れがある。`@OnDoubleSubmission` を付与するActionメソッドでも必ず再バリデーションを実行すること。

4. **カスタムトークン生成**: `TokenGenerator` インタフェースを実装し、リポジトリに `tokenGenerator` という名前で登録することでトークン発行処理を変更できる。デフォルト実装は `RandomTokenGenerator`（16文字のランダム文字列）。

参照: `guide/web-application/web-application-07_insert.json#s6`, `component/libraries/libraries-07_SubmitTag.json#s2`, `guide/web-application/web-application-08_complete.json#s3`, `guide/web-application/web-application-07_insert.json#s5`, `component/handlers/handlers-HttpMethodBinding.json#s6`
