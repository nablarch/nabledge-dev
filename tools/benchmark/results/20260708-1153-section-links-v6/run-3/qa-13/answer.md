**結論**: RESTfulウェブサービスでフォームのデータをDBに登録するには、①全プロパティをString型にしたFormクラスを作成、②`@Path`/`@POST`でURLマッピングしたアクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、`BeanUtil.createAndCopy`でEntityに変換後、`UniversalDao.insert`を呼び出す。

**根拠**:

**1. Formクラスの作成**

```java
public class ProjectForm implements Serializable {

    // 一部のみ抜粋

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全てString型で宣言する（外部からどのような値が送られてきてもBeanへの変換が失敗しないよう保証するため。String以外の型に不正な値が送られるとバリデーション前に変換エラーが発生し障害となる）

**2. アクションメソッドの実装**

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

各アノテーション・メソッドのポイント:

| 要素 | 目的 |
|---|---|
| `@Path("/projects")` + `@POST` | POSTリクエストをこのメソッドにマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして受け付け、Formに変換 |
| `@Valid` | Bean Validationを実行（バリデーションエラー時はアクションメソッドは呼ばれない） |
| `BeanUtil.createAndCopy(Project.class, project)` | FormをEntityに変換 |
| `UniversalDao.insert(...)` | DB登録 |
| `new HttpResponse(HttpResponse.Status.CREATED.getStatusCode())` | 201 Createdを返却 |

**3. リクエストボディ変換の設定（インフラ設定）**

コンポーネント定義ファイルで`BodyConvertHandler`に使用するMIMEに対応した`BodyConverter`を設定する:

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/xmlに対応したリクエスト・レスポンスのコンバータ -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
      <!-- application/x-www-form-urlencodedに対応したリクエスト・レスポンスのコンバータ -->
      <component class="nablarch.fw.jaxrs.FormUrlEncodedConverter" />
    </list>
  </property>
</component>
```

**注意点**:
- Formのプロパティは全てString型のみ使用すること
- `@Consumes`に設定したMIMEと異なるContent-Typeのリクエストが来た場合、ステータスコード`415`（Unsupported Media Type）が返却される

参照:
- 登録機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md
  プロジェクト情報を登録する
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  バリデーションルールの設定方法
  RESTfulウェブサービスのユーザ入力値のチェックを行う
- リクエストボディ変換ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md
  変換処理を行うコンバータを設定する
  リクエストボディをFormに変換する