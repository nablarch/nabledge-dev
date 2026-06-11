**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付けたアクションメソッドを作成し、`BeanUtil.createAndCopy`でフォームをエンティティに変換後、`UniversalDao.insert`でDBに登録する。

**根拠**:

**1. フォームクラスの作成**

クライアントから送信されたJSONを受け付けるフォームを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. 業務アクションメソッドの実装**

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

- `@Path`・`@POST`でPOSTリクエスト時のURLマッピングを定義する
- `@Consumes(MediaType.APPLICATION_JSON)`でJSON形式のリクエストボディを受け付ける（`BodyConvertHandler`がFormに変換する）
- `@Valid`でBean Validationを実行する（`JaxRsBeanValidationHandler`が処理する）
- `BeanUtil.createAndCopy`でフォームをエンティティに変換し、`UniversalDao.insert`でDBに登録する
- 戻り値としてリソース作成完了（ステータスコード`201`）を返す

**3. ユニバーサルDAOの設定**

コンポーネント定義ファイルに`BasicDaoContextFactory`を追加する。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `JaxRsBeanValidationHandler`（`@Valid`の処理）は、`BodyConvertHandler`（JSON→Form変換）よりも後ろにハンドラキューへ設定すること
- `BodyConvertHandler`の`bodyConverters`プロパティにJSON用の`BodyConverter`を設定していない場合、ステータスコード`415`（Unsupported Media Type）が返される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6