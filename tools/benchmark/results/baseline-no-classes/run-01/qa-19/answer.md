**結論**: NablarchのRESTful Webサービスで「JSONを受け取ってDBに登録する」には、アクションクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付け、`UniversalDao.insert()` でDB登録する実装が基本パターンです。JSONの変換は `BodyConvertHandler` がフレームワーク側で自動的に行います。

---

**根拠**:

**全体の処理の流れ**

1. HTTPリクエスト受信 → WebFrontController → ハンドラキュー
2. `BodyConvertHandler` がリクエストボディのJSONをFormクラスに変換（`@Consumes` を元に判断）
3. `JaxRsBeanValidationHandler` がバリデーションを実行（`@Valid` アノテーションが必要）
4. アクションクラスのメソッドが実行 → `UniversalDao.insert()` でDB登録
5. `JaxRsResponseHandler` がレスポンスをクライアントへ返却

**Formクラス（リクエスト受付）の作成**

```java
public class ProjectForm implements Serializable {
    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> ポイント: Formのプロパティは全て `String` 型で宣言する。

**アクションクラスのメソッド実装**

```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

> ポイント:
> - `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言する
> - `@Valid` を付けることでBean Validationハンドラがバリデーションを実行する
> - `BeanUtil.createAndCopy()` でFormをEntityに変換してから `UniversalDao.insert()` で登録する
> - 戻り値は `HttpResponse.Status.CREATED`（ステータスコード `201`）を返す

**ハンドラ構成（最小構成）**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションのマッピング |
| 6 | **BodyConvertHandler** | JSON → Formクラスへの変換 |
| 7 | **JaxRsBeanValidationHandler** | バリデーション実行 |

> `BodyConvertHandler` と `JaxRsBeanValidationHandler` は `ルーティングアダプタ` の後ろ（子ハンドラキュー）に設定する。`Jakarta RESTful Web Servicesアダプタ` を使用すると、これらが自動的に追加される。

---

**注意点**:
- `BodyConvertHandler` の `bodyConverters` プロパティに `application/json` に対応したコンバータが設定されていないと、ステータスコード `415`（Unsupported Media Type）が返る
- `UniversalDao.insert()` はJakarta Persistenceアノテーション（`@Table`、`@Id`、`@Column` など）を付けたEntityクラスが必要。設定として `BasicDaoContextFactory` をコンポーネント定義に追加しておく必要がある
- Formのプロパティは全て `String` 型で宣言すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6