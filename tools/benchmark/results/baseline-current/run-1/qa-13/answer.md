**結論**: フォームから受け取ったデータをDBに登録するパターンは、「入力画面 → 確認画面 → 登録処理」の3段階フローで実装し、`@InjectForm` + `BeanUtil.createAndCopy` + `UniversalDao.insert` を組み合わせる。

**根拠**:

**① フォームクラスの作成**

フォームは `Serializable` を実装し、全プロパティを `String` 型で宣言する。

```java
public class ClientForm implements Serializable {
    @Required
    @Domain("clientName")
    private String clientName;

    @Required(message = "{nablarch.core.validation.ee.Required.select.message}")
    @Domain("industryCode")
    private String industryCode;
    // getter、setter は必須
}
```

**② confirmメソッド（バリデーション + セッション保存）**

```java
@InjectForm(form = ClientForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input")
public HttpResponse confirm(HttpRequest request, ExecutionContext context) {
    ClientForm form = context.getRequestScopedVar("form");

    // フォームをエンティティに変換してセッションストアに保存
    Client client = BeanUtil.createAndCopy(Client.class, form);
    SessionUtil.put(context, "client", client);

    return new HttpResponse("/WEB-INF/view/client/confirm.jsp");
}
```

**③ createメソッド（DBへの登録）**

```java
@OnDoubleSubmission
public HttpResponse create(HttpRequest request, ExecutionContext context) {
    Client client = SessionUtil.get(context, "client");

    UniversalDao.insert(client);

    SessionUtil.delete(context, "client");

    return new HttpResponse(303, "redirect://complete");
}
```

**注意点**:
- **セッションストアにはフォームを格納しない**。`BeanUtil.createAndCopy` でエンティティに変換してから保存すること
- 登録完了後はリダイレクト（ステータスコード 303）で完了画面へ遷移する（PRGパターン、ブラウザ更新による二重登録防止）
- 二重サブミット防止のため、Actionメソッドに `@OnDoubleSubmission` を付与し、JSPの確定ボタンに `allowDoubleSubmission="false"` を設定する
- 入力画面初期表示時に `SessionUtil.delete` でセッション残留データをクリアする
- `UniversalDao` は主キー以外の条件を指定した更新・削除には使えない。その場合はJDBCラッパーを使用する

参照: `processing-pattern/web-application/web-application-client-create2.json` / `processing-pattern/web-application/web-application-client-create4.json` / `component/libraries/libraries-create-example.json#s2` / `component/libraries/libraries-create-example.json#s4` / `component/libraries/libraries-universal-dao.json#s2`