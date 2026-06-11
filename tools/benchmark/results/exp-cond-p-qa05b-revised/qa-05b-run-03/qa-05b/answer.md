**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録する処理は、ハンドラキューの「リクエストボディ変換ハンドラ（BodyConvertHandler）→ Bean Validationハンドラ → アクション → ユニバーサルDAO」という流れで実現する。アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、`UniversalDao.insert()`を呼び出すのが基本パターン。

**根拠**:

**処理の流れ（アーキテクチャ）**

1. WebフロントコントローラがPOSTリクエストを受信
2. ハンドラキューに処理を委譲
3. **BodyConvertHandler** がリクエストボディ（JSON）をアクションが受け取るフォームクラスに変換
4. **JaxRsBeanValidationHandler** がフォームに対してBeanValidationを実行（バリデーションエラー時は`ApplicationException`を送出）
5. アクションクラスが業務ロジックを実行してDBに登録
6. **JaxRsResponseHandler** がレスポンスを返却

**最小ハンドラ構成（ハンドラキュー）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み・例外時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | リクエストパスからアクション(メソッド)を決定 |
| 6 | リクエストボディ変換ハンドラ | JSONリクエストボディ→フォームクラスへの変換 |
| 7 | Bean Validationハンドラ | フォームに対するバリデーション実行 |

**アクションクラスの実装例**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、BodyConvertHandlerがJSONとして解釈してフォームクラスに変換する
- `@Valid` を付けることで、JaxRsBeanValidationHandlerがフォームに対してBeanValidationを実行する
- `BeanUtil.createAndCopy()` でフォームクラスをエンティティクラスに変換し、`UniversalDao.insert()` でDBに登録する
- 登録完了後は`HttpResponse.Status.CREATED`（ステータスコード`201`）を返却する

**フォームクラスの作成ルール**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する

    // ゲッタ及びセッタ
}
```

**注意点**: Formクラスのプロパティは全てString型で宣言する必要がある。また、BodyConvertHandlerの`bodyConverters`プロパティに`application/json`に対応したBodyConverterを設定しておく必要がある。

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4