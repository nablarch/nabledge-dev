**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録する場合、リソースクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、Formを引数として受け取り、`BeanUtil.createAndCopy` でエンティティに変換してから `UniversalDao.insert` でDBに登録する。

---

**根拠**:

**① Formクラスの作成**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- フォームのプロパティは全て `String` 型で宣言する。

**② リソースクラスの実装**

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

各アノテーションの役割:

| アノテーション | 役割 |
|---|---|
| `@Path("/projects")` | URLとクラスのマッピング |
| `@POST` | POSTリクエストへのマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして受け付ける |
| `@Valid` | Formに対してBean Validationを実行する |

- `BeanUtil.createAndCopy(Project.class, project)` でFormをエンティティに変換
- `UniversalDao.insert(...)` でDBに登録
- 戻り値はリソース作成完了を示すステータスコード `201` の `HttpResponse`

**③ ハンドラの役割**

リクエスト処理の流れ:
1. **リクエストボディ変換ハンドラ**（`BodyConvertHandler`）: リクエストボディのJSONをFormに変換
2. **Bean Validationハンドラ**（`JaxRsBeanValidationHandler`）: Formに対してバリデーションを実行。バリデーションエラー時は `ApplicationException` を送出して処理終了

---

**注意点**:
- `BodyConvertHandler` は `ルーティングアダプタ` よりも後ろに設定すること
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` よりも後ろに設定すること
- RESTfulウェブサービスでは Jakarta RESTful Web Services 標準の `@PathParam` / `@QueryParam` は使用できず、`JaxRsHttpRequest` から取得する

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-body-convert-handler.json:s5