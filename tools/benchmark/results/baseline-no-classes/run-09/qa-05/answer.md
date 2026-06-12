**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドを作成し、`BeanUtil.createAndCopy()` でエンティティに変換してから `UniversalDao.insert()` で登録する。

**根拠**:

**① Formクラスの作成**

JSONのリクエストボディを受け取るFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② 業務アクションメソッドの実装**

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

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディがJSONとして受け付けられ、Formに変換される
- `@Valid` を指定することで、Formに定義したBean Validationルールが自動的に実行される
- `BeanUtil.createAndCopy(Project.class, project)` でFormをエンティティに変換する
- `UniversalDao.insert()` でDBに登録する
- ステータスコード `201`（リソース作成完了）を返す

**③ ユニバーサルDAOの設定（コンポーネント定義）**

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全てString型で宣言する必要がある
- RESTfulウェブサービスで楽観的ロックを行う場合、ETagやIf-Matchは使用できないため、リクエストボディに直接バージョン番号を含めること

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-router-adaptor.json:s8, component/libraries/libraries-universal-dao.json:s6