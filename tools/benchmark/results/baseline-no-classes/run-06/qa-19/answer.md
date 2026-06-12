**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションクラスに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてフォームクラスを引数に受け取り、`BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDB登録する。

---

**根拠**:

### 処理の流れ（全体像）

1. `WebFrontController`（Servletフィルタ）がリクエストを受信
2. ハンドラキューに処理を委譲。ディスパッチハンドラ（DispatchHandler）がURIからアクションクラスを特定
3. **BodyConvertHandler** がリクエストボディ（JSON）をフォームクラスに変換
4. **JaxRsBeanValidationHandler** が `@Valid` の指示に従ってフォームをバリデーション
5. **アクションクラス**が業務ロジックを実行（フォーム → エンティティ → DB登録）
6. **JaxRsResponseHandler** が `HttpResponse` をクライアントへ返却

### 最小ハンドラ構成

| No. | ハンドラ | 主な役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外時のログ出力 |
| 2 | JaxRsResponseハンドラ | レスポンス書き込み・エラー応答 |
| 3 | DB接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | ルーティングアダプタ | URLとアクションの紐付け |
| 6 | BodyConvertHandler | JSONリクエスト → Formへの変換 |
| 7 | JaxRsBeanValidationHandler | `@Valid` によるバリデーション実行 |

### 各クラスの責務

- **アクションクラス**: フォームからエンティティを作成してDBに登録し、レスポンスを返す
- **フォームクラス**: JSONリクエストボディをマッピングするクラス。バリデーションアノテーションを持つ
- **エンティティクラス**: テーブルと1対1で対応するクラス

### 実装例

**フォームクラス**（リクエストボディのマッピング）:

```java
public class ProjectForm implements Serializable {

    // 一部のみ抜粋

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**アクションクラス**（URLマッピング＋登録処理）:

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

実装のポイント:
- `@Path("/projects")` と `@POST` でPOSTリクエストをこのメソッドにマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、BodyConvertHandlerがJSONをフォームに変換する
- `@Valid` を付けることで、JaxRsBeanValidationHandlerがフォームのバリデーションを実行する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値はリソース作成完了を示すステータスコード `201` の `HttpResponse`

---

**注意点**:

- フォームクラスのプロパティは **全てString型** で定義すること（Bean Validationの仕様上の要件）
- リクエストヘッダの `Content-Type` が `@Consumes` に指定したMIMEと異なる場合、BodyConvertHandlerがステータスコード `415` を返す

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-application-design.json, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4