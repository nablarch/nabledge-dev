**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドでフォームを受け取り、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

#### 1. Formクラスの作成

受信したJSONをマッピングするFormを作成する。プロパティは**全てString型**で宣言すること。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. アクションクラスの実装

`@Path` と `@POST` でURLマッピングを行い、`@Consumes(MediaType.APPLICATION_JSON)` でJSON受信を宣言する。

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
- `@Consumes(MediaType.APPLICATION_JSON)` を付けることで、リクエストボディのJSONが自動的にFormに変換される
- `@Valid` を付けることで、Bean Validationによるバリデーションが実行される（エラー時は `ApplicationException` が送出されて後続処理は行われない）
- `BeanUtil.createAndCopy(Project.class, project)` でFormからEntityに変換する
- `UniversalDao.insert(...)` でDBに登録する
- 戻り値はステータスコード `201`（リソース作成完了）の `HttpResponse` を返す

#### 3. ユニバーサルDAOの設定（コンポーネント定義）

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- リクエストのContent-Typeが `application/json` でない場合、ステータスコード `415`（Unsupported Media Type）が返却される
- Formのプロパティは全てString型で宣言する必要がある

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6