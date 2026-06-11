**結論**: リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、引数にフォームクラスを受け取る形で定義する。`BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録後、`HttpResponse.Status.CREATED (201)` を返すのが基本パターン。

**根拠**:

**1. フォームクラスの作成**

クライアントから送信されたJSONを受け付けるフォームを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラスの実装**

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

各アノテーション・メソッドの役割:

| 要素 | 役割 |
|---|---|
| `@Path("/projects")` | クラスにURLパスを紐付ける |
| `@POST` | POSTリクエストにメソッドを紐付ける |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして受け付けることを宣言する。`BodyConvertHandler` がこの指定を元にフォームへの変換処理を行う |
| `@Valid` | `JaxRsBeanValidationHandler` がフォームに対してバリデーションを実行する |
| `BeanUtil.createAndCopy(Project.class, project)` | フォームをエンティティクラスに変換する |
| `UniversalDao.insert(...)` | エンティティをDBに登録する（SQLを書かずにCRUD可能）|
| `HttpResponse.Status.CREATED` | ステータスコード201（リソース作成完了）を返す |

**3. メソッドシグネチャのバリエーション**

| 引数パターン | 用途 |
|---|---|
| `(SampleForm form)` | リクエストボディをフォームに変換して受け取る（今回のパターン） |
| `(JaxRsHttpRequest request)` | パスパラメータやクエリパラメータ、HTTPヘッダを取得したい場合 |
| `(SampleForm form, JaxRsHttpRequest request)` | 上記を組み合わせて使用する場合 |

戻り値に `void` を指定すると204 NoContentを返す。フォームクラスを返すと `BodyConvertHandler` がJSONレスポンスに変換する。

**4. 処理の流れ（ハンドラキュー）**

リクエストは以下の順でハンドラを経由して処理される：

| No. | ハンドラ | 処理 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・エラー処理 |
| 3 | DB接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | URLからアクションメソッドを決定 |
| 6 | BodyConvertHandler | リクエストボディ→フォームの変換 |
| 7 | JaxRsBeanValidationHandler | フォームのバリデーション実行 |

**5. Jersey環境でのJSON変換設定**

Jersey環境では `JerseyJaxRsHandlerListFactory` を使うと、JSONコンバータ（`Jackson2BodyConverter`）が自動設定される。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**注意点**:
- フォームのプロパティは全てString型で宣言すること（バリデーション仕様）
- `@Consumes` に指定したMIMEとリクエストの `Content-Type` が異なる場合、ステータスコード415が返却される
- ルーティングアダプタより後ろに設定するハンドラ（BodyConvertHandler、BeanValidationHandler）は、ハンドラキューに直接ではなくルーティングアダプタに対して設定する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, adapters-jaxrs-adaptor.json:s2, adapters-router-adaptor.json:s8