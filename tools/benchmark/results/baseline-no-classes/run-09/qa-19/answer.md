**結論**: NablarchのRESTfulウェブサービスでJSONを受け取りDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付けたアクションメソッドを実装し、`UniversalDao.insert()` でDBに登録する。JSONのパースはフレームワーク（`BodyConvertHandler`）が自動的に担う。

**根拠**:

### 処理の流れ

リクエストがDB登録に至るまでの仕組みは以下のとおり。

1. **WebFrontController**（Servletフィルタ）がPOSTリクエストを受信し、ハンドラキューに委譲する
2. **ルーティングアダプタ**（`RoutesMapping`）がURIをもとにアクションクラス・メソッドを決定する
3. **リクエストボディ変換ハンドラ**（`BodyConvertHandler`）がリクエストボディのJSONをフォームクラスに変換する
4. **Bean Validationハンドラ**（`JaxRsBeanValidationHandler`）がフォームクラスをバリデーションする
5. **アクションクラス**のメソッドが実行され、`UniversalDao.insert()` でDBに登録する
6. **JaxRsResponseHandler** がレスポンスをクライアントに返す

### 最小ハンドラ構成

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | URI → アクションメソッドの決定 |
| 6 | BodyConvertHandler | JSONボディ → Formクラス変換 |
| 7 | JaxRsBeanValidationHandler | フォームのバリデーション実行 |

### 実装例

**フォームクラス**（JSONのプロパティを受け取る）

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全てString型で宣言する

**アクションクラス**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、`BodyConvertHandler` がJSONをフォームクラスに変換する対象と認識する
- `@Valid` を指定することで、`JaxRsBeanValidationHandler` がバリデーションを実行する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値は作成完了を示すステータスコード `201` の `HttpResponse`
- `@Path` と `@POST` でURLとHTTPメソッドのマッピングを定義する

### BodyConvertHandlerの設定（JSON対応）

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/json に対応したコンバータ（Jakarta RESTful Web Servicesアダプタが提供） -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
    </list>
  </property>
</component>
```

- `bodyConverters` プロパティに対応MIMEの `BodyConverter` 実装を設定する
- Content-TypeがConsumesに設定したMIMEと異なる場合、ステータスコード `415` が返る

**注意点**:
- `BodyConvertHandler` は**ルーティングアダプタより後ろ**に配置する（アクションのアノテーション情報が必要なため）
- Jakarta RESTful Web Servicesアダプタ（Jersey等）を使用した場合、`BodyConvertHandler` と `JaxRsBeanValidationHandler` は自動的に追加される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5