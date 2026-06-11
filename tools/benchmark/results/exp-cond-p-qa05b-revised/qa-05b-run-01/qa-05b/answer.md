**結論**: NablarchのRESTfulウェブサービスでJSON受信→DB登録を行うには、アクションクラスのメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、フォームを引数として受け取り、`BeanUtil.createAndCopy()`でエンティティに変換後に`UniversalDao.insert()`でDB登録する。

**根拠**:

**処理の流れ（全体）**

リクエストは以下の経路で処理される。

```
WebFrontController
 → ハンドラキュー（7ハンドラ）
   1. グローバルエラーハンドラ
   2. Jakarta RESTful Web Servicesレスポンスハンドラ（JaxRsResponseHandler）
   3. データベース接続管理ハンドラ（DB接続取得/解放）
   4. トランザクション制御ハンドラ（コミット/ロールバック）
   5. ルーティングアダプタ（URLからアクションを決定）
   6. リクエストボディ変換ハンドラ（BodyConvertHandler）← JSONをFormに変換
   7. Bean Validationハンドラ（JaxRsBeanValidationHandler）← @Validで検証
 → アクションクラス（業務ロジック）
```

ポイントは**No.6のBodyConvertHandler**が、アクションメソッドの`@Consumes`アノテーションに基づいてJSONリクエストボディをFormクラスに自動変換することである。

**Formクラス（受け口）**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**アクションクラス（業務ロジック）**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストを受け付けることを宣言。BodyConvertHandlerがこれを見てJSONをFormに変換する
- `@Valid`: Bean ValidationハンドラがFormに対してバリデーションを実行する。エラー時は`ApplicationException`が送出され、後続処理は実行されない
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換
- `UniversalDao.insert(...)`: DBにINSERT
- 戻り値としてステータスコード`201`（Created）の`HttpResponse`を返却する

**BodyConvertHandlerの仕組み**

`bodyConverters`プロパティに設定された`BodyConverter`実装クラスが変換を担う。`@Consumes`で指定されたMIMEタイプと一致するコンバータで変換が行われる。未対応のMIMEが来た場合はステータスコード`415`が返却される。

**注意点**:

- Formのプロパティは全てString型で宣言すること（Bean Validationの仕様上の制約）
- BodyConvertHandlerはルーティングアダプタ（No.5）より後ろに設定すること（アクションクラスが確定してから`@Consumes`を読み取るため）
- Bean ValidationハンドラはBodyConvertHandler（No.6）より後ろに設定すること（Formへの変換が先に必要なため）

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4