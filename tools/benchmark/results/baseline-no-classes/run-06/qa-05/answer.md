**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスを作成し、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`UniversalDao.insert()` でDB登録する。

**根拠**:

**① Formクラスの作成**（リクエストボディのJSON受け取り先）

```java
public class ProjectForm implements Serializable {
    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全て `String` 型**で宣言する（バリデーション仕様のため）。

**② アクションクラスの実装**

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

- `@Path("/projects")` + `@POST` でURLとHTTPメソッドをマッピング。
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストボディをJSON形式で受け取る。この指定により、`BodyConvertHandler` がリクエストボディをFormに変換する。
- `@Valid` アノテーションにより、`JaxRsBeanValidationHandler` がFormのバリデーションを自動実行する。
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換後、`UniversalDao.insert()` でDB登録。
- 登録成功時はステータスコード `201` を返す。

**③ ハンドラへのコンバータ設定**（コンポーネント設定ファイル）

`application/json` に対応した `BodyConverter` を `BodyConvertHandler` の `bodyConverters` プロパティに設定する必要がある。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- JSON対応のコンバータを設定する -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
    </list>
  </property>
</component>
```

**注意点**: `Content-Type: application/json` でリクエストしないと、ステータスコード `415`（サポートしていないメディアタイプ）が返却される。

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-router-adaptor.json:s8