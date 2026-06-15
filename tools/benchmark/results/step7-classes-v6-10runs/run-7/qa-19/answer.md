**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドを定義し、`BeanUtil.createAndCopy` でEntityに変換したうえで `UniversalDao.insert` でDB登録する。

**根拠**:

**1. フォームクラスの作成**

リクエストのJSONを受け取るFormクラスを作成する。プロパティは全てString型で宣言し、Bean Validationアノテーションでバリデーションルールをつけることができる。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. アクションクラスの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言する
- `@Valid` を付けることで `JaxRsBeanValidationHandler` がFormのBean Validationを自動実行する（バリデーションエラーの場合は `ApplicationException` がスローされ後続処理は行われない）
- `BeanUtil.createAndCopy` でFormからEntityに値をコピーし、`UniversalDao.insert` でDB登録する
- 登録成功時はステータスコード `201`（CREATED）を返す

**3. ハンドラキューの構成**

リクエストボディのJSON変換には `BodyConvertHandler` が必要。Jersey環境では `JerseyJaxRsHandlerListFactory` を使うことで、JSONコンバータ（`Jackson2BodyConverter`）とBean Validationハンドラが自動設定される。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- Jersey用アダプタで自動的にBodyConvertHandlerとBeanValidationHandlerが設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

最小ハンドラ構成では以下の順で設定する:
| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URLとアクションのマッピング |
| 6 | リクエストボディ変換ハンドラ | JSONボディ→Formクラス変換 |
| 7 | Bean Validationハンドラ | Formのバリデーション実行 |

**注意点**:
- `BodyConvertHandler` はルーティングアダプタより後ろに設定する必要がある（アノテーション情報がディスパッチ後に確定するため）
- ユニバーサルDAOを使うには `BasicDaoContextFactory` のコンポーネント定義が必要（`daoContextFactory` という名前で定義する）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2