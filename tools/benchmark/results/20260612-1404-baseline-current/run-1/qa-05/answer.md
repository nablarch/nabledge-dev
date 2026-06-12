**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付与し、`BeanUtil.createAndCopy`でFormからEntityへ変換した上で`UniversalDao.insert`を呼び出します。

**根拠**:

**1. Formクラスの作成**

JSONのプロパティを受け取るFormクラスを作成します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言します。

**2. アクションクラスの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` ― リクエストボディをJSON形式で受け付けます。`BodyConvertHandler`がJSONをFormオブジェクトに変換します。
- `@Valid` ― `JaxRsBeanValidationHandler`がFormに対してBean Validationを実行します。バリデーションエラーが発生すると`ApplicationException`がスローされます。
- `BeanUtil.createAndCopy` ― FormをEntityに変換します。
- `UniversalDao.insert` ― EntityをDBに登録します。
- `HttpResponse.Status.CREATED`（ステータスコード201）を返します。

**3. ユニバーサルDAOの設定**

コンポーネント定義ファイルに以下を追加します。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `Content-Type`ヘッダが`application/json`以外の場合、ステータスコード415（Unsupported Media Type）が返却されます。
- `UniversalDao.insert`を使用するには、`BasicDaoContextFactory`の設定に加えてデータベースアクセス（JDBCラッパー）の設定も必要です。
- フォームのプロパティは全てString型で宣言する必要があります（数値型などの型変換はバリデーション/BeanUtilが担います）。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6