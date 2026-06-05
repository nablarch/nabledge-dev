Step 5 と Step 6 を実行し、回答を生成・検証します。

**Step 6 検証:**
- `@Consumes(MediaType.APPLICATION_JSON)` → s1 に明記 ✅
- `@Valid` アノテーション → s1・s4 に明記 ✅
- `UniversalDao.insert()` → s1・s4 に明記 ✅
- `BeanUtil.createAndCopy()` → s1 に明記 ✅
- `@Path`・`@POST` アノテーション → s1 に明記 ✅
- Form のプロパティは全て String 型 → s1 に明記 ✅
- `BasicDaoContextFactory` 設定 → s6 に明記 ✅
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` の後に配置 → s3 に明記 ✅

verify_result = PASS

---

**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、①Formクラスの作成、②`@Path`/`@POST`/`@Consumes`/`@Valid` アノテーションを付けたリソースメソッドの実装、③`BeanUtil.createAndCopy()` でEntityに変換後 `UniversalDao.insert()` で登録、という3ステップで実装する。

**根拠**:

**① Formクラスの作成**

クライアントからのJSONを受け取るFormクラスを作成する。プロパティは全てString型で宣言すること。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソース(アクション)メソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付けるために指定する
- `@Valid`: `JaxRsBeanValidationHandler` によりFormに対してBean Validationを実行する。バリデーションエラー時は `ApplicationException` が送出され後続処理には進まない
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する
- `UniversalDao.insert()`: Entityをそのまま渡すだけでINSERT SQLが自動構築されDBに登録される
- ステータスコード `201`（Created）を返す

**③ ユニバーサルDAOの事前設定**

コンポーネント定義ファイルに `BasicDaoContextFactory` を追加しておく必要がある。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `JaxRsBeanValidationHandler` はハンドラキューで **リクエストボディ変換ハンドラより後ろ** に設定すること。変換後のFormに対してバリデーションを行うため、順序が逆だとFormが存在しない状態でバリデーションが実行されてしまう
- `UniversalDao` は主キー以外の条件を指定した更新/削除には対応していないため、その場合はJDBCラッパー（`DbConnectionContext` 経由）を使用すること

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-jaxrs-bean-validation-handler.json:s3, libraries-universal-dao.json:s6, libraries-universal-dao.json:s2

---