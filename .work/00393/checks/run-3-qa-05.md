# qa-05 — run-3

## 質問

REST APIでJSONを受け取ってDBに登録する処理を作りたい

## 回答

**結論**: `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与したアクションメソッドでJSONボディを受け取り、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録する。

---

**根拠**:

**1. Formクラスを作成する**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全てString型で宣言する。

**2. アクションメソッドを実装する**

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

- `@Consumes(MediaType.APPLICATION_JSON)` : JSONリクエストを受け付けることを示す。リクエストボディ変換ハンドラがこのアノテーションをもとにJSONをFormへ変換する。
- `@Valid` : Bean Validationを実行する。
- `BeanUtil.createAndCopy` : FormをEntityクラスに変換する。
- `UniversalDao.insert` : Entityをデータベースに登録する。
- ステータスコード `201`（Created）を返す。

**3. コンポーネント設定（JSONボディコンバータの設定）**

Jersey環境の場合、`JerseyJaxRsHandlerListFactory` を設定することで、JSONコンバータとして `Jackson2BodyConverter` が自動的に組み込まれる。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyJaxRsHandlerListFactoryがJackson2BodyConverterを自動設定する -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

RESTEasy環境の場合は `ResteasyJaxRsHandlerListFactory` を使用する。

---

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの要件）。
- `@Consumes` に設定したMIMEとリクエストの `Content-Type` が一致しない場合、ステータスコード `415` が返される。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [変換処理を行うコンバータを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#変換処理を行うコンバータを設定する) (s4)
- [リクエストボディをFormに変換する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#リクエストボディをformに変換する) (s5)
- [Jersey環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#jersey環境下でrestfulウェブサービスを使用する) (s2)
- [マッピングの実装方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#マッピングの実装方法) (s8)
- [RESTfulウェブサービスのユーザ入力値のチェックを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md#restfulウェブサービスのユーザ入力値のチェックを行う) (s17)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts: it mentions creating a Form class to receive client-submitted values (ProjectForm implementing Serializable with properties), and explicitly states 'プロパティは全てString型で宣言する' (declare all properties as String type) both in the code example and in the notes section. Both expected facts from the checklist are present and accurately represented without distortion. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, which asks about creating a process to receive JSON via REST API and register it in a DB. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.92 | NG | The score is 0.92 because the actual output incorrectly frames the requirement for declaring all ProjectForm properties as String type as being specifically tied to Bean Validation, when the retrieval context presents this simply as a general property declaration rule, not a Bean Validation requirement. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「Formクラスでクライアントから送信された値を受け付ける」は回答の「ProjectFormクラスの作成とコード例」に含まれている。参照事実「プロパティは全てString型で宣言する」は回答の「- プロパティは全てString型で宣言する。」および「注意点」セクションに明示されている。 |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- Formクラスでクライアントから送信された値を受け付ける
- プロパティは全てString型で宣言する
