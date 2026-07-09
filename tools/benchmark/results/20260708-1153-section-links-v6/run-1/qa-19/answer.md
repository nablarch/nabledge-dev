**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、フォームを受け取り`BeanUtil.createAndCopy()`でEntityに変換後に`UniversalDao.insert()`でDBへ登録する。

**根拠**:

**① 実装の全体像**

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

**② フォームの作成**
```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

- フォームのプロパティは**全てString型**で宣言する（バリデーション後にBeanUtilで型変換される）

**③ 処理の仕組み**

ハンドラキューが以下の順で動作する（最小ハンドラ構成）:

| No. | ハンドラ | 処理内容 |
|-----|---------|---------|
| 1 | グローバルエラーハンドラ | 例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み／エラー時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット |
| 5 | ルーティングアダプタ | URLとアクションを紐付け |
| 6 | リクエストボディ変換ハンドラ | JSONをFormクラスに変換 |
| 7 | Bean Validationハンドラ | @ValidによるFormバリデーション |

**④ JSON→Formへの変換（No.6の仕組み）**

リクエストボディ変換ハンドラは、`@Consumes(MediaType.APPLICATION_JSON)`を元に、JSON対応の`BodyConverter`でリクエストボディをFormに変換する:

```java
// @Consumes(MediaType.APPLICATION_JSON)が設定されたメソッドでは、
// application/json対応BodyConverterでリクエストボディがProjectFormに変換される
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(ProjectForm project) { ... }
```

**⑤ バリデーション（No.7の仕組み）**

`@Valid`アノテーションを設定することで、変換後のFormに対してBean Validationが実行される。エラー時は`ApplicationException`が送出され後続処理は行われない:

```java
// Validアノテーションを付けるとProjectFormに対してバリデーションが実行される
@Valid
public HttpResponse save(ProjectForm project) { ... }
```

**⑥ Jakarta RESTful Web ServicesアダプタでJSONコンバータを有効化**

JerseyまたはRESTEasy用アダプタを使用することで、JSONコンバータ（`Jackson2BodyConverter`）とBean Validationハンドラが自動的に設定される:

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- Jerseyを使う場合 -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
  ...
</component>
```

**注意点**:
- `UniversalDao.insert()`に渡すのはEntityクラスのインスタンス（`@Table`などJakarta Persistenceアノテーションを付けたクラス）であり、Formは直接渡せない。`BeanUtil.createAndCopy(Entity.class, form)`で変換する
- URLのマッピングには`@Path`（クラスレベル）と`@POST`（メソッドレベル）を組み合わせる（routes.xmlによる定義も可能）
- ルーティングアダプタより後ろのハンドラ（No.6以降）はハンドラキューに直接設定せず、ルーティングアダプタの`methodBinderFactory`に設定する

参照:
- 登録機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md
  プロジェクト情報を登録する
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md
  RESTfulウェブサービスの処理の流れ
  最小ハンドラ構成
- リクエストボディ変換ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md
  リクエストボディをFormに変換する
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する