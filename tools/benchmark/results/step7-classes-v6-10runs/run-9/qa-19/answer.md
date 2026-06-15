**結論**: RESTful APIでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`BeanUtil.createAndCopy()` でFormをEntityに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**① フォームクラスの作成**

受け取るJSONのフィールドに対応するフォームを作成する。プロパティは全てString型で宣言し、Bean Validationアノテーションでバリデーションルールを定義する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② アクションメソッドの実装**

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

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` を付与することで、リクエストボディ変換ハンドラ（`BodyConvertHandler`）がリクエストボディをJSONとして `ProjectForm` に変換する
- `@Valid` を付与することで、JaxRsBeanValidationHandlerによりBean Validationが実行される
- `BeanUtil.createAndCopy()` でFormオブジェクトをEntityクラスにコピーする
- `UniversalDao.insert()` でDBに登録する
- レスポンスとして、リソース作成完了を示すステータスコード `201` を返却する

**③ ハンドラ構成（最小構成）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外・エラーのログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIをもとにアクションを決定 |
| 6 | リクエストボディ変換ハンドラ | JSONをFormクラスに変換 |
| 7 | JaxRsBeanValidationHandler | Formクラスのバリデーション実行 |

**注意点**:
- `BodyConvertHandler` のJSONコンバータには `Jackson2BodyConverter` を設定する必要がある。Jersey/RESTEasyアダプタ（`JerseyJaxRsHandlerListFactory` / `ResteasyJaxRsHandlerListFactory`）を使用すると自動的に設定される。
- フォームのプロパティは全てString型で宣言すること（Bean Validationの型変換ルールによる）。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2