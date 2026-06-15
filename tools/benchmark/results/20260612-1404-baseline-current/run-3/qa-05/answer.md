**結論**: RESTfulウェブサービスでJSONをDBに登録するには、リソース(アクション)クラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を設定し、`BeanUtil.createAndCopy()` でFormをEntityに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**1. Formクラスの作成**

JSON受信用のFormを作成する。プロパティは全てString型で宣言すること。

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**2. アクションクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストを受け付けることを指定する
- `@Valid`: リクエストボディ変換後にBean Validationを実行する（`JaxRsBeanValidationHandler`が処理）
- `BeanUtil.createAndCopy()`: FormをEntityに変換する
- `UniversalDao.insert()`: EntityをDBに登録する
- ステータスコード`201`（作成完了）を返却する

**3. ユニバーサルDAOの設定**

コンポーネント定義に以下を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**4. BodyConvertHandlerの設定（JSON変換用コンバータ）**

`BodyConvertHandler`の`bodyConverters`プロパティにJSONコンバータを設定する（ブランクプロジェクトでは設定済み）。Jacksonベースのコンバータが`application/json`を処理する。

**注意点**:
- `JaxRsBeanValidationHandler`は`BodyConvertHandler`よりも後ろに設定すること（変換後のFormに対してバリデーションするため）
- Formのプロパティは全てString型で宣言すること
- Content-TypeヘッダがConsumesに設定したMIMEと異なる場合、ステータスコード`415`が返却される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s3, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6