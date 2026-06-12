**結論**: NablarchのRESTfulウェブサービスでJSONを受け取りDBに登録するには、アクションクラスに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付与したメソッドを実装し、`UniversalDao.insert()`でDB登録する。リクエストボディのJSON→Form変換はフレームワークの`BodyConvertHandler`が自動で行う。

**根拠**:

### 処理の流れ（仕組み）

リクエストを受信してDBに登録されるまでの流れは以下の通り：

1. WebFrontController（`jakarta.servlet.Filter`の実装）がリクエストを受信
2. ハンドラキューに処理を委譲
3. ディスパッチハンドラがURIを元にアクションクラスを特定
4. **BodyConvertHandler**（リクエストボディ変換ハンドラ）がリクエストのJSONボディをFormクラスに変換
5. **JaxRsBeanValidationHandler**がFormに対してBean Validationを実行
6. アクションクラスが業務ロジック（DB登録）を実行
7. JaxRsResponseHandlerがHttpResponseをクライアントへ返却

### 最小ハンドラ構成（ポイント）

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み・エラー処理 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションのマッピング |
| 6 | **リクエストボディ変換ハンドラ** | JSONボディ→Formクラスへの変換 |
| 7 | **Jakarta RESTful Web Servcies Bean Validationハンドラ** | Formのバリデーション実行 |

### アクションクラスの実装例

```java
@Path("/projects")
public class ProjectAction {

  @POST
  @Consumes(MediaType.APPLICATION_JSON)  // JSONで受け取ることを宣言
  @Valid                                  // バリデーション実行を指定
  public HttpResponse save(ProjectForm project) {
    // BeanUtilでFormをEntityに変換し、UniversalDaoでDB登録
    UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
    // ステータスコード201(Created)を返却
    return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
  }
}
```

### Formクラスの実装例

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言

    // ゲッタ及びセッタ
}
```

**注意点**:
- Formクラスのプロパティは全て`String`型で宣言する
- `@Consumes`に設定したMIMEとリクエストのContent-Typeが異なる場合、ステータスコード`415`が返却される
- `BodyConvertHandler`は`ルーティングアダプタ`より後ろに設定する必要がある（ディスパッチ先が確定してからでないとアクションのアノテーションを読めないため）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4