**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付与した業務アクションメソッドで受け取ったFormを、`BeanUtil.createAndCopy()`でEntityに変換し、`UniversalDao.insert()`でDBに登録する。

**根拠**:

1. **Formクラスの作成** — JSONのキーに対応するプロパティを持つFormクラスを作成する。

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタ
}
```

> プロパティは全て`String`型で宣言する。

2. **業務アクションメソッドの実装** — `@Path`・`@POST`でURLをマッピングし、メソッドに`@Consumes`と`@Valid`を付与する。

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

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付ける
- `@Valid`: フォームに対してバリデーションを実行する（`JaxRsBeanValidationHandler`が処理）
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換
- `UniversalDao.insert(...)`: Entityをそのままインサート
- 戻り値にステータスコード`201 Created`を返す

3. **コンポーネント定義の設定** — `BodyConvertHandler`に`application/json`対応のコンバータを設定する。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <component class="nablarch.fw.jaxrs.Jackson2BodyConverter" />
    </list>
  </property>
</component>
```

また、ユニバーサルDAOを使用するために以下の設定も必要。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `Consumes`に設定したMIMEとリクエストヘッダの`Content-Type`が一致しない場合、ステータスコード`415`が返される
- バリデーションエラー時のレスポンスは`JaxRsResponseHandler`が制御する

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
- ルーティングアダプタ
  .claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md
  Jakarta RESTful Web ServicesのPathアノテーションでマッピングする