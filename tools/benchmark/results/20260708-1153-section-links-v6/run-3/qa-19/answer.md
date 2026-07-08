**結論**: REST APIでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`UniversalDao.insert()` でDB登録する。ハンドラが自動的にJSONボディのFormへの変換とバリデーションを行う。

**根拠**:

**処理の流れ**

1. `BodyConvertHandler` がリクエストボディのContent-TypeとリソースメソッドのConsumesアノテーションを照合し、対応する `BodyConverter` でボディをFormに変換する
2. `JaxRsBeanValidationHandler` がFormに対して `@Valid` アノテーションを見て Bean Validationを実行する
3. リソースメソッドが実行され、`UniversalDao.insert()` でDBに登録する

**フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**業務アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` — JSONでリクエストを受け付けることを指定
- `@Valid` — リクエストのバリデーションを実行（`JaxRsBeanValidationHandler` がこれを見て処理）
- `BeanUtil.createAndCopy()` — FormをEntityに変換
- `UniversalDao.insert()` — DBへの登録
- ステータスコード `201`（リソース作成完了）を返却

**BodyConvertHandlerの設定（コンポーネント定義）**

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/json に対応したコンバータを設定する -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
      <!-- application/x-www-form-urlencoded に対応したコンバータ -->
      <component class="nablarch.fw.jaxrs.FormUrlEncodedConverter" />
    </list>
  </property>
</component>
```

`bodyConverters` に設定されたコンバータで変換できないMIMEが使用された場合、ステータスコード `415`（サポートしていないメディアタイプ）を返す。

**注意点**:
- FormのプロパティはすべてString型で宣言する
- `@Consumes` に設定されたMIMEとリクエストのContent-Typeが異なる場合はステータスコード `415` が返る
- ユニバーサルDAOを使用するためには `BasicDaoContextFactory` のコンポーネント設定が別途必要

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