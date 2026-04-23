**結論**: Nablarch には二重サブミット防止の仕組みが標準で備わっている。「クライアント側（JavaScript）」と「サーバ側（トークン）」の2層で制御でき、どちらか一方、または両方を組み合わせて使用する。

---

**根拠**:

### 1. サーバ側制御（トークンによる二重サブミット防止）

業務アクションメソッドに `@OnDoubleSubmission` アノテーションを付与する。フォームタグに `useToken="true"` を指定すると、サブミット時にトークンが発行・検証され、同じリクエストが2回来た場合はエラーページへ遷移する。
（`processing-pattern/web-application/web-application-getting-started-project-update.json:s2`）

```java
@OnDoubleSubmission
public HttpResponse update(HttpRequest request, ExecutionContext context) {
    // 二重サブミット時はエラーページへ遷移する
}
```

```jsp
<n:form useToken="true">
    <n:submit value="確定" uri="/action/project/update"
              allowDoubleSubmission="false" type="button" />
</n:form>
```

遷移先は `@OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")` のように属性で指定できる。アプリケーション全体のデフォルト遷移先は `BasicDoubleSubmissionHandler` をコンポーネント定義に追加することで設定できる。
（`component/handlers/handlers-on_double_submission.json:s3`、`component/handlers/handlers-on_double_submission.json:s4`）

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
  <property name="path" value="/WEB-INF/view/error/userError.jsp" />
  <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
  <property name="statusCode" value="400" />
</component>
```

### 2. クライアント側制御（JavaScript によるボタン無効化）

`<n:submit>` や `<n:button>` タグの `allowDoubleSubmission="false"` を指定すると、初回クリック後にボタンが無効化される JavaScript が自動で付加される。
（`component/libraries/libraries-tag_reference.json:s6`、`processing-pattern/web-application/web-application-client_create4.json:s1`）

```jsp
<n:button uri="/action/client/create"
          allowDoubleSubmission="false"
          cssClass="btn btn-lg btn-success">確定</n:button>
```

2回目以降のクリック時に独自処理を実行したい場合は、JavaScript で `nablarch_handleDoubleSubmission(element)` 関数を実装する。
（`component/libraries/libraries-tag.json:s2`）

---

**注意点**:
- `@OnDoubleSubmission` と `BasicDoubleSubmissionHandler` の**両方**で `path` が未指定の場合、二重サブミット判定時に遷移先不明でシステムエラーとなるため、必ずどちらかに `path` を指定すること（`component/handlers/handlers-on_double_submission.json:s4`）。
- クライアント側（JavaScript）制御だけでは、JavaScript を無効にしたブラウザからの二重送信を防げない。確実に防ぐにはサーバ側の `@OnDoubleSubmission` と `useToken="true"` を組み合わせること。
- サーバ側トークンはデフォルトで HTTP セッションに保存される。アプリケーションサーバをスケールアウトする場合は、スティッキーセッション・セッションレプリケーション、またはトークンをデータベースに保管する実装（`db_double_submit`）の利用を検討すること（`component/libraries/libraries-tag.json:s2`）。

参照: component/handlers/handlers-on_double_submission.json:s3, component/handlers/handlers-on_double_submission.json:s4, processing-pattern/web-application/web-application-getting-started-project-update.json:s2, processing-pattern/web-application/web-application-client_create4.json:s1, component/libraries/libraries-tag_reference.json:s6, component/libraries/libraries-tag.json:s2