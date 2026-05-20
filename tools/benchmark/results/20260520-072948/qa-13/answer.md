**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`@Consumes` + `@Valid` アノテーションを付けたアクションメソッドで Form を受け取り、`BeanUtil.createAndCopy` でエンティティに変換した後 `UniversalDao.insert` でDBに登録する。

**根拠**:

**① Formクラスの作成**

クライアントから送信されたJSONを受け付けるFormを作成する。プロパティは全て `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定すると、リクエストボディ変換ハンドラ (`BodyConvertHandler`) がJSONをFormに変換する
- `@Valid` アノテーションを設定すると、`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する。バリデーションエラーが発生した場合は `ApplicationException` が送出される
- `BeanUtil.createAndCopy` でFormをEntityに変換し、`UniversalDao.insert` でDBに登録する
- ステータスコード `201` (Created) を表す `HttpResponse` を返す

**③ コンポーネント設定**

ユニバーサルDAOを使用するには、コンポーネント定義に以下を追加する。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `BodyConvertHandler` の `bodyConverters` に `application/json` に対応したコンバータを設定しておく必要がある。設定されていないMIMEが使用された場合は415が返る
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` より後ろに設定すること（変換後のFormに対してバリデーションを実行するため）
- `UniversalDao` は主キー以外の条件を指定した更新/削除には使用できない。その場合はデータベースアクセス(JDBCラッパー)を使用すること

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6