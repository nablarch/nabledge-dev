**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けてFormを引数に受け取り、`UniversalDao.insert()` でDBに登録します。リクエストボディからFormへの変換は `BodyConvertHandler`（`BodyConvertHandler` が `JaxbBodyConverter` 等を使って自動変換）が担い、バリデーションは `JaxRsBeanValidationHandler` が実行します。

**根拠**:

**処理の流れ（アーキテクチャ）**

1. Webフロントコントローラがリクエストを受信
2. ハンドラキューに委譲
3. ディスパッチハンドラがURIを元にアクションクラスを特定
4. **BodyConvertHandler** がリクエストボディ（JSON）をFormクラスに変換
5. **JaxRsBeanValidationHandler** がFormに対してBean Validationを実行
6. アクションクラスが業務ロジック（DB登録）を実行
7. JaxRsResponseHandler がレスポンスをクライアントに返却

**Formクラスの実装例**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全てString型で宣言する

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でバリデーションを実行（エラー時は `ApplicationException` が送出され後続処理は行われない）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録
- 戻り値として 201 Created を示す `HttpResponse` を返却する

**BodyConvertHandlerの設定例（コンポーネント定義）**

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/jsonに対応したコンバータを設定する -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
    </list>
  </property>
</component>
```

- `bodyConverters` プロパティに使用するMIMEに対応した `BodyConverter` を設定する
- 設定されていないMIMEが使用された場合、ステータスコード `415`（Unsupported Media Type）を返却する

**最小ハンドラ構成（ハンドラキューの順序）**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・例外時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションのマッピング |
| 6 | BodyConvertHandler | リクエストボディ→Form変換 / レスポンスボディ変換 |
| 7 | JaxRsBeanValidationHandler | Formに対するBean Validation実行 |

**注意点**:

- `BodyConvertHandler` は必ず `ルーティングアダプタ` より後ろに設定すること（アクションクラスのメソッドに設定されたアノテーション情報を元に変換するため）
- `JaxRsBeanValidationHandler` は必ず `BodyConvertHandler` より後ろに設定すること（変換後のFormに対してバリデーションを行うため）
- Jakarta RESTful Web ServicesアダプタはJersey/RESTEasyなどの環境に対応しており、使用する場合は `BodyConvertHandler` と `JaxRsBeanValidationHandler` がハンドラキューに自動追加される

参照: processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4