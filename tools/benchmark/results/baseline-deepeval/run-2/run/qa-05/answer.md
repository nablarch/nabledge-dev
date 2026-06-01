**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、Formクラスを引数に取るリソースメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、`BeanUtil.createAndCopy()` でエンティティに変換後 `UniversalDao.insert()` でDBに登録する。

---

**根拠**:

#### 1. Formクラスの作成

リクエストボディのJSONをマッピングするFormクラスを作成する。プロパティは**全てString型**で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. リソース(アクション)クラスの実装

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

- `@Path("/projects")` をクラスに付与してURLとマッピングする
- `@POST` でHTTPメソッドを指定する
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストがJSON形式であることを宣言する。リクエストボディは自動的にFormに変換される
- `@Valid` でBean Validationによる入力値チェックを行う
- `BeanUtil.createAndCopy(Project.class, project)` でFormからエンティティへ変換する
- `UniversalDao.insert()` でDBに登録する
- 戻り値として `HttpResponse.Status.CREATED`（ステータスコード `201`）を返す

#### 3. メソッド引数・戻り値の選択肢

| 用途 | 引数/戻り値 |
|------|-----------|
| JSONリクエストボディ受け取り | フォーム（Java Beans） |
| パスパラメータ・クエリパラメータ | `JaxRsHttpRequest`（`getPathParam()` / `getParamMap()` で取得） |
| ステータスコード・ヘッダ指定 | `HttpResponse` |
| JSONレスポンス返却 | `@Produces(MediaType.APPLICATION_JSON)` + Bean戻り値 |
| ボディなしレスポンス（204） | `void` |

**注意点**:
- Jakarta RESTful Web Servicesで規定されている `@PathParam` や `@QueryParam` は Nablarch では使用できない。パスパラメータは `JaxRsHttpRequest.getPathParam()` で取得すること
- RESTfulウェブサービスでは `排他制御` ライブラリ（クライアントtaglibとの連動前提）は使用できないため、楽観的ロックが必要な場合はリクエストボディに直接バージョン番号を含めること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, adapters-router-adaptor.json:s8

---