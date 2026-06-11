**結論**: RESTful WebサービスでJSONを受け取ってDBに登録するには、フォームクラスを作成し、リソース(アクション)クラスのメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、`UniversalDao.insert()`でDBに登録します。

**根拠**:

**1. フォームクラスの作成**

クライアントから送信されるJSONのフィールドに対応したフォームを作成します。プロパティは全てString型で宣言します。

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

実装のポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストをJSON形式で受け付けることを宣言します。リクエストボディ変換ハンドラがこのアノテーションを見てJSONをFormに変換します。
- `@Valid` — Jakarta RESTful Web Services Bean ValidatonハンドラによりFormに対してBean Validationが実行されます。バリデーションエラー時は`ApplicationException`が送出されます。
- `BeanUtil.createAndCopy(Project.class, project)` — フォームをEntityに変換します。
- `UniversalDao.insert()` — Entityをそのままテーブルに登録します。SQLを書く必要はありません。
- 戻り値に`201 Created`を返します。

**3. ユニバーサルDAOの設定**

コンポーネント定義に以下を追加します：

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**4. URLマッピング**

`@Path`と`@POST`アノテーションで、POSTリクエスト時のマッピングを定義します（上記アクションクラスの例を参照）。

**注意点**:
- フォームのプロパティは全てString型で宣言すること（Bean Validationの仕様）。
- `@Valid`を設定しないとバリデーションは実行されません。
- ユニバーサルDAOの使用には、データベースアクセス(JDBCラッパー)の設定も別途必要です。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6, restful-web-service-resource-signature.json:s1