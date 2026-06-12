**結論**: RESTfulウェブサービスでJSONを受け取りDBに登録するには、`@POST`と`@Consumes(MediaType.APPLICATION_JSON)`を付けた業務アクションメソッドを作成し、`BodyConvertHandler`がJSONをFormクラスに変換、`UniversalDao.insert()`でDBに登録する流れになる。

---

**根拠**:

## 処理の仕組み（ハンドラキューの流れ）

リクエスト受信からDB登録まで、以下のハンドラが順に動作する：

| 順序 | ハンドラ | 役割 |
|------|--------|------|
| 1 | グローバルエラーハンドラ | 例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み・エラー対応 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションメソッドを特定 |
| 6 | **リクエストボディ変換ハンドラ** | **JSONリクエストをFormクラスに変換** |
| 7 | **Jakarta RESTful Web Services Bean Validationハンドラ** | **Formに対しバリデーション実行** |

`BodyConvertHandler`がアクションメソッドの`@Consumes`アノテーションを見てJSONをFormクラスに変換する。変換後、`JaxRsBeanValidationHandler`がFormをバリデーションする。

## 実装例

**Formクラス（リクエストJSON受け取り用）:**

```java
public class ProjectForm implements Serializable {
    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**業務アクションクラス:**

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

各ポイント：
- `@Path("/projects")` と `@POST` でURLとHTTPメソッドをマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを宣言（`BodyConvertHandler`がこの指定に従ってJSONをFormに変換する）
- `@Valid` でFormに対してBean Validationを実行（バリデーションエラー時はApplicationExceptionが送出される）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録
- 戻り値はリソース作成完了を示すステータスコード`201`のHttpResponse

---

**注意点**:

- **Formのプロパティは全てString型**で宣言すること（バリデーションルールの設定方法の制約）
- `BodyConvertHandler`は**ルーティングアダプタより後ろ**に設定すること（アクション特定後でないと`@Consumes`情報が取得できないため）
- `JaxRsBeanValidationHandler`は**`BodyConvertHandler`より後ろ**に設定すること（変換後のFormをバリデーションするため）
- RESTfulウェブサービスでは**ETagやIf-Matchを使った楽観的ロックは未対応**。楽観的ロックが必要な場合はリクエストボディに直接バージョン番号を含めること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4