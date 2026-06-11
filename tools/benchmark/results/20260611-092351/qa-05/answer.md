**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、引数にFormクラスを受け取って `BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDB登録する。

**根拠**:

**1. Formクラスの作成**

クライアントから送信される値を受け付けるFormを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラス（業務アクション）の実装**

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

- **`@Consumes(MediaType.APPLICATION_JSON)`**: リクエストボディをFormに変換するBodyConvertHandlerが、このアノテーションを元にJSONのパースを行う
- **`@Valid`**: JaxRsBeanValidationHandlerがFormに対してBean Validationを実行する。バリデーションエラー時は `ApplicationException` が送出される
- **`BeanUtil.createAndCopy(Project.class, project)`**: FormをEntityに変換する
- **`UniversalDao.insert()`**: エンティティをDBに登録する
- **戻り値**: 登録完了を示すステータスコード `201 Created` を返す

**3. URLマッピング**

`@Path` アノテーション（Pathアノテーションルーティングを使用する場合）でクラスとパスを紐づけ、`@POST` でHTTPメソッドを指定する。

| パス | HTTPメソッド | ディスパッチされるメソッド |
|---|---|---|
| `/projects` | `POST` | `ProjectAction#save()` |

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの仕様上の制約）
- `@Valid` が機能するには、ハンドラキューに `JaxRsBeanValidationHandler` が `BodyConvertHandler` より後ろに設定されている必要がある
- `@Path` アノテーションによるルーティングには、`PathOptionsProviderRoutesMapping` を使用するための設定が必要

参照: restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-router-adaptor.json:s8