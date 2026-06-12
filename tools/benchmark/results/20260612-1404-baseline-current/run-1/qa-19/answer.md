**結論**: Nablarchの「Jakarta RESTful Web Servicesサポート」を使い、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてフォームを受け取り、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録します。

---

**根拠**:

### 処理の流れ（仕組み）

リクエストが来ると次の順序で処理されます。

1. `WebFrontController`（Filter）がリクエストを受信し、ハンドラキューに委譲
2. **リクエストボディ変換ハンドラ（BodyConvertHandler）** がJSONボディをFormクラスに変換
3. **Bean Validationハンドラ（JaxRsBeanValidationHandler）** がFormに対してバリデーションを実行
4. アクションクラスがビジネスロジックを実行（DB登録）
5. **JaxRsResponseHandler** がレスポンスをクライアントに返却（トランザクションコミット後）

### 最小ハンドラ構成

| No. | ハンドラ | 役割 |
|-----|----------|------|
| 1 | グローバルエラーハンドラ | 例外時のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラー処理 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを特定 |
| 6 | リクエストボディ変換ハンドラ | JSONボディ → Formに変換 |
| 7 | Bean Validationハンドラ | バリデーション実行 |

### 実装例

**Formクラス**（プロパティは全てString型で宣言）:

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**アクションクラス**:

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

- `@Path("/projects")` + `@POST` でURLとメソッドをマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストボディを受け付けるよう指定（BodyConvertHandlerが変換処理に使用）
- `@Valid` でバリデーションを有効化（バリデーションエラー時は`ApplicationException`がスローされ後続は実行されない）
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換
- `UniversalDao.insert(...)` でDBに登録
- ステータスコード `201`（Created）を返却

### ユニバーサルDAOの設定

```xml
<!-- コンポーネント定義に追加が必要 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- Formクラスのプロパティは全てString型で宣言すること（バリデーション仕様による制約）
- `@Consumes` と異なるContent-Typeのリクエストには、ステータスコード `415`（Unsupported Media Type）が返される
- ルーティングアダプタより後のハンドラ（BodyConvertHandler、Bean Validationハンドラ）は、ハンドラキューに直接設定せず、ルーティングアダプタに対して設定すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6