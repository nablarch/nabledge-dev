**結論**: RESTfulウェブサービスでJSONを受け取りDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`BeanUtil.createAndCopy` でフォームをエンティティに変換して `UniversalDao.insert` でDBに登録します。

**根拠**:

**1. フォームクラスの作成**

クライアントから送信されたJSONを受け付けるフォームクラスを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
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
- `@Consumes(MediaType.APPLICATION_JSON)` : リクエストをJSON形式で受け付けるために指定する
- `@Valid` : リクエストに対してBean Validationを実行する
- `BeanUtil.createAndCopy` : フォームをエンティティに変換する
- `UniversalDao.insert` : エンティティをDBに登録する
- 戻り値はリソース作成完了を表すステータスコード `201` の `HttpResponse` を返却する
- `@Path("/projects")` と `@POST` : URLとHTTPメソッドのマッピングを定義する

**3. ハンドラの設定（リクエストボディ変換）**

JSONのリクエストボディをフォームに変換するために、`BodyConvertHandler` の `bodyConverters` プロパティにJSONに対応したコンバータを設定します。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/jsonに対応したコンバータ -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
    </list>
  </property>
</component>
```

**4. ユニバーサルDAOの設定**

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `BodyConvertHandler` はルーティングアダプタよりも後ろに設定する必要があります
- `JaxRsBeanValidationHandler`（`@Valid` を処理するハンドラ）は `BodyConvertHandler` よりも後ろに設定する必要があります
- フォームのプロパティは全てString型で宣言してください

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6