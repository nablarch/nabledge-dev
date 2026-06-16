**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラスを作成し、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付与し、`BeanUtil.createAndCopy`でエンティティに変換してから`UniversalDao.insert`でDBに登録する。

**根拠**:

**処理の流れ（仕組み）**

リクエスト受信から登録完了までの流れは以下のとおり：

1. WebフロントコントローラがHTTPリクエストを受信し、ハンドラキューに処理を委譲する
2. ルーティングアダプタがURIからアクションクラスを特定する
3. `BodyConvertHandler`（リクエストボディ変換ハンドラ）が、`@Consumes`に指定されたMIMEタイプに対応するコンバータ（JSON場合は`Jackson2BodyConverter`）を使ってリクエストボディをフォームクラスに変換する
4. `JaxRsBeanValidationHandler`がフォームに対してバリデーションを実行する
5. アクションクラスがフォームをエンティティに変換し、`UniversalDao.insert`でDBに登録する
6. `JaxRsResponseHandler`がレスポンスをクライアントに返却する

**最小ハンドラ構成**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・エラー時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを決定 |
| 6 | `BodyConvertHandler` | JSONリクエストボディ→フォームクラスへ変換 |
| 7 | `JaxRsBeanValidationHandler` | フォームのバリデーション実行 |

**実装例**

フォームクラス：
```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
}
```

アクションクラス：
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

**JSON変換の設定（Jersey環境の場合）**

`JerseyJaxRsHandlerListFactory`をファクトリインジェクションすることで、`Jackson2BodyConverter`（JSON変換）が自動的にハンドラキューに設定される：

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
- フォームクラスのプロパティは全て`String`型で宣言する
- `@Consumes`に指定されたMIMEタイプとリクエストのContent-Typeが異なる場合、ステータスコード`415`（サポートしていないメディアタイプ）が返却される
- RESTfulウェブサービスでは`@Context`アノテーションやCDIは使用できない

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, adapters-jaxrs-adaptor.json:s2, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5