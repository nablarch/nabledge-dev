**結論**: 二重サブミット防止には「JavaScript方式」と「トークン方式」の2種類があり、DBの登録・更新処理を行う場合はサーバ側のトークン方式を併用することが推奨されます。

---

**根拠**:

### JavaScript方式（クライアント側対策）

`n:submit` タグの `allowDoubleSubmission` 属性に `false` を指定する。1回目のサブミット後にボタンの `onclick` 属性を書き換え、2回目以降のサーバ送信を防止する（ボタンには `disabled` 属性も設定される）。

```jsp
<n:submit cssClass="buttons" type="button" name="register" value="登録"
          uri="./USERS00302" allowDoubleSubmission="false" />
```

> 注意: ユーザがブラウザの中止ボタンを押した場合、ボタンはdisabled状態のままとなるため、他のボタン/リンクで処理を継続する必要があります。

---

### トークン方式（サーバ側対策）

サーバ側(セッション)とクライアント側(hiddenタグ)に一意なトークンを保持し、サーバ側で突合することで二重サブミットを防止する。JSP側とAction側の両方に実装が必要。

#### JSP側（formタグの設定）

`n:form` タグの `useToken` 属性に `true` を設定する。

```jsp
<n:form useToken="true">
```

| 入力画面と確認画面の共通化 | useToken属性の設定 | @OnDoubleSubmissionアノテーション |
|---|---|---|
| 共有化している | 設定不要（自動的にトークンが設定される） | 必要 |
| 共有化していない | `true` を設定する | 必要 |

#### Action側（アノテーションの設定）

トークンをチェックしたいメソッドに `@OnDoubleSubmission` アノテーションを付与する。

```java
@OnDoubleSubmission(
    path = "forward://RW11AC0201"  // 二重サブミット判定時の遷移先
)
public HttpResponse doRW11AC0204(HttpRequest req, ExecutionContext ctx) {
    // 処理
}
```

| 属性 | 説明 | デフォルト値 |
|---|---|---|
| path | 二重サブミット判定時の遷移先リソースパス | なし |
| messageId | 二重サブミット判定時のエラーメッセージID | なし |
| statusCode | 二重サブミット判定時のレスポンスステータス | 400 (Bad Request) |

#### アプリケーション全体のデフォルト設定（任意）

`BasicDoubleSubmissionHandler` をリポジトリに登録することでアプリケーション全体のデフォルト値を設定できる。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
    <property name="messageId" value="MSG00022" />
    <property name="statusCode" value="200" />
</component>
```

---

**注意点**:

1. **path属性は必ず指定すること**: `@OnDoubleSubmission` アノテーションと `BasicDoubleSubmissionHandler` の両方で `path` 属性が未指定の場合、二重サブミット判定時にシステムエラーが発生します。
2. **複数ウィンドウ並行操作の制約**: 同じ業務を複数ウィンドウで並行操作した場合、後に確認画面に遷移したウィンドウのみ処理継続可能。先に確認画面に遷移したウィンドウはトークンが古くなり二重サブミットと判定されます（別々の業務を複数ウィンドウで操作する場合は問題なし）。
3. **Firefoxの既知問題**: 古いバージョンのFirefox (3.x系) で `n:submitLink` のダブルクリック時にまれに2回リクエストが送信される事象がある。Firefox 9.01以降へのアップデートで解消。ただし、サーバ側トークンチェックと併用していれば業務処理の2重実行は防止されます。
4. **確認画面後のバリデーション**: 確認画面を経由して登録処理メソッドが呼ばれる場合でも、入力データはhiddenタグ経由で渡されるため**改竄の可能性があります**。毎回 `validate()` でバリデーションを行ってください。

---

参照: `component/libraries/libraries-07_SubmitTag.json#s1`, `component/libraries/libraries-07_SubmitTag.json#s2`, `guide/web-application/web-application-07_insert.json#s3`, `guide/web-application/web-application-07_insert.json#s4`, `guide/web-application/web-application-07_insert.json#s5`, `guide/web-application/web-application-07_insert.json#s8`, `processing-pattern/web-application/web-application-14.json#s1`