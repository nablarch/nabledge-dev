**結論**: アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`BeanUtil.createAndCopy` でFormをEntityに変換してから `UniversalDao.insert` で登録します。

**根拠**:

**1. Formクラスの作成**

リクエストJSONを受け取るFormクラスを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でBean Validationによるバリデーションを実行する
- `BeanUtil.createAndCopy` でFormをEntityに変換する
- `UniversalDao.insert` でDBへ登録する
- 戻り値にステータスコード `201`（Created）の `HttpResponse` を返す
- `@Path` と `@POST` でURLとHTTPメソッドのマッピングを定義する

**3. JSONコンバータの設定（Jerseyの場合）**

`JerseyJaxRsHandlerListFactory` を使うことで、JSONコンバータ（`Jackson2BodyConverter`）が自動的に設定されます。

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

**4. ユニバーサルDAOのEntityアノテーション例**

```java
@Entity
@Table(name = "PROJECT")
public class Project {
    @Id
    @Column(name = "PROJECT_ID")
    private Long projectId;

    @Column(name = "PROJECT_NAME")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**注意点**:
- `BodyConvertHandler` の `bodyConverters` プロパティに `application/json` 対応のコンバータが設定されていない場合、ステータスコード `415`（Unsupported Media Type）が返される
- RESTfulウェブサービスでは `排他制御` ライブラリは使用できない。楽観的ロックを行う際はリクエストボディにバージョン番号を含めること

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2