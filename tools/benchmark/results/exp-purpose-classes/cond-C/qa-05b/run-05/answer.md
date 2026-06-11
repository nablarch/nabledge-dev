**結論**: RESTfulウェブサービスでJSON受信 → DB登録を実装するには、`@Consumes(APPLICATION_JSON) @Valid` を付けたメソッドでFormを受け取り、`BeanUtil.createAndCopy` でEntityに変換して `UniversalDao.insert` でDBに登録する。

**根拠**:

**1. フォームクラスの作成**

リクエストボディのJSONを受け取るFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソース（アクション）クラスのメソッド実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを宣言する。リクエストボディの変換は `BodyConvertHandler` が行う
- `@Valid` アノテーションを付けることで、`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する。バリデーションエラー時は `ApplicationException` が送出される
- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する
- 戻り値として `201 Created` を返す

**3. URLマッピング（`@Path` アノテーション方式）**

```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        // 実装
    }
}
```

`@Path` アノテーションを使う場合、ディスパッチハンドラに `PathOptionsProviderRoutesMapping` を設定する必要がある。

**メソッドシグネチャ（引数・戻り値）まとめ**:

| 引数の型 | 用途 |
|---|---|
| フォーム（Java Beans） | リクエストボディをFormに変換して受け取る |
| `JaxRsHttpRequest` | パスパラメータ・クエリーパラメータ・ヘッダを使う場合 |
| 組み合わせ | 両方を同時に扱える |

| 戻り値の型 | 説明 |
|---|---|
| `HttpResponse` | ステータスコードを明示的に返す場合 |
| フォーム（Java Beans） | JSONレスポンスとして返す場合（`@Produces` と組み合わせ） |
| `void` | `204 NoContent` を返す |

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8