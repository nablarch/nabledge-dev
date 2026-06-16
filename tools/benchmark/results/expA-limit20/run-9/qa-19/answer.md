**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`BodyConvertHandler`（Jackson2BodyConverter）がリクエストボディをFormに変換した後、`UniversalDao.insert()` でDBに登録する流れになります。

---

**根拠**:

**処理の流れ**

1. クライアントからのPOSTリクエスト（Content-Type: `application/json`）
2. `BodyConvertHandler` が `Jackson2BodyConverter` を使ってJSONボディをFormオブジェクトに変換
3. `JaxRsBeanValidationHandler` が `@Valid` アノテーションに従ってバリデーション実行
4. アクションメソッドが `UniversalDao.insert()` でDBに登録

**フォームの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言
- `@Valid` でリクエストデータのBean Validationを実行
- `BeanUtil.createAndCopy()` でFormをEntityに変換
- `UniversalDao.insert()` でDB登録（SQLを書かずにCRUD可能）
- 成功時はステータスコード `201`（作成完了）を返却

**アダプタの設定（コンポーネント定義）**

Jersey環境では、`JerseyJaxRsHandlerListFactory` を使うことでJSONのコンバータ（`Jackson2BodyConverter`）が自動設定されます:

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

**UniversalDAOのコンポーネント設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全て `String` 型で宣言する（Bean Validationの制約）
- `UniversalDao.insert()` を使う場合、EntityクラスにJakarta Persistenceアノテーション（`@Entity`、`@Table`、`@Id`、`@Column` 等）を付与する必要がある

参照: handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, restful-web-service-getting-started-create.json:s1, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6