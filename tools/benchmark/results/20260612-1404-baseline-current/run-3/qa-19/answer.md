**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドを作成し、`UniversalDao.insert()` でDBに登録する。JSON→Form変換はハンドラキュー内の `BodyConvertHandler` が自動で行う。

**根拠**:

処理の流れは以下のとおり。

```
クライアント
  → WebFrontController
  → ハンドラキュー（各種ハンドラ）
  → BodyConvertHandler    ← JSONボディをFormに変換
  → JaxRsBeanValidationHandler  ← @Validが付いていればバリデーション実行
  → アクションクラス      ← 業務処理（DB登録など）
```

**1. フォームの作成**

リクエストのJSON項目に対応するFormを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、`BodyConvertHandler` がリクエストボディをJSONとして解釈してFormに変換する
- `@Valid` を指定することで、`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する（バリデーションエラー時はApplicationExceptionをスローし後続処理には進まない）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録する
- 戻り値はリソース作成完了を示すステータスコード `201` の `HttpResponse` を返す

**3. ハンドラキューの最小構成**（参考）

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込みとエラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | リクエストボディ変換ハンドラ | JSON→Formの変換 |
| 7 | Bean Validationハンドラ | @Valid によるバリデーション実行 |

**注意点**:
- `BodyConvertHandler` は `ルーティングアダプタ` よりも後ろに設定する必要がある（アクションのアノテーション情報が必要なため）
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` よりも後ろに設定する必要がある（変換後のFormに対してバリデーションを行うため）
- フォームのプロパティは全てString型で宣言すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4