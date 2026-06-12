**結論**: リソースクラスに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、`BeanUtil.createAndCopy()` でFormをEntityに変換して `UniversalDao.insert()` でDB登録する。ステータスコード `201` の `HttpResponse` を返す。

---

**根拠**:

#### 1. Formクラスの作成

リクエストJSONを受け取るFormクラスを作成する。プロパティは**全てString型**で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. リソースクラスの実装

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

ポイント:
- `@Path` でURLパスを指定し、`@POST` でHTTP POSTメソッドに紐づける
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストボディをJSON形式で受け付ける
- `@Valid` でBean Validationによる入力値チェックを実行する
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値はリソース作成完了（ステータスコード `201`）を示す `HttpResponse`

#### 3. URLマッピング設定（RoutesMapping）

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>

<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- その他のハンドラは省略 -->
      <component-ref name="packageMapping" />
    </list>
  </property>
</component>
```

#### 4. Jersey環境のJSON設定（JerseyJaxRsHandlerListFactory）

Jersey環境ではJacksonによるJSON変換を自動設定できる:

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

これにより `BodyConvertHandler`（Jackson2BodyConverter）と `JaxRsBeanValidationHandler` が自動的にハンドラキューに追加される。

#### 5. UniversalDAO設定

コンポーネント定義に `BasicDaoContextFactory` を追加する:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- Formのプロパティは**全てString型**で宣言すること（数値型等は不可）
- `RoutesMapping` は初期化対象リスト（`initializeList`）にも設定が必要

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-architecture.json:s4, adapters-jaxrs-adaptor.json:s2, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s8, handlers-body-convert-handler.json:s5, libraries-universal-dao.json:s6

---