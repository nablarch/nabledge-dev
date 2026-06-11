**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`BodyConvertHandler`がJSONをFormクラスに自動変換し、`@Valid`バリデーション後、アクションクラスで`UniversalDao.insert()`を呼ぶ構造になっている。

**根拠**:

**処理の流れ**

1. Webフロントコントローラがリクエストをハンドラキューへ委譲
2. `BodyConvertHandler` が `@Consumes(MediaType.APPLICATION_JSON)` を見てJSONリクエストボディをFormクラスに変換（Jackson2BodyConverterを使用）
3. `JaxRsBeanValidationHandler` がFormに対してBean Validationを実行（`@Valid`指定時）
4. アクションクラスの業務ロジックが実行される
5. `JaxRsResponseHandler`（JaxRsレスポンスハンドラ）がレスポンスをクライアントへ返す

**実装例**

Formクラス:
```java
public class ProjectForm implements Serializable {
    // プロパティは全てString型で宣言する
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

アクションクラス:
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

**最小ハンドラ構成**（ハンドラキューに設定が必要）

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsレスポンスハンドラ | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | ルーティングアダプタ | URL→アクションのマッピング |
| 6 | BodyConvertHandler | JSONボディ↔Formの変換 |
| 7 | JaxRsBeanValidationHandler | Formのバリデーション実行 |

**注意点**:
- `@Consumes`に指定したMIMEと異なるContent-Typeがリクエストされた場合、ステータスコード`415`が返る
- Jersey/RESTEasyアダプタ（`JerseyJaxRsHandlerListFactory`等）を使うと、`BodyConvertHandler`と`JaxRsBeanValidationHandler`が自動的にハンドラキューに追加される
- JSON変換には`Jackson2BodyConverter`が内部で使用される

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-jaxrs-adaptor.json:s2, component/adapters/adapters-router-adaptor.json:s8