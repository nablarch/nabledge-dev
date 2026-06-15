**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソース(アクション)クラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、メソッド引数にフォームクラスを宣言し、`UniversalDao.insert()` でDBに登録します。

**根拠**:

#### 1. フォームクラスの作成

JSONのフィールドをマッピングするフォームクラスを作成します。**プロパティは全てString型**で宣言することが必要です。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. アクションクラスの実装

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを宣言する
- `@Valid` を設定することで、`JaxRsBeanValidationHandler` がフォームに対してBean Validationを実行する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する
- 登録成功時のレスポンスとしてステータスコード `201` を返す

#### 3. JSONボディ変換の仕組み

リクエストボディのJSON→Form変換は `BodyConvertHandler`（リクエストボディ変換ハンドラ）が担います。JerseyまたはRESTEasy環境では、`JerseyJaxRsHandlerListFactory` / `ResteasyJaxRsHandlerListFactory` をコンポーネント定義に設定することで、Jacksonベースの `Jackson2BodyConverter` が自動的に組み込まれます。

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

#### 4. ユニバーサルDAOの設定

`UniversalDao` を使うには、コンポーネント定義に `BasicDaoContextFactory` を追加する必要があります。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームのプロパティが `String` 以外の型だと、不正な値が送信された際にBeanへの変換が失敗して予期せぬ例外が発生します。必ずString型で宣言してください。
- `@Valid` を付け忘れると、バリデーションが実行されないまま登録処理が走ります。

参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1`, `component/handlers/handlers-body-convert-handler.json:s5`, `component/adapters/adapters-jaxrs-adaptor.json:s2`, `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`, `component/libraries/libraries-universal-dao.json:s6`