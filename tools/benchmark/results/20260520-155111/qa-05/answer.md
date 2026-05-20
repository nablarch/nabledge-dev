**結論**: RESTfulウェブサービスでJSON登録を受け付けるリソースクラスは、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたメソッドにフォームを引数として定義し、`BeanUtil.createAndCopy` でエンティティに変換して `UniversalDao.insert` で登録する。

**根拠**:

**フォームクラス（リクエストJSON受け取り用）**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する（Bean Validationのルール）。

**リソース（アクション）クラス**

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

1. **`@Path`** と **`@POST`** でURLとHTTPメソッドをマッピングする。
2. **`@Consumes(MediaType.APPLICATION_JSON)`** でリクエストをJSON形式で受け付けることを宣言する。リクエストボディのJSONは `BodyConvertHandler` によってフォームへ自動変換される。
3. **`@Valid`** でリクエストのBean Validationが実行される（`JaxRsBeanValidationHandler` が処理）。
4. **`BeanUtil.createAndCopy`** でフォームをエンティティクラスに変換する。
5. **`UniversalDao.insert`** でDBへ登録する。
6. 登録完了は**ステータスコード`201`（Created）**を返却する。

**注意点**:
- Jakarta RESTful Web Servicesの `@PathParam` / `@QueryParam` はNablarchでは使用**不可**。パスパラメータが必要な場合は `JaxRsHttpRequest` を引数に追加して `req.getPathParam("id")` で取得する。
- RESTfulウェブサービスでは排他制御ライブラリ（taglib連動前提）は使用できない。楽観的ロックが必要な場合はリクエストボディにバージョン番号を含める設計にする。

参照: `restful-web-service-getting-started-create.json:s1`, `restful-web-service-resource-signature.json:s1`, `handlers-body-convert-handler.json:s5`