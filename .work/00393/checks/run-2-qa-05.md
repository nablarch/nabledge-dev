# qa-05 — run-2

## 質問

REST APIでJSONを受け取ってDBに登録する処理を作りたい

## 回答

**結論**: REST APIでJSONを受け取りDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`UniversalDao.insert()` でエンティティを保存します。

**根拠**:

**1. フォームクラスを作成する**

クライアントから受け取るJSONをマッピングするフォームを作成します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // その他プロパティ（全てString型で宣言すること）
    // ゲッタ及びセッタは省略
}
```

**2. アクションクラスを実装する**

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディのJSONがフォームに変換される
- `@Valid` を指定することで、Bean Validationによるバリデーションが実行される（エラー時は `ApplicationException` が送出される）
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDBに登録する
- レスポンスとして登録完了（ステータスコード `201`）を返す

**3. コンポーネント設定（Jersey環境の場合）**

JSONのボディ変換には `Jackson2BodyConverter` が必要です。Jersey環境では以下の設定で自動的に構成されます。

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- Jerseyのハンドラキューを設定するとJackson2BodyConverter等が自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
  ...
</component>
```

**4. ユニバーサルDAOの設定**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームのプロパティは全て `String` 型で宣言すること
- `@Consumes` に設定したMIMEと異なる `Content-Type` がリクエストに含まれる場合、ステータスコード `415` が返される
- `UniversalDao.insert()` に渡すのはフォームではなくエンティティクラスであるため、`BeanUtil.createAndCopy()` での変換が必要

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6, adapters-jaxrs-adaptor.json:s2

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [変換処理を行うコンバータを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#変換処理を行うコンバータを設定する) (s4)
- [リクエストボディをFormに変換する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#リクエストボディをformに変換する) (s5)
- [リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md#リソースアクションで受け取るformbeanに対してバリデーションを実行する) (s4)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)
- [Jersey環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#jersey環境下でrestfulウェブサービスを使用する) (s2)
- [ディスパッチハンドラを変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#ディスパッチハンドラを変更する) (s7)
- [マッピングの実装方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#マッピングの実装方法) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both key facts from the Expected Output. It mentions creating a Form class to receive values from the client (フォームクラスを作成する section with ProjectForm example), and explicitly states that all properties should be declared as String type (フォームのプロパティは全て `String` 型で宣言すること in both the code comment and the 注意点 section). Both expected facts are fully addressed. |
| answer_relevancy | 0.95 | 0.95 | OK | The score is 0.95 because the response was largely relevant to the task of creating a REST API that receives JSON and registers it to a DB, with only a minor irrelevant statement regarding form properties needing to be declared as String type in all cases, which is incorrect and not always applicable. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「Formクラスでクライアントから送信された値を受け付ける」は回答の「クライアントから受け取るJSONをマッピングするフォームを作成します」およびProjectFormコード例に含まれている。参照事実「プロパティは全てString型で宣言する」は回答の注意点「フォームのプロパティは全て `String` 型で宣言すること」に含まれている |
| answer_relevancy | OK | 回答全体が「REST APIでJSONを受け取りDBに登録する」という質問に直接答えており、フォームクラス作成・アクション実装・コンポーネント設定・DAO設定・注意点いずれも質問の目的に沿った情報。DeepEvalが「minor irrelevant」と指摘したString型プロパティの制約もNablarch固有の必須要件であり、質問に答える上で必要な情報。的外れな内容は含まれていない。 |
| faithfulness | OK | 回答の主要な主張はすべてナレッジMDと一致している。`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid`・`UniversalDao.insert(BeanUtil.createAndCopy(...))`・ステータスコード201はrestful-web-service-getting-started-create.mdと完全一致。Content-TypeがConsumes設定と異なる場合に415を返す点はhandlers-body-convert-handler.mdと一致。プロパティはString型で宣言するという注意点もナレッジに記載あり。矛盾する記述はない。 |

### 参照事実（expected_facts）

- Formクラスでクライアントから送信された値を受け付ける
- プロパティは全てString型で宣言する
