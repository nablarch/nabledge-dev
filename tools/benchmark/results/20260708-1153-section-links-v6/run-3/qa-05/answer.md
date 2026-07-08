**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、①Formクラスを作成し、②業務アクションメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付けて実装し、③`UniversalDao.insert()` でDBに登録します。

**根拠**:

**1. フォームの作成**

リクエストボディのJSONを受け取るためのFormクラスを作成します。プロパティは全てString型で宣言し、Bean Validationアノテーションでバリデーションルールを設定します。

```java
public class ProjectForm implements Serializable {

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

- `@Consumes(MediaType.APPLICATION_JSON)` ：リクエストをJSON形式で受け付けることを指定
- `@Valid` ：`JaxRsBeanValidationHandler` によりFormに対してBean Validationが実行される。バリデーションエラー時は `ApplicationException` がスローされ後続処理は実行されない
- `BeanUtil.createAndCopy()` ：FormをEntityに変換
- `UniversalDao.insert()` ：Entityをデータベースに登録
- 戻り値に `HttpResponse` のステータスコード201（CREATED）を返却

**3. ハンドラ設定（コンポーネント定義）**

`BodyConvertHandler` に、`application/json` を処理できる `BodyConverter` 実装を設定します。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- JSON対応コンバータ（JaxRsアダプタが提供） -->
      <component class="nablarch.fw.jaxrs.Jackson2BodyConverter" />
    </list>
  </property>
</component>
```

**注意点**:
- `@Consumes` に指定したMIMEとリクエストのContent-Typeが異なる場合、ステータスコード415が返却される
- `BodyConvertHandler` は `ルーティングアダプタ` より後ろに配置する必要がある
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` より後ろに配置する必要がある

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
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  ユニバーサルDAOを使うための設定を行う