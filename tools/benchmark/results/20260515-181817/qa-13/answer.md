**結論**: フォームデータをDBに登録するには、Jakarta PersistenceアノテーションをEntityに付与し、`UniversalDao.insert()` を呼び出します。二重サブミット防止のため `@OnDoubleSubmission` を付与し、完了後はリダイレクトします。

**根拠**:

### 1. 登録フローの構成

顧客登録機能を例にとると、以下のURL/アクションマッピングで構成されます。

| NO. | 処理名 | URL | Action | HTTPメソッド |
|---|---|---|---|---|
| 1 | 初期表示 | /action/client/ | ClientAction#input | GET |
| 2 | 登録内容の確認 | /action/client/confirm | ClientAction#confirm | POST |
| 3 | 登録画面に戻る | /action/client/back | ClientAction#back | POST |
| 4 | 登録処理の実行 | /action/client/create | ClientAction#create | POST |

### 2. DB登録を行う業務アクションメソッド（更新処理と同パターン）

```java
@OnDoubleSubmission
public HttpResponse create(HttpRequest request, ExecutionContext context) {
    Client client = SessionUtil.delete(context, "client");
    UniversalDao.insert(client);
    return new HttpResponse(303, "redirect://completeOfCreate");
}
```

実装のポイント:
- `UniversalDao.insert(entity)` を使うことで、SQLを書かずにDB登録が可能
- `@OnDoubleSubmission` で二重サブミットを防止する
- 処理後はリダイレクト（303）でブラウザのリロード再実行を防ぐ

### 3. Entityの定義（Jakarta Persistenceアノテーション）

```java
@Entity
@Table(name = "CLIENT")
public class Client {

    private Long clientId;
    private String clientName;

    @Id
    @Column(name = "CLIENT_ID")
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "seq")
    @SequenceGenerator(name = "seq", sequenceName = "CLIENT_ID_SEQ")
    public Long getClientId() {
        return clientId;
    }
}
```

### 4. サロゲートキーの採番方式

| ストラテジ | アノテーション | 説明 |
|---|---|---|
| AUTO | @GeneratedValue(strategy = AUTO) | DBのDialect設定に従い自動選択 |
| IDENTITY | @GeneratedValue(strategy = IDENTITY) | IDENTITY列を使用 |
| SEQUENCE | @GeneratedValue(strategy = SEQUENCE) + @SequenceGenerator | シーケンスオブジェクトを使用 |
| TABLE | @GeneratedValue(strategy = TABLE) + @TableGenerator | 採番用テーブルを使用 |

### 5. 複数件の一括登録

```java
UniversalDao.batchInsert(clientList);
```

### 6. 必要な設定

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `@Table` アノテーションでスキーマを指定できるが、「環境毎にスキーマを切り替える」機能はユニバーサルDAOでは使用できない。スキーマ切り替えが必要な場合はデータベースアクセス（JDBCラッパー）を使用すること
- `batchInsert` はパフォーマンス向上に有効だが、`batchUpdate` では排他制御が行われないため注意（バージョン不一致の場合、更新されずに正常終了する）

参照: component/libraries/libraries-universal-dao.json#s2, component/libraries/libraries-universal-dao.json#s6, component/libraries/libraries-universal-dao.json#s13, component/libraries/libraries-universal-dao.json#s14, processing-pattern/web-application/web-application-getting-started-client-create.json#s1, processing-pattern/web-application/web-application-getting-started-project-update.json#s2