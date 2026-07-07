# qa-19 — run-3

## 質問

REST APIでJSONを受け取ってDBに登録する処理を作りたい

## 回答

**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドでJSONボディをFormとして受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録する。

**根拠**:

**1. 処理の流れ（ハンドラキュー）**

最小ハンドラ構成でのJSON受信～DB登録の流れ：

| No. | ハンドラ | 役割 |
|---|---|---|
| 3 | `DbConnectionManagementHandler` | DB接続取得・解放 |
| 4 | `TransactionManagementHandler` | トランザクション開始・コミット・ロールバック |
| 6 | `BodyConvertHandler` | リクエストボディ（JSON）→Formに変換 |
| 7 | `JaxRsBeanValidationHandler` | Bean Validationを実行 |

**2. JSONをFormに変換する仕組み**

`BodyConvertHandler` に設定されたコンバータが `Content-Type: application/json` のリクエストボディをFormクラスに変換する。Jerseyの場合、`JerseyJaxRsHandlerListFactory` を使うことで `Jackson2BodyConverter` が自動的に設定される：

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

**3. アクションの実装**

```java
// Formクラス
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する
    // ゲッタ・セッタ省略
}

// アクションクラス
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)  // JSONで受け取る
    @Valid                                  // Bean Validationを実行
    public HttpResponse save(ProjectForm project) {
        // FormをEntityに変換してDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode()); // 201
    }
}
```

**4. ユニバーサルDAO設定**

コンポーネント定義ファイルに `BasicDaoContextFactory` を追加する必要がある：

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Formのプロパティは全て `String` 型で宣言する（Bean Validationの要件）
- バリデーションエラー時は `ApplicationException` がスローされ、後続処理には進まない
- RESTEasy使用の場合は `JerseyJaxRsHandlerListFactory` の代わりに `ResteasyJaxRsHandlerListFactory` を使用する

参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1`, `processing-pattern/restful-web-service/restful-web-service-architecture.json:s4`, `component/handlers/handlers-body-convert-handler.json:s4`, `component/handlers/handlers-body-convert-handler.json:s5`, `component/adapters/adapters-jaxrs-adaptor.json:s2`, `component/handlers/handlers-jaxrs-bean-validation-handler.json:s4`, `component/libraries/libraries-universal-dao.json:s6`

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [最小ハンドラ構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#最小ハンドラ構成) (s4)
- [変換処理を行うコンバータを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#変換処理を行うコンバータを設定する) (s4)
- [リクエストボディをFormに変換する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#リクエストボディをformに変換する) (s5)
- [Jersey環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#jersey環境下でrestfulウェブサービスを使用する) (s2)
- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)
- [RESTfulウェブサービスの処理の流れ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#restfulウェブサービスの処理の流れ) (s2)
- [リソース(アクション)の処理結果をレスポンスボディに変換する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#リソースアクションの処理結果をレスポンスボディに変換する) (s6)
- [RESTEasy環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#resteasy環境下でrestfulウェブサービスを使用する) (s3)
- [データベースアクセス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-feature-details.md#データベースアクセス) (s3)
- [SQLを書かなくても単純なCRUDができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#sqlを書かなくても単純なcrudができる) (s2)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly mentions `Jackson2BodyConverter` in section 2, stating that when using Jersey, `JerseyJaxRsHandlerListFactory` causes `Jackson2BodyConverter` to be automatically configured. This directly covers the Expected Output fact that JSON body conversion is handled by `Jackson2BodyConverter`. The coverage is complete. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing the request to create a process for receiving JSON via REST API and registering it to a database. No irrelevant statements were identified! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「JSONのボディ変換はJackson2BodyConverterが担当する」は回答の「Jerseyの場合、`JerseyJaxRsHandlerListFactory` を使うことで `Jackson2BodyConverter` が自動的に設定される」に含まれている |
| answer_relevancy | NG | 回答末尾に「参照: `processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1`, ...」など内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ内容と矛盾なし（adapters-jaxrs-adaptor.md でJersey環境時にJackson2BodyConverterが設定されることが確認でき、コード例・ハンドラ構成も一致する） |

### 参照事実（expected_facts）

- JSONのボディ変換はJackson2BodyConverterが担当する
