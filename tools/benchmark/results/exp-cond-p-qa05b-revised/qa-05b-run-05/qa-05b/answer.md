**結論**: JSONリクエストボディをDBに登録するには、`BodyConvertHandler`がリクエストのJSONをFormクラスに自動変換し、アクションメソッドで`BeanUtil.createAndCopy()`でEntityに変換後、`UniversalDao.insert()`でDBに登録する仕組みになっている。

---

**根拠**:

#### 処理の流れ（仕組み）

リクエスト受信からDB登録まで、ハンドラキューが以下の順序で処理を行う:

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外時ログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット/ロールバック |
| 5 | ルーティングアダプタ（RoutesMapping） | URI→アクションのマッピング |
| 6 | **BodyConvertHandler** | **JSONボディ→Formクラスへの変換** |
| 7 | **JaxRsBeanValidationHandler** | **Formのバリデーション実行** |

処理の流れ（詳細）:
1. `BodyConvertHandler` がアクションメソッドの `@Consumes` アノテーションを参照し、Content-Typeに対応した `BodyConverter` でリクエストボディのJSONをFormクラスに変換する
2. `JaxRsBeanValidationHandler` が `@Valid` アノテーションの付いたメソッドのFormに対してBean Validationを実行する（エラー時は `ApplicationException` を送出）
3. アクションメソッドが実行され、`BeanUtil.createAndCopy()` でFormをEntityに変換後、`UniversalDao.insert()` でDBに登録する

#### フォームクラスの実装

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

#### アクションクラスの実装

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

**ポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを指定する
- `@Valid` でBean Validationを有効化する
- `BeanUtil.createAndCopy()` でFormからEntityへプロパティをコピーする
- 登録成功時はステータスコード `201`（Created）の `HttpResponse` を返す
- `@Path` と `@POST` でURLとHTTPメソッドのマッピングを定義する

#### BodyConvertHandlerの設定

`BodyConvertHandler` には使用するMIMEに対応した `BodyConverter` を設定する必要がある（application/json対応のコンバータを含む）。Jakarta RESTful Web Servicesアダプタを使用すると、`BodyConvertHandler` と `JaxRsBeanValidationHandler` が自動的にハンドラキューに追加されるため、手動で設定する手間を省ける。

#### ユニバーサルDAOの設定

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**: `Consumes` に設定したMIMEと異なるContent-Typeがリクエストヘッダにあるとステータスコード `415`（Unsupported Media Type）が返却される。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/libraries/libraries-universal-dao.json:s6