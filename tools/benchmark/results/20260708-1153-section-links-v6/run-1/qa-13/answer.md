**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、①Formクラスの作成、②`@Valid`付き業務アクションメソッドの実装、③`BeanUtil`でエンティティ変換して`UniversalDao.insert()`でDB登録、という3ステップで実装する。

**根拠**:

**① Formクラスの作成**

受け取る値のFormクラスはプロパティを全てString型で定義し、バリデーションアノテーションを付ける。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**ポイント**: プロパティは必ず`String`型で宣言すること（それ以外の型だと変換エラーで予期せぬ例外が発生する）。

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSON形式でリクエストを受け付ける宣言
- `@Valid`: メソッドに付けることで`JaxRsBeanValidationHandler`がFormのバリデーションを自動実行する
- `BeanUtil.createAndCopy(Project.class, project)`: FormからEntityへ変換する
- `UniversalDao.insert(...)`: Entityをそのままインサートする
- 戻り値はリソース作成完了を示すステータスコード`201`の`HttpResponse`

**③ URLマッピング**

`@Path`アノテーションでクラスとURLを対応付け、`@POST`アノテーションでHTTPメソッドを指定する。上記②のコード例でそのまま有効。

**注意点**:
- フォームのプロパティを`String`以外の型（数値型等）にすると、不正な値が送信されたときにバリデーション前の変換処理で例外が発生する。外部からの値は`String`で受け取り、バリデーション後に変換すること。
- `@Valid`を付け忘れるとバリデーションが実行されない。

参照:
- 登録機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md
  プロジェクト情報を登録する
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  バリデーションルールの設定方法
  RESTfulウェブサービスのユーザ入力値のチェックを行う
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する