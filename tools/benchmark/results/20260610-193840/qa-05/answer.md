**結論**: リソースクラスに `@Path` + `@POST` を付けたメソッドを定義し、`@Consumes(APPLICATION_JSON)` + `@Valid` を指定した上で、`BeanUtil.createAndCopy()` でFormをEntityに変換して `UniversalDao.insert()` でDB登録し、ステータスコード `201` の `HttpResponse` を返す。

---

**根拠**:

**①フォームクラスの作成**

JSONリクエストを受け取るFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**②リソースクラスの実装**

`@Path` でURLを定義し、`@POST` + `@Consumes(APPLICATION_JSON)` + `@Valid` を組み合わせて登録メソッドを実装する。

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
- `@Consumes(MediaType.APPLICATION_JSON)` — リクエストボディをFormに変換するBodyConverterにJSON処理を委譲する。Formへの変換は `BodyConvertHandler` が自動的に行う
- `@Valid` — Formオブジェクトに対するBean Validationが実行される（`JaxRsBeanValidationHandler` が担当）
- `BeanUtil.createAndCopy(Project.class, project)` — FormからEntityへ変換する
- `UniversalDao.insert()` — EntityのJakarta PersistenceアノテーションをもとにINSERT文が自動生成されDBに登録される
- 戻り値として `201 Created` を示す `HttpResponse` を返す

**③メソッド引数・戻り値の選択肢**

| 引数定義 | 使いどころ |
|---|---|
| フォーム(Java Beans) | リクエストボディから変換したフォームで処理する場合（登録処理の基本形） |
| JaxRsHttpRequest | パスパラメータ・クエリパラメータ・HTTPヘッダが必要な場合 |
| ExecutionContext | スコープ変数にアクセスしたい場合 |
| 組み合わせ | 例: `save(ProjectForm form, JaxRsHttpRequest request)` |

| 戻り値の型 | 挙動 |
|---|---|
| void | `204 NoContent` を返す |
| フォーム(Java Beans) | BodyConvertHandlerがレスポンスボディに変換して返す |
| HttpResponse | ステータスコードやヘッダを任意に指定できる |

**④コンポーネント設定（JSON対応）**

`BodyConvertHandler` の `bodyConverters` にJSONコンバータを設定する（`application/json` 対応）:

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- JSON対応のコンバータを設定 -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
    </list>
  </property>
</component>
```

また、UniversalDAOを使うためには `BasicDaoContextFactory` のコンポーネント定義が必要:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- `@Consumes` に設定したMIMEとリクエストヘッダの `Content-Type` が異なる場合は `415 Unsupported Media Type` が返される
- バリデーションエラー時の挙動は `JaxRsBeanValidationHandler` の設定に依存する
- レスポンスヘッダを個別に指定したい場合は `HttpResponse` に `setHeader()` を使用する。`@Produces` でBeanを返す場合は `EntityResponse` を使うこと

**参照**:
- restful-web-service-getting-started-create.json:s1
- restful-web-service-resource-signature.json:s1
- handlers-body-convert-handler.json:s4, s5
- handlers-jaxrs-bean-validation-handler.json:s4
- libraries-universal-dao.json:s2, s6
- adapters-router-adaptor.json:s8