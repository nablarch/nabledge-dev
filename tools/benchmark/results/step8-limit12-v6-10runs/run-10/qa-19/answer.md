**結論**: NablarchのRESTful WebサービスでJSONを受け取ってDBに登録する処理は、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付与し、`BeanUtil`でFormをEntityに変換して`UniversalDao.insert()`でDBに登録する形で実装する。

**根拠**:

#### 1. Formクラスの作成

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する

    // ゲッタ及びセッタ
}
```

#### 2. アクションメソッドの実装

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

**実装のポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` — JSON形式のリクエストを受け付ける指定
- `@Valid` — Bean Validationを実行する（バリデーションエラー時は`ApplicationException`が送出される）
- `BeanUtil.createAndCopy()` — FormをEntityに変換する
- `UniversalDao.insert()` — DBに登録する
- ステータスコード`201`（Created）をレスポンスとして返す

#### 3. 処理の仕組み（ハンドラによる自動変換）

リクエストボディからFormへのJSON変換は**リクエストボディ変換ハンドラ**（`BodyConvertHandler`）が行う。Jersey環境では以下の設定で、`Jackson2BodyConverter`（JSON変換）とBean Validationハンドラが自動的に構成される：

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyJaxRsHandlerListFactoryでJSON変換とバリデーションが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

RESTEasy環境の場合は`JerseyJaxRsHandlerListFactory`の代わりに`ResteasyJaxRsHandlerListFactory`を使用する。

**処理フロー**:
1. `BodyConvertHandler` がリクエストボディ（JSON）→ Form（Bean）に変換
2. `JaxRsBeanValidationHandler` がFormに対してBean Validationを実行
3. アクションメソッドが呼び出され、`UniversalDao.insert()`でDB登録
4. `JaxRsResponseHandler` がレスポンス（201 Created）をクライアントに返却

#### 4. ユニバーサルDAOの設定

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `UniversalDao`を使用するには、`BasicDaoContextFactory`のコンポーネント定義が必要
- バリデーションエラー時のレスポンスカスタマイズが必要な場合は`ErrorResponseBuilder`を継承して対応する

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6