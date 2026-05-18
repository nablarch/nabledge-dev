**結論**: Nablarch WebアプリケーションでフォームからのデータをDBに登録する処理は、「入力画面 → 確認画面 → 登録完了画面」の3画面構成で実装し、`UniversalDao.insert()` でDB登録を行うのが標準パターンです。

**根拠**:

### 1. フォームクラスの作成

入力値を受け取るフォームクラスを作成する。全プロパティはString型で宣言し、`Serializable` を実装する。

```java
public class ClientForm implements Serializable {
    @Required
    @Domain("clientName")
    private String clientName;

    @Required(message = "{nablarch.core.validation.ee.Required.select.message}")
    @Domain("industryCode")
    private String industryCode;

    // getter、setter必須
}
```

### 2. 確認画面への遷移（バリデーション + セッション保存）

```java
@InjectForm(form = ClientForm.class, prefix = "form")
@OnError(type = ApplicationException.class, path = "forward://input")
public HttpResponse confirm(HttpRequest request, ExecutionContext context) {
    ClientForm form = context.getRequestScopedVar("form");

    // FormをEntityに変換してセッションストアに保存
    Client client = BeanUtil.createAndCopy(Client.class, form);
    SessionUtil.put(context, "client", client);

    return new HttpResponse("/WEB-INF/view/client/confirm.jsp");
}
```

### 3. DB登録処理（二重サブミット防止付き）

```java
@OnDoubleSubmission  // 二重サブミット防止
public HttpResponse create(HttpRequest request, ExecutionContext context) {
    Client client = SessionUtil.get(context, "client");

    UniversalDao.insert(client);  // DB登録

    SessionUtil.delete(context, "client");  // セッションから削除

    return new HttpResponse(303, "redirect://complete");  // PRGパターン
}
```

### 4. Entityクラス（Jakarta Persistenceアノテーション）

```java
@Entity
@Table(name = "CLIENT")
public class Client {
    @Id
    @Column(name = "CLIENT_ID")
    private Long clientId;

    @Column(name = "CLIENT_NAME")
    private String clientName;

    // getter、setter必須
}
```

### 5. URLマッピング（routes.xml）

```xml
<routes>
  <get  path="/action/client"         to="Client#input"/>
  <post path="/action/client/confirm" to="Client#confirm"/>
  <post path="/action/client/back"    to="Client#back"/>
  <post path="/action/client/create"  to="Client#create"/>
</routes>
```

**注意点**:
- **フォームはセッションに格納しない**: `@InjectForm` で使うフォームクラスをセッションに直接保存するのではなく、`BeanUtil.createAndCopy()` でEntityに変換してから保存する
- **二重サブミット防止は2箇所必須**: 業務アクションの `@OnDoubleSubmission`（サーバーサイド）と、JSPの `allowDoubleSubmission="false"`（クライアントサイド）の両方が必要
- **登録完了後はリダイレクト（PRGパターン）**: `redirect://complete` でリダイレクトし、ブラウザのリロードによる多重登録を防ぐ
- **セッションのクリーンアップ**: 初期表示メソッドで既存のセッションデータを `SessionUtil.delete()` で削除する（直接ブックマーク遷移等に備えて）
- **共通項目の自動設定は非サポート**: `UniversalDao` は登録ユーザ・更新日時等の共通項目への自動設定を提供しない。Domaアダプタのエンティティリスナーを使うか、アプリケーション側で明示的に設定する

参照: `processing-pattern/web-application/web-application-client-create2.json`, `processing-pattern/web-application/web-application-client-create4.json`, `component/libraries/libraries-universal-dao.json#s2`