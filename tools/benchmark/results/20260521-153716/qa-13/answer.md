Step 5: 回答を生成します。

---

**結論**: RESTfulウェブサービスでのDB登録は、①String型プロパティのみを持つFormクラス、②`@Path`/`@POST`/`@Consumes`/`@Valid`アノテーション付きアクションメソッド、③`BeanUtil.createAndCopy()`でEntity変換後に`UniversalDao.insert()`でDB登録、という3ステップで実装する。

---

**根拠**:

**① Formクラスの作成**

クライアントから送信されたJSONを受け取るFormクラスを作成する。**プロパティは全てString型で宣言する**ことがポイント。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② 業務アクションメソッドの実装**

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
| `@Path("/projects")` | URLとアクションクラスのマッピング |
| `@POST` | POSTリクエストへのメソッドマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | JSONリクエストボディの受け付け |
| `@Valid` | Bean Validationによる入力チェック |

**③ FormからEntityへの変換とDB登録**

- `BeanUtil.createAndCopy(Project.class, project)` でFormをEntityに変換
- `UniversalDao.insert()` でDBに登録
- 戻り値にステータスコード`201`（リソース作成完了）を表す`HttpResponse`を返却

---

**注意点**:
- `@Valid`を設定するだけでBean Validationが自動実行される。バリデーションエラー時のレスポンスはJakarta RESTful Web Services Bean Validationハンドラが処理する
- `UniversalDao`を使用するには、コンポーネント定義に`BasicDaoContextFactory`の設定が必要:
  ```xml
  <component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
  ```
- `BeanUtil.createAndCopy()`はForm側と一致するプロパティ名をEntity側にコピーし、型変換も行う

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-bean-util.json:s2, libraries-universal-dao.json:s6, adapters-router-adaptor.json:s8

---