**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@POST`+`@Consumes(MediaType.APPLICATION_JSON)`+`@Valid`を付けたアクションメソッドを作成し、`BeanUtil.createAndCopy`でフォームをエンティティに変換後、`UniversalDao.insert`でDBに登録する。

**根拠**:

**1. フォームクラスの作成**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全て`String`型**で宣言すること（外部入力値をBeanに変換する前にバリデーションを行うため）

**2. 業務アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付ける
- `@Valid` でリクエストのBean Validationを実行する
- `BeanUtil.createAndCopy` でフォームをエンティティに変換する
- `UniversalDao.insert` でDBに登録する
- ステータスコード`201`（リソース作成完了）を返却する

**3. URLマッピング**

`@Path` と `@POST` アノテーションを使用してPOSTリクエスト時のマッピングを定義する（上記コード参照）。

**4. JSON変換の設定（コンポーネント設定ファイル）**

Jersey環境の場合は `JerseyJaxRsHandlerListFactory` を使用すると、JSONコンバータ（`Jackson2BodyConverter`）が自動的に設定される：

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

RESTEasy環境の場合は `ResteasyJaxRsHandlerListFactory` を使用する。

**注意点**:
- `BeanUtil.createAndCopy` を使う場合、フォームのプロパティ名とエンティティのプロパティ名が一致している必要がある
- `@Valid` はメソッド引数にフォームを受け取る場合に使用する。バリデーションエラー時は `JaxRsBeanValidationHandler` が処理する
- `UniversalDao` を使うには `BasicDaoContextFactory` のコンポーネント定義が必要

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-bean-validation.json:s8, libraries-bean-validation.json:s17, libraries-universal-dao.json:s6