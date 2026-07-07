# qa-19 — run-2

## 質問

REST APIでJSONを受け取ってDBに登録する処理を作りたい

## 回答

**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラスを作成し、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けて、`UniversalDao.insert()` でDBに登録する。ハンドラキューの `BodyConvertHandler` がリクエストのJSONを自動的にフォームクラスに変換する。

**根拠**:

**1. フォームクラスの作成**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

プロパティは全て `String` 型で宣言する。

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でBean Validationを実行する
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換してから `UniversalDao.insert()` で登録する
- レスポンスとしてステータスコード `201 Created` を返す

**3. 処理の流れ（仕組み）**

| No. | ハンドラ | 処理内容 |
|---|---|---|
| 3 | データベース接続管理ハンドラ | DB接続を取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット/ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを特定 |
| 6 | リクエストボディ変換ハンドラ (BodyConvertHandler) | JSONをフォームクラスに変換 |
| 7 | JaxRsBeanValidationハンドラ | フォームにバリデーションを実行 |

**4. JSONコンバータの設定（Jerseyアダプタ使用時）**

`JerseyJaxRsHandlerListFactory` を使用すると、JSONのコンバータとして `Jackson2BodyConverter` が自動的に設定される。

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

**5. ユニバーサルDAOの設定**

コンポーネント定義に `BasicDaoContextFactory` を追加する必要がある。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**: フォームのプロパティは全て `String` 型で宣言すること。`@Consumes` に設定したMIMEと異なる `Content-Type` がリクエストヘッダに設定されていた場合、ステータスコード `415` が返却される。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [RESTfulウェブサービスの処理の流れ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#restfulウェブサービスの処理の流れ) (s2)
- [最小ハンドラ構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#最小ハンドラ構成) (s4)
- [変換処理を行うコンバータを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#変換処理を行うコンバータを設定する) (s4)
- [リクエストボディをFormに変換する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#リクエストボディをformに変換する) (s5)
- [Jersey環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#jersey環境下でrestfulウェブサービスを使用する) (s2)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly mentions Jackson2BodyConverter in section 4, stating that when using JerseyJaxRsHandlerListFactory, Jackson2BodyConverter is automatically configured as the JSON converter. This directly addresses the Expected Output fact that Jackson2BodyConverter is responsible for JSON body conversion. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing the request to create a process for receiving JSON via REST API and registering it in a database. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「JSONのボディ変換はJackson2BodyConverterが担当する」は回答の「JerseyJaxRsHandlerListFactory を使用すると、JSONのコンバータとして Jackson2BodyConverter が自動的に設定される」（セクション4）に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- JSONのボディ変換はJackson2BodyConverterが担当する
