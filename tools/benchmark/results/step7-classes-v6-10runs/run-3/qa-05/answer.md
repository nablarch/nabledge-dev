**結論**: RESTful ウェブサービスで JSON を受け取って DB に登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`BeanUtil` でフォームをエンティティに変換後 `UniversalDao.insert()` を呼び出す。

**根拠**:

**1. フォームクラスの作成**

受け取る JSON のフィールドに対応したフォームクラスを作成する。プロパティはすべて `String` 型で宣言し、バリデーションアノテーションを付ける。

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
    public HttpResponse save(ProjectForm form) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストが `application/json` であることを宣言する。`BodyConvertHandler` がこの設定をもとに `Jackson2BodyConverter` でリクエストボディを Form オブジェクトに変換する。
- `@Valid`: `JaxRsBeanValidationHandler` によりフォームのバリデーションが実行される。バリデーションエラー時は `ApplicationException` が送出される。
- `BeanUtil.createAndCopy(Project.class, form)`: フォームをエンティティクラスに変換する。
- `UniversalDao.insert(entity)`: エンティティを DB に登録する（SQL は自動生成）。
- 戻り値のステータスコードは `201`（作成完了）を返す。

**3. JSON コンバータの設定（Jersey 環境の場合）**

`JerseyJaxRsHandlerListFactory` を使用すると、JSON コンバータとして `Jackson2BodyConverter` が自動設定される。

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
- `Content-Type: application/json` ヘッダを含めてリクエストを送信すること。異なる MIME タイプを指定するとステータスコード `415` が返る。
- `UniversalDao` を使用するためには `BasicDaoContextFactory` のコンポーネント定義が必要。
- `BeanUtil.createAndCopy` を使わず、フォームと同じクラスを直接 `UniversalDao.insert()` に渡すことも可能（Form = Entity の場合）。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-jaxrs-adaptor.json:s2