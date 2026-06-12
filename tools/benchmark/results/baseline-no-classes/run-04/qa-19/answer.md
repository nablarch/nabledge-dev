**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたアクションメソッドを実装し、`UniversalDao.insert()` でDBに登録する。

**根拠**: リクエストからDB登録までの処理の流れは以下のとおり。

---

**① リクエスト受信〜アクション呼び出しの流れ**

1. WebFrontController（`jakarta.servlet.Filter`実装）がリクエストを受信
2. ハンドラキューに処理を委譲
3. ルーティングアダプタがURIからアクションクラスを特定
4. **リクエストボディ変換ハンドラ（BodyConvertHandler）** がJSONリクエストボディをFormクラスに変換
5. **Bean Validationハンドラ（JaxRsBeanValidationHandler）** がFormに対してバリデーションを実行
6. アクションクラスのメソッドが呼び出される

---

**② フォームクラスの作成**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する

---

**③ アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、BodyConvertHandlerがJSONボディをFormに変換する
- `@Valid` アノテーションによりBean Validationハンドラがバリデーションを実行（エラー時は `ApplicationException` を送出）
- `BeanUtil.createAndCopy()` でFormをEntityに変換してから `UniversalDao.insert()` でDB登録
- 登録成功後はステータスコード `201`（Created）を返却

---

**④ 最小ハンドラ構成**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・エラー時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを特定 |
| 6 | BodyConvertHandler | JSONリクエストボディ→Formへ変換 |
| 7 | JaxRsBeanValidationHandler | Formのバリデーション実行 |

No.6以降は、ルーティングアダプタの設定内に記述する点に注意。

**注意点**:
- `@Consumes` に指定したMIMEと異なる `Content-Type` のリクエストが来た場合、ステータスコード `415`（Unsupported Media Type）が返却される
- BodyConvertHandlerには使用するMIMEに対応した `BodyConverter` を設定しておく必要がある（JSONの場合はJacksonなどのコンバータ）

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4