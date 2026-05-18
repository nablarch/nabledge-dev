**結論**: Nablarch 6のウェブアプリケーションでフォームのデータをDBに登録する場合、「入力画面 → 確認画面 → 登録処理」という3ステップのパターンが標準実装です。`@InjectForm` + `BeanUtil` + `UniversalDao.insert()` の組み合わせが基本です。

**根拠**:

## 実装パターン概要

### 1. フォームクラスの作成
フォームは `Serializable` を実装し、全プロパティを `String` 型で宣言します。

```java
public class ClientForm implements Serializable {
    @Required
    @Domain("clientName")
    private String clientName;

    @Required(message = "{nablarch.core.validation.ee.Required.select.message}")
    @Domain("industryCode")
    private String industryCode;

    // getter, setter 省略
}
```

### 2. 確認画面への遷移（バリデーション + セッション保存）
`@InjectForm` でバリデーションを実行し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換して `SessionUtil` に保存します。

```java
@InjectForm(form = ClientForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input")
public HttpResponse confirm(HttpRequest request, ExecutionContext context) {
    ClientForm form = context.getRequestScopedVar("form");

    // フォーム → エンティティ変換
    Client client = BeanUtil.createAndCopy(Client.class, form);
    // セッションストアに保存（フォームをそのまま保存しないこと）
    SessionUtil.put(context, "client", client);

    EntityList<Industry> industries = UniversalDao.findAll(Industry.class);
    context.setRequestScopedVar("industries", industries);

    return new HttpResponse("/WEB-INF/view/client/confirm.jsp");
}
```

### 3. DB登録処理の実装
セッションからエンティティを取り出して `UniversalDao.insert()` で登録します。登録後はセッションを削除し、リダイレクトで完了画面へ遷移します（多重登録防止）。

```java
@OnDoubleSubmission  // 二重サブミット防止
public HttpResponse create(HttpRequest request, ExecutionContext context) {
    Client client = SessionUtil.get(context, "client");

    UniversalDao.insert(client);  // DB登録

    SessionUtil.delete(context, "client");  // セッションクリーンアップ

    return new HttpResponse(303, "redirect://complete");  // PRGパターン
}
```

### 4. エンティティクラスの定義
エンティティには Jakarta Persistence アノテーションを付与します。

```java
@Entity
@Table(name = "CLIENT")
public class Client {
    @Id
    @Column(name = "CLIENT_ID")
    private Long clientId;

    @Column(name = "CLIENT_NAME")
    private String clientName;

    @Column(name = "INDUSTRY_CODE")
    private String industryCode;

    // getter, setter 省略
}
```

### 5. URLマッピング設定 (routes.xml)
```xml
<routes>
  <get  path="/action/client"         to="Client#input"   />
  <post path="/action/client/confirm" to="Client#confirm" />
  <post path="/action/client/back"    to="Client#back"    />
  <post path="/action/client/create"  to="Client#create"  />
</routes>
```

**注意点**:
- **セッションにフォームを格納しない**: `BeanUtil.createAndCopy()` でエンティティに変換してからセッション保存すること
- **二重サブミット防止**: `@OnDoubleSubmission` をアクションに付与し、JSPの `<n:button>` に `allowDoubleSubmission="false"` を指定すること
- **PRGパターン**: 登録完了後は `redirect://complete` でリダイレクトし、ブラウザリロードによる多重登録を防ぐこと
- **初期表示でセッション削除**: 入力画面の初期表示時に `SessionUtil.delete()` でセッションをクリアすること（ヘッダメニュー経由の直接遷移等を考慮）
- **バリデーションエラー時の戻り先**: `@OnError` で `forward://input` を指定し、業種リストを再取得するため初期表示処理へ内部フォーワードすること
- **UniversalDAO使用前提**: コンポーネント定義に `BasicDaoContextFactory` を `daoContextFactory` という名前で登録しておく必要がある

参照: web-application-getting-started-client-create#s1, web-application-client-create1, web-application-client-create2, web-application-client-create3, web-application-client-create4, libraries-create-example#s2, libraries-create-example#s4, libraries-universal-dao#s2, libraries-bean-util#s2