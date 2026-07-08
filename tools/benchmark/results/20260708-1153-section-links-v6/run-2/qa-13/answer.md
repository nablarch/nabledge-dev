**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたリソースメソッドで Form を受け取り、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` で登録する。登録完了後は HTTP 201 を返却する。

**根拠**:

フォームクラスの作成:

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

業務アクションメソッドの実装:

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

リクエストボディの JSON 変換とバリデーションの仕組み:

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、`リクエストボディ変換ハンドラ`（`BodyConvertHandler`）が `application/json` に対応した `BodyConverter` でリクエストボディを Form に変換する
- `@Valid` アノテーションを設定することで、`Jakarta RESTful Web Servcies Bean Validationハンドラ`がそのメソッドで受け取る Form に対して Bean Validation を実行する。バリデーションエラーが発生した場合は `ApplicationException` を送出して後続処理を中断する

DB登録の仕組み:

- `UniversalDao.insert()` を使用することで、Jakarta Persistence アノテーションを付けた Entity クラスを指定するだけで、SQL を書かずに登録処理を実行できる
- `BeanUtil.createAndCopy(Project.class, project)` で Form から Entity への変換を行う

URL マッピング:
- `@Path` アノテーションと `@POST` アノテーションを使用して POST リクエスト時にマッピングする業務アクションメソッドを定義する

**注意点**:

- Form のプロパティは**全て String 型**で宣言すること。String 以外のプロパティが存在し不正な値が送信された場合、バリデーション実施前の Bean 変換処理が失敗して予期せぬ例外が発生するため
- `BodyConvertHandler` に `application/json` 対応の `BodyConverter`（例: `Jackson2BodyConverter`）が設定されていること。設定がない場合はステータスコード 415 が返却される
- `BodyConvertHandler` は `ルーティングアダプタ` より後ろに設定すること

参照:
- 登録機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md
  プロジェクト情報を登録する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  SQLを書かなくても単純なCRUDができる
  ユニバーサルDAOを使うための設定を行う
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
- リクエストボディ変換ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md
  変換処理を行うコンバータを設定する
  リクエストボディをFormに変換する
- Bean Validation
  .claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md
  バリデーションルールの設定方法