**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、引数にFormクラスを受け取る。DBへの登録は `UniversalDao.insert()` で行う。リクエストJSONからFormへの変換は `BodyConvertHandler` が自動的に担う。

**根拠**:

**処理の流れ**

1. `BodyConvertHandler` がリクエストボディをアクションメソッドの引数型（Formクラス）に変換する。変換に使うフォーマットはメソッドの `@Consumes` アノテーションで決まる。
2. `JaxRsBeanValidationHandler` が `@Valid` アノテーションを基にバリデーションを実行する。
3. アクションメソッドが呼ばれ、`BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録する。
4. `HttpResponse` を返却する（登録完了時はステータスコード `201`）。

**実装例**（GettingStartedのプロジェクト登録機能より）

Formクラス:
```java
public class ProjectForm implements Serializable {
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

**ハンドラの最小構成**（BodyConvertHandlerの配置）

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <list>
          <component class="nablarch.fw.jaxrs.BodyConvertHandler">
            <!-- application/jsonに対応したコンバータを設定 -->
          </component>
          <component class="nablarch.fw.jaxrs.JaxRsBeanValidationHandler" />
        </list>
      </property>
    </component>
  </property>
</component>
```

なお、`BodyConvertHandler` は `ルーティングアダプタ` よりも後ろに設定する必要がある（ディスパッチ先特定後にアノテーション情報を参照するため）。

**ユニバーサルDAOの設定**（コンポーネント定義に追加）

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全て `String` 型で宣言する（バリデーションルールの設定方法を参照）。
- `@Valid` がないとバリデーションが実行されないため忘れずに付与すること。
- `BodyConvertHandler` に `application/json` 対応のコンバータが設定されていないと、ステータスコード `415`（Unsupported Media Type）が返却される。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-body-convert-handler.json:s4, component/libraries/libraries-universal-dao.json:s6