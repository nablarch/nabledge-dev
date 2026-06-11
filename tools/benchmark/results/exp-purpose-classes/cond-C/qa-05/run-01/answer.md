**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するリソースクラスは、メソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、引数のFormを`BeanUtil.createAndCopy()`でEntityに変換し、`UniversalDao.insert()`で登録するパターンが基本です。

---

**根拠**:

**① Formクラスの作成**

クライアントから受け取るJSONのプロパティを持つFormクラスを作成します。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラス（業務アクションメソッド）の実装**

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

- **`@Consumes(MediaType.APPLICATION_JSON)`**: JSONリクエストボディをFormクラスに変換するためのアノテーション。Content-TypeがこのMIMEタイプと異なる場合は415が返される。
- **`@Valid`**: メソッドで受け取るFormに対してBean Validationを実行するアノテーション。
- **`BeanUtil.createAndCopy(Project.class, project)`**: FormをEntityクラスに変換する。
- **`UniversalDao.insert()`**: EntityにJakarta PersistenceアノテーションさえあればSQL不要でDB登録できる。
- **`HttpResponse.Status.CREATED.getStatusCode()`**: リソース作成完了を表すステータスコード201を返す。

**③ URLマッピング**

- クラスに`@Path("/projects")`を付けてURLとリソースクラスを紐付ける。
- メソッドに`@POST`を付けてHTTPメソッドとメソッドを紐付ける。
- `@Path`アノテーションによるルーティングを使用する場合、`PathOptionsProviderRoutesMapping`をディスパッチハンドラとして設定する。

---

**注意点**:

- **Formのプロパティは全てString型で宣言する**（バリデーションルールの設定方法の制約）。
- `UniversalDao`を使うには、`BasicDaoContextFactory`のコンポーネント定義への追加が必要:
  ```xml
  <component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
  ```
- Jersey環境では`JerseyJaxRsHandlerListFactory`を使うと、JSONコンバータ（Jackson2BodyConverter）とBean Validationハンドラが自動設定される。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s7, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6, adapters-jaxrs-adaptor.json:s2