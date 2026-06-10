**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラス（String型プロパティ + Beanバリデーションアノテーション）を作成し、リソースクラスのメソッドに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与して、`BeanUtil.createAndCopy` でエンティティに変換後 `UniversalDao.insert` でDB登録する。

---

**根拠**

**1. フォームクラスを作成する**

クライアントから送信されたJSONを受け付けるフォームを作成する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラスを実装する**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラがJSONリクエストボディを `ProjectForm` に自動変換する
- `@Valid` を指定することで、Jakarta RESTful Web Services Bean Validationハンドラがバリデーションを実行する。バリデーションエラー時は後続ハンドラに委譲せず `ApplicationException` をスローして処理を終了する
- `BeanUtil.createAndCopy` でフォームをエンティティに変換し、`UniversalDao.insert` でDB登録する
- 戻り値は `HttpResponse(201)` でリソース作成完了を返す

**3. URLとのマッピングを設定する（@Pathアノテーション方式）**

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定することで、クラスに付与した `@Path` アノテーションと `@POST` アノテーションによりURLマッピングが自動的に行われる。

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

---

**注意点**

- フォームのプロパティは全て **String型** で宣言すること（バリデーションルールの設定方法の制約）
- `@Valid` を指定しない場合、バリデーションは実行されない
- リクエストボディ変換ハンドラ（`BodyConvertHandler`）には `application/json` に対応した `BodyConverter` が設定されている必要がある。未設定の場合はステータスコード `415` が返却される
- `@Path` アノテーション方式は JBoss/WildFly（vfsファイルシステムで管理されるアプリケーションサーバ）では使用できない。その場合は `routes.xml` を使ったXML定義を使用すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8