**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、Formクラスを作成し、業務アクションメソッドに `@Valid` アノテーションを付けて `UniversalDao.insert()` でDB登録する。

**根拠**:

#### 1. Formクラスの作成

クライアントから受け取るデータをFormクラスとして定義する。プロパティは**すべてString型**で宣言すること（型変換はバリデーション後に行う）。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. 業務アクションメソッドの実装

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付ける
- `@Valid` アノテーションを付けると `JaxRsBeanValidationHandler` がFormに対してBean Validationを自動実行する（バリデーションエラー時は `ApplicationException` を送出）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値はステータスコード `201 Created` を表す `HttpResponse` を返す

#### 3. ユニバーサルDAOの設定

コンポーネント定義ファイルに `BasicDaoContextFactory` を設定する必要がある:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `JaxRsBeanValidationHandler` は `BodyConvertHandler`（リクエストボディ変換ハンドラ）の**後ろ**に設定すること
- Formのプロパティを `String` 以外の型にすると、不正な値が送信された場合にバリデーション前に変換エラーが発生する

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/handlers/handlers-jaxrs-bean-validation-handler.json:s3, component/libraries/libraries-bean-validation.json:s8, component/libraries/libraries-universal-dao.json:s6