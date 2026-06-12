**結論**: RESTfulウェブサービスでのDB登録は、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーションを付けたアクションメソッドで、`BeanUtil.createAndCopy()` でFormをEntityに変換し `UniversalDao.insert()` で登録するパターンが標準実装です。

**根拠**:

```java
// Formクラス（プロパティは全てString型で定義）
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ・セッタ省略
}

// アクションクラス
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm form) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディのJSONをFormに変換するBodyConverterが選択される
- `@Valid`: Jakarta RESTful Web Services Bean ValidationハンドラがFormのバリデーションを実行する
- `BeanUtil.createAndCopy(Entity.class, form)`: FormからEntityへの変換
- `UniversalDao.insert()`: EntityをDBに登録（SQLファイル不要）
- レスポンスはステータスコード `201 (CREATED)` を返却

**コンポーネント定義への設定**（UniversalDAO使用時）:
```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全て`String`型で宣言し、型変換はBeanUtilが行う
- RESTfulウェブサービスでは `排他制御` ライブラリ（taglibと連動するもの）は使用不可。楽観的ロックが必要な場合はリクエストボディに直接バージョン番号を含めて `UniversalDao` の楽観的ロック機能を使うこと
- `ETag` / `If-Match` を使った楽観的ロックはNablarch RESTfulウェブサービスでは対応していない

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-body-convert-handler.json:s5, restful-web-service-feature-details.json:s4