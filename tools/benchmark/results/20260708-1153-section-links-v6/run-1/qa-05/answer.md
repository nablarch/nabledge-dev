**結論**: アクションメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与してJSONをFormで受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録する。

---

**根拠**:

### 1. Formクラスの作成

クライアントから送信されたJSONを受け付けるFormクラスを作成する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- **プロパティは全てString型で宣言する**（Bean Validationのバリデーションルール設定の要件）

---

### 2. アクションメソッドの実装

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

| アノテーション/メソッド | 役割 |
|---|---|
| `@POST` | POSTリクエストにマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | JSON形式のリクエストボディを受け付ける |
| `@Valid` | JaxRsBeanValidationHandlerによるバリデーションを実行 |
| `BeanUtil.createAndCopy()` | FormをEntityに変換 |
| `UniversalDao.insert()` | DBへ登録 |
| `HttpResponse(201)` | リソース作成完了を示すステータスコードを返却 |

---

### 3. JSON変換の仕組み（BodyConvertHandler）

リクエストボディ変換ハンドラが `@Consumes` のMIMEタイプに対応したコンバータでリクエストボディをFormに変換する。Jersey環境では `JerseyJaxRsHandlerListFactory` を使用することで、以下のコンバータが自動設定される。

- JSON → `Jackson2BodyConverter`
- XML → `JaxbBodyConverter`
- application/x-www-form-urlencoded → `FormUrlEncodedConverter`

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

---

### 4. ユニバーサルDAOの設定

コンポーネント定義ファイルに以下を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が異なる場合、ステータスコード `415`（サポートしていないメディアタイプ）が返却される
- バリデーションエラー時は `ApplicationException` が送出され、後続の処理は行われない

参照:
- 登録機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md
  プロジェクト情報を登録する
- リクエストボディ変換ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md
  変換処理を行うコンバータを設定する
  リクエストボディをFormに変換する
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
- Jakarta RESTful Web Servicesアダプタ
  .claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md
  Jersey環境下でRESTfulウェブサービスを使用する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  ユニバーサルDAOを使うための設定を行う