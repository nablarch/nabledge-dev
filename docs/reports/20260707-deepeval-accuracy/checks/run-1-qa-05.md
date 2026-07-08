# qa-05 — run-1

## 質問

REST APIでJSONを受け取ってDBに登録する処理を作りたい

## 回答

**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたアクションメソッドでJSONをFormとして受け取り、`BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` でDBに登録する。

**根拠**:

**① Formクラスの作成**

クライアントから受け取るJSONのフィールドに対応したFormクラスを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② アクションメソッドの実装**

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONをFormクラスに自動変換する（`Jackson2BodyConverter` が使用される）
- `@Valid` を付けることで `JaxRsBeanValidationHandler` がFormのBean Validationを実行する
- `BeanUtil.createAndCopy(Project.class, project)` でFormからEntityクラスに値をコピーする
- `UniversalDao.insert()` でDBにINSERTする
- `@Path` と `@POST` でURLとHTTPメソッドをマッピングする

**③ リクエストボディ変換ハンドラの設定（Jersey環境の場合）**

`JaxRsMethodBinderFactory` の `handlerList` に `JerseyJaxRsHandlerListFactory` を設定することで、JSONのコンバータ（`Jackson2BodyConverter`）やBean Validationハンドラが自動的に設定される。

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

**④ ユニバーサルDAOの設定**

コンポーネント定義に `BasicDaoContextFactory` を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- Content-TypeヘッダとメソッドのConsumes指定が異なる場合、ステータスコード `415` (Unsupported Media Type) が返却される
- `@Valid` が設定されたメソッドでバリデーションエラーが発生した場合、`ApplicationException` がスローされ後続処理は実行されない

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6, adapters-router-adaptor.json:s8

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [変換処理を行うコンバータを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#変換処理を行うコンバータを設定する) (s4)
- [リクエストボディをFormに変換する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#リクエストボディをformに変換する) (s5)
- [Jersey環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#jersey環境下でrestfulウェブサービスを使用する) (s2)
- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [RESTEasy環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#resteasy環境下でrestfulウェブサービスを使用する) (s3)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)
- [マッピングの実装方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#マッピングの実装方法) (s8)
- [フィールドの詳細](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-core-beans-BeanUtil.md#フィールドの詳細) (s1)
- [フィールドの詳細](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-fw-web-HttpResponse.md#フィールドの詳細) (s1)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers both facts from the Expected Output: (1) it mentions using a Form class to receive values from the client (Formクラスを作成する、クライアントから受け取るJSONのフィールドに対応したFormクラス), and (2) it explicitly states that all properties are declared as String type (プロパティは全てString型で宣言する). Both expected facts are present and accurately represented without contradiction. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing the request to create a process for receiving JSON via REST API and registering it to a database. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「Formクラスでクライアントから送信された値を受け付ける」は回答の「クライアントから受け取るJSONのフィールドに対応したFormクラスを作成する」に含まれている。参照事実「プロパティは全てString型で宣言する」は回答の「プロパティは全てString型で宣言する」に明示されている。 |
| answer_relevancy | OK | 回答はREST APIでJSONを受け取りDBに登録する処理という質問に直接答えており、Formクラスの作成・アクションメソッドの実装・Jersey設定・UniversalDAO設定という必要な手順を網羅している。的外れな情報は含まれていない。 |
| faithfulness | OK | 回答の主要な内容（ProjectFormクラス、@Consumes/@Valid/@Path/@POSTアノテーション、BeanUtil.createAndCopy、UniversalDao.insert、HttpResponse.Status.CREATED）はすべてナレッジファイル(restful-web-service-getting-started-create.md)の記述と一致している。矛盾する記述は確認されなかった。 |

### 参照事実（expected_facts）

- Formクラスでクライアントから送信された値を受け付ける
- プロパティは全てString型で宣言する
