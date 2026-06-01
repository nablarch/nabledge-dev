**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドで `ProjectForm` を受け取り、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` で登録する。

**根拠**:

**① Formクラスの作成**

プロパティは全て `String` 型で宣言し、バリデーションアノテーションを設定する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

> プロパティを全て `String` 型にする理由: バリデーション前にBeanへの変換処理が行われるため、String以外の型に不正な値が来ると変換処理が失敗し例外が発生する。

**② アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストボディを `ProjectForm` に変換する（`BodyConvertHandler` が処理）
- `@Valid`: `JaxRsBeanValidationHandler` がFormに対してバリデーションを実行する
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する
- `UniversalDao.insert(...)`: EntityをDBに登録する（SQL記述不要）
- 戻り値はステータスコード `201 Created`

**③ Entityクラスの定義**

Jakarta PersistenceアノテーションをEntityに付けることでSQLなしにCRUD操作ができる。

```java
@Entity
@Table(name = "PROJECT")
public class Project {

    @Id
    @Column(name = "PROJECT_ID")
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long projectId;

    @Column(name = "PROJECT_NAME")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**④ ハンドラキュー構成**（`@Path`アノテーション使用時）

ルーティングハンドラは `PathOptionsProviderRoutesMapping` を使用し、`JaxRsMethodBinderFactory` に `BodyConvertHandler` と `JaxRsBeanValidationHandler` を設定する。

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

> `JerseyJaxRsHandlerListFactory`（Jersey環境）を使用すると、`BodyConvertHandler` と `JaxRsBeanValidationHandler` が自動的にハンドラキューに追加される。

**注意点**:
- `@Valid` アノテーションがないとバリデーションが実行されない
- FormのプロパティはString以外にすると不正な入力値で例外が発生する
- `@Path` アノテーション使用時は `PathOptionsProviderRoutesMapping` への変更と初期化設定が必要

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s4, libraries-universal-dao.json:s2, libraries-universal-dao.json:s24, libraries-bean-validation.json:s8, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s7

---