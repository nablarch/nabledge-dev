**結論**: Nablarch 5 で二重サブミット防止を実装するには、**クライアント側**（JavaScriptによるボタン無効化）と**サーバ側**（トークンによる重複リクエスト検出）を両方組み合わせる。

**根拠**:

### クライアント側の防止

`n:submit` / `n:button` / `n:submitLink` などのカスタムタグの `allowDoubleSubmission` 属性に `false` を指定する。1回目のサブミット時にJavaScriptでボタンをdisabled化し、2回目以降のリクエストをブロックする。

```jsp
<n:button uri="/action/client/create"
          allowDoubleSubmission="false"
          cssClass="btn btn-raised btn-success">確定</n:button>
```

### サーバ側の防止

#### 1. JSPのformタグでトークンを設定する

`n:form` タグの `useToken` 属性を `true` に指定する（確認画面ではデフォルトが `true` のため省略可）。

```jsp
<n:form useToken="true">
    <n:forConfirmationPage>
        <n:submit value="確定" uri="/action/project/update"
                  allowDoubleSubmission="false" type="button" />
    </n:forConfirmationPage>
</n:form>
```

#### 2. アクションメソッドに `@OnDoubleSubmission` を付与する

トークンをチェックするインターセプタを有効化する。`path` 属性で二重サブミット検出時の遷移先を指定する。

```java
@OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")
public HttpResponse create(HttpRequest request, ExecutionContext context) {
    Client client = SessionUtil.get(context, "client");
    UniversalDao.insert(client);
    SessionUtil.delete(context, "client");
    return new HttpResponse(303, "redirect://complete");
}
```

`path` を省略する場合は、アプリ全体のデフォルト設定として `BasicDoubleSubmissionHandler` をコンポーネント定義に追加する。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
  <property name="path" value="/WEB-INF/view/error/userError.jsp" />
  <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
  <property name="statusCode" value="200" />
</component>
```

#### 3. JSP以外のテンプレートエンジンを使用する場合

`@UseToken` インターセプタをトークン発行側のアクションに付与し、テンプレートでトークンをhiddenに明示的に埋め込む。チェック側のアクションには `@OnDoubleSubmission` を付与する。

**注意点**:
- クライアント側のみ使用した場合: リクエストが重複処理される恐れあり
- サーバ側のみ使用した場合: ダブルクリック時の処理順によってはユーザに処理結果が返らない恐れあり。**両方の併用を推奨する**
- トークンはセッションに格納されるため、同一ユーザが複数ウィンドウ/タブで並行して同一フローを操作すると、後に確認画面に遷移した画面のみ処理継続できる（先の画面はトークン不一致でエラー）
- `@OnDoubleSubmission` と `BasicDoubleSubmissionHandler` のどちらも `path` 未指定の場合、遷移先が不明となりシステムエラーになる。必ずどちらかで `path` を設定すること

参照: `component/handlers/handlers-on_double_submission.json#s1`, `#s3`, `#s4` / `component/handlers/handlers-use_token.json#s1` / `component/libraries/libraries-tag.json#s1` / `processing-pattern/web-application/web-application-client_create4.json#s1` / `processing-pattern/web-application/web-application-getting-started-project-update.json#s2`