**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けて実装します。フレームワークが `BodyConvertHandler` でJSONをFormクラスに変換し、`JaxRsBeanValidationHandler` がバリデーションを実行した後、アクション内で `UniversalDao.insert()` を呼び出してDBへ登録します。

---

**根拠**:

**全体の処理の流れ**

リクエスト受信からDB登録までの流れは以下のとおりです。

1. `WebFrontController`（`jakarta.servlet.Filter`の実装）がHTTPリクエストを受信する
2. ハンドラキューに委譲し、ルーティングアダプタがURIをもとにアクションクラスを特定する
3. **`BodyConvertHandler`**（往路）: リクエストボディのJSONをアクションの引数のFormクラスに変換する
4. **`JaxRsBeanValidationHandler`**（往路）: 変換されたFormクラスに対してBean Validationを実行する（エラー時は `ApplicationException` をスロー）
5. アクションメソッドの業務ロジックが実行される（DB登録）
6. `JaxRsResponseHandler`（復路）がHttpResponseをクライアントへ返す

**最小ハンドラ構成**（コンポーネント定義に設定が必要）

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションのマッピング |
| 6 | BodyConvertHandler | JSONリクエスト⇔Formクラスの変換 |
| 7 | JaxRsBeanValidationHandler | Formクラスのバリデーション実行 |

**Formクラスの実装**

フォームのプロパティは全て `String` 型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**アクションクラスの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)`: `BodyConvertHandler` がJSON変換に使用するMIMEタイプを指定する
- `@Valid`: `JaxRsBeanValidationHandler` がFormクラスのバリデーションを実行するトリガーになる
- `@Path` + `@POST`: ルーティングアダプタがURLとメソッドのマッピングに使用する
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する（`UniversalDao.insert()` にはEntityを渡す）

**BodyConvertHandlerのJSON対応設定**（コンポーネント定義）

JSONを処理するには `Jackson2BodyConverter` をコンバータとして設定します。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <component class="nablarch.fw.jaxrs.Jackson2BodyConverter" />
    </list>
  </property>
</component>
```

**UniversalDAOの設定**（コンポーネント定義）

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- `BodyConvertHandler` と `JaxRsBeanValidationHandler` はルーティングアダプタより後ろに設定する必要があります。Jakarta RESTful Web Servicesアダプタを使用する場合、これら2つのハンドラは自動的に追加されます
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が不一致の場合、ステータスコード `415` が返却されます

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6