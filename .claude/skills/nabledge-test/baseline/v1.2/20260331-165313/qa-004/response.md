**結論**: 二重サブミット防止には「JavaScript方式」と「トークン方式」の2種類があります。DBの登録・更新処理では、サーバ側で確実に防止できる**トークン方式**を使用することが推奨されます。

---

**根拠**:

## JavaScript方式

ユーザのボタン連打をクライアント側で防止する方式です。`n:submit`タグの`allowDoubleSubmission`属性に`false`を指定します。

```jsp
<n:submit cssClass="buttons" type="button" name="register" value="登録"
          uri="./USERS00302" allowDoubleSubmission="false" />
```

**仕組み**: 1回目のサブミット時に対象要素のonclick属性を書き換え、2回目以降はサーバに送信しません。ボタンの場合はdisabled属性も設定されます。

> **注意**: 1回目のサブミット後にユーザがブラウザの中止ボタンを押した場合、ボタンがdisabled状態のままになります。

---

## トークン方式

サーバ側でトークンを突合することで二重サブミットを防止する方式です。JSP側とAction側の両方に実装が必要です。

### JSP側: `n:form`タグに`useToken="true"`を設定

```jsp
<n:form useToken="true">
    ...
</n:form>
```

| 入力・確認画面の共通化 | useToken設定 | アノテーション付与 |
|---|---|---|
| 共有化している | 設定不要（自動でトークン設定） | 必要 |
| 共有化していない | `true`を設定 | 必要 |

### Action側: `@OnDoubleSubmission`アノテーションを付与

```java
@OnError(type = ApplicationException.class, path = "forward://RW11AC0201")
@OnDoubleSubmission(
    path = "forward://RW11AC0201"  // 二重サブミット判定時の遷移先
)
public HttpResponse doRW11AC0204(HttpRequest req, ExecutionContext ctx) {
    // 確認画面からのデータは改竄の恐れがあるため、毎回バリデーションを実施
    W11AC02Form form = validate(req);
    // ...
    return new HttpResponse("/ss11AC/W11AC0203.jsp");
}
```

`@OnDoubleSubmission`の主な属性:

| 属性 | 説明 | デフォルト値 |
|---|---|---|
| `path` | 二重サブミット判定時の遷移先リソースパス | (必須指定推奨) |
| `messageId` | 二重サブミット判定時のエラーメッセージID | |
| `statusCode` | 二重サブミット判定時のレスポンスステータス | 400 (Bad Request) |

### アプリケーション全体のデフォルト設定

`BasicDoubleSubmissionHandler`をリポジトリに登録することで、全体のデフォルト値を設定できます。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
    <property name="messageId" value="MSG00022" />
    <property name="statusCode" value="200" />
</component>
```

---

**注意点**:

1. **pathの指定は必須**: `@OnDoubleSubmission`アノテーションと`BasicDoubleSubmissionHandler`の両方で`path`が未指定の場合、二重サブミット判定時に遷移先不明となりシステムエラーが発生します。必ずどちらか一方で`path`属性を指定してください。

2. **確認画面からのデータは再バリデーション必須**: 入力データはhiddenタグでクライアント側に保持されるため、確認画面から遷移した場合でも改竄される恐れがあります。登録確定メソッドでは毎回`validate()`を呼び出してください。

3. **複数ウィンドウの並行操作**: 同じ業務を複数ウィンドウで並行操作した場合、後に確認画面に遷移したウィンドウのみ処理継続可能です。先に確認画面に遷移したウィンドウはトークンが古くなり二重サブミットと判定されます。

4. **トークン発行処理のカスタマイズ**: `TokenGenerator`インタフェースを実装し、リポジトリに`"tokenGenerator"`という名前で登録することで変更可能です（デフォルト: `RandomTokenGenerator`、16文字のランダム文字列）。

参照:
- `guide/web-application/web-application-07_insert.json#s5`
- `guide/web-application/web-application-07_insert.json#s4`
- `guide/web-application/web-application-07_insert.json#s3`
- `guide/web-application/web-application-07_insert.json#s8`
- `component/libraries/libraries-07_SubmitTag.json#s1`
- `component/libraries/libraries-07_SubmitTag.json#s2`

###