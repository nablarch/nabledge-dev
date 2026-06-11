**結論**: JSON登録処理は、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたメソッドでFormを受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録するパターンで実装する。

**根拠**:

**① Formクラスの作成**

JSONの各フィールドを受け取るFormクラスを定義する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスのメソッド実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラがJSONをFormに変換する。Content-Typeが一致しない場合はステータスコード `415` が返却される。
- `@Valid` を指定することで、Bean Validationハンドラがメソッド実行前にFormのバリデーションを実行する。バリデーションエラー時は後続処理に進まず `ApplicationException` が送出される。
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDBに登録する。
- 戻り値として、リソース作成完了を示すステータスコード `201` の `HttpResponse` を返却する。
- URLマッピングは `@Path` と `@POST` アノテーションで定義する。

**注意点**: Formのプロパティは全てString型で宣言する必要がある。また、バリデーションルールはBean Validationのアノテーション（`@Required`、`@Domain` など）でFormに定義する。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2