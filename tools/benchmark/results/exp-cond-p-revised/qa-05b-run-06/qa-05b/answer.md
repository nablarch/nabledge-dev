**結論**: NablarchのRESTfulウェブサービスでは、`BodyConvertHandler`がリクエストのJSONボディをFormクラスに自動変換し、アクションクラスで`BeanUtil.createAndCopy()`を使ってEntityに変換した後、`UniversalDao.insert()`でDBに登録する仕組みになっている。

---

**根拠**:

**処理の流れ**（リクエスト受信からDB登録まで）

1. WebフロントコントローラがHTTPリクエストを受信し、ハンドラキューに処理を委譲する
2. ルーティングアダプタがURIをもとにアクションクラスを特定する
3. **`BodyConvertHandler`（リクエストボディ変換ハンドラ）** がJSONをアクションのFormクラスに変換する
4. **`JaxRsBeanValidationHandler`（Bean Validationハンドラ）** がFormに対してバリデーションを実行する（エラーがあれば`ApplicationException`を送出して終了）
5. アクションクラスが業務ロジックを実行してDB登録し、`HttpResponse`を返す

**最小ハンドラ構成**（登録処理に必要なハンドラキュー）

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外ログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット／ロールバック |
| 5 | ルーティングアダプタ | URI→アクション紐付け |
| 6 | **リクエストボディ変換ハンドラ** | JSONをFormに変換 |
| 7 | **Bean Validationハンドラ** | Formをバリデーション |

**アクションクラスの実装例**（Formを受け取りDBに登録する）

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

- `@Consumes(MediaType.APPLICATION_JSON)`: このアクションがJSONを受け付けることを宣言。`BodyConvertHandler`はこのアノテーションを見てJSONをFormに変換する
- `@Valid`: `JaxRsBeanValidationHandler`にFormのバリデーション実行を指示する
- `BeanUtil.createAndCopy(Project.class, project)`: FormのプロパティをEntityにコピーして変換する
- `UniversalDao.insert(...)`: EntityをDBに登録するSQLを自動生成して実行する
- `HttpResponse.Status.CREATED.getStatusCode()`: リソース作成完了を示すHTTPステータス201を返す

**Formクラスのポイント**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- Formのプロパティは**全てString型**で宣言する（バリデーション仕様による）

**注意点**:
- `BodyConvertHandler`には`bodyConverters`プロパティにJSONコンバータを設定する必要がある。設定されていないMIMEのリクエストはステータスコード`415`が返される
- `JaxRsBeanValidationHandler`は`BodyConvertHandler`より**後ろ**に設定する必要がある（変換済みのFormに対してバリデーションを行うため）
- RESTfulウェブサービスでは`ETag`/`If-Match`を使った楽観的ロックには対応していない。楽観的ロックを行う場合はリクエストボディに直接バージョン番号を含める

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6