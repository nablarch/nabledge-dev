**結論**: 二重サブミット防止は、クライアント側（JavaScriptによるダブルクリック防止）とサーバ側（トークンによる処理済みリクエスト受信防止）の**2つを併用**することが推奨されます。サーバ側の実装では、JSPの `n:form` タグの `useToken` 属性と、ActionクラスへのJavaアノテーション `@OnDoubleSubmission` を組み合わせます。

---

**根拠**:

#### 1. JSP側: `useToken` 属性の設定

確認画面のJSPで、二重サブミットを防止したい `n:form` タグの `useToken` 属性を `true` に設定します。

```jsp
<n:form useToken="true">
  <!-- フォームの内容 -->
</n:form>
```

> **注意**: 入力画面と確認画面のJSPを共通化している場合（`confirmationPage` タグ使用時）は `useToken="true"` の指定は不要で、自動的にトークンが設定されます。

| 入力/確認画面の共通化 | useToken属性の設定 | アノテーションの付与 |
|---|---|---|
| 共通化している | 設定不要（自動設定） | 必要 |
| 共通化していない | `true` を設定 | 必要 |

#### 2. Actionクラス側: `@OnDoubleSubmission` アノテーションの付与

二重サブミットをチェックしたいActionメソッドに `@OnDoubleSubmission` アノテーションを付与します。

```java
@OnError(type = ApplicationException.class, path = "forward://RW11AC0201")
@OnDoubleSubmission(
    path = "forward://RW11AC0201"  // 二重サブミット判定時の遷移先パス
)
public HttpResponse doRW11AC0204(HttpRequest req, ExecutionContext ctx) {
    // 入力データは改竄の恐れがあるため、再度バリデーションを必ず実施する
    W11AC02Form form = validate(req);
    // ... 処理 ...
    return new HttpResponse("/ss11AC/W11AC0203.jsp");
}
```

`@OnDoubleSubmission` の属性:

| 属性 | デフォルト | 説明 |
|---|---|---|
| `path` | （必須） | 二重サブミット判定時の遷移先リソースパス |
| `messageId` | | 遷移先画面に表示するエラーメッセージID |
| `statusCode` | 400 | レスポンスステータスコード |

#### 3. 仕組み

- サーバ側（セッション）とクライアント側（hiddenタグ）に一意なトークンを保持し、突合することで実現
- トークンは1回のチェックのみ有効
- デフォルトのトークン実装: `RandomTokenGenerator`（16文字のランダム文字列）

#### 4. アプリケーション全体のデフォルト設定（任意）

`BasicDoubleSubmissionHandler` をリポジトリに登録することで、全体のデフォルト値を設定できます。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
    <property name="messageId" value="MSG00022" />
    <property name="statusCode" value="200" />
</component>
```

---

**注意点**:

- `@OnDoubleSubmission` アノテーションにも `BasicDoubleSubmissionHandler` にも `path` 属性が指定されていない場合、遷移先が不明でシステムエラーになります。**必ずどちらか一方で `path` を指定してください。**
- 確認画面から遷移した場合でも、hiddenタグ経由のデータは改竄される恐れがあるため、Actionメソッドで**再度バリデーション（`validate(req)`）を必ず実施**してください。
- 同一業務を**複数ウィンドウで並行操作**した場合、後に確認画面に遷移したウィンドウのみトークンが有効となります。先のウィンドウは二重サブミット判定されます（別業務の並行操作は問題なし）。

参照: `component/libraries/libraries-07_SubmitTag.json#s3`, `guide/web-application/web-application-07_insert.json#s4`, `guide/web-application/web-application-07_insert.json#s8`
