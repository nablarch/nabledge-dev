**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラスを作成し、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`BeanUtil` でエンティティに変換した後 `UniversalDao.insert` でDBに登録します。

**根拠**:

#### 処理の流れ（仕組み）

1. WebフロントコントローラがHTTPリクエストを受信し、ハンドラキューに委譲
2. **リクエストボディ変換ハンドラ**（`BodyConvertHandler`）が、アクションメソッドの `@Consumes` アノテーションに応じてJSONをフォームクラスに変換
3. **Bean Validationハンドラ**（`JaxRsBeanValidationHandler`）がフォームに対してバリデーションを実行（`@Valid` が必要）
4. アクションメソッドが実行され、`BeanUtil` でフォーム → エンティティへ変換し `UniversalDao.insert` でDB登録
5. `HttpResponse` を返却

#### 実装例（フォームクラス）

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言すること
    // ゲッタ及びセッタは省略
}
```

#### 実装例（アクションクラス）

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

#### ハンドラキューの最小構成（設定）

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを決定 |
| 6 | BodyConvertHandler | JSONをFormに変換 |
| 7 | JaxRsBeanValidationHandler | バリデーション実行 |

#### ユニバーサルDAOのコンポーネント設定

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームのプロパティは**全てString型**で宣言すること
- `BodyConvertHandler` には JSON対応のコンバータ（`Jackson2BodyConverter` など）を設定する必要があります
- `@Consumes` に設定したMIMEと異なる `Content-Type` のリクエストが来た場合、ステータスコード `415` が返却されます

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/libraries/libraries-universal-dao.json:s6