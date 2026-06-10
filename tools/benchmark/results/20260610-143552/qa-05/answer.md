**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`アノテーションを付けたメソッドを定義し、`BeanUtil.createAndCopy`でEntityに変換後に`UniversalDao.insert`で登録する。

**根拠**:

**① Formクラスの作成**

リクエストボディを受け付けるFormを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソース(アクション)クラスの実装**

URLマッピング(`@Path`, `@POST`)、JSON受付(`@Consumes`)、バリデーション(`@Valid`)、DB登録の順に実装する。

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

**ポイント:**
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディのJSONをFormに変換するよう`リクエストボディ変換ハンドラ`に指示する
- `@Valid`: `Jakarta RESTful Web Servcies Bean Validationハンドラ`がFormに対してBean Validationを実行する
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する
- `UniversalDao.insert(entity)`: EntityをDBに登録する
- 戻り値の`HttpResponse.Status.CREATED`でステータスコード`201`を返す

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの制約）
- `@Valid`アノテーションがない場合、バリデーションは実行されない
- `リクエストボディ変換ハンドラ`はルーティングアダプタより後ろに、`Bean Validationハンドラ`はリクエストボディ変換ハンドラより後ろに設定すること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4