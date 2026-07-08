# qa-19 — run-1

## 質問

REST APIでJSONを受け取ってDBに登録する処理を作りたい

## 回答

**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションクラスに `@Consumes(MediaType.APPLICATION_JSON)` を付けたメソッドを定義し、`BodyConvertHandler`（内部でJackson2BodyConverterを使用）がJSONをFormクラスに変換した後、`UniversalDao.insert()` でDBに登録する。

---

**根拠**:

### 処理の流れ

リクエストが届いてからDBに登録されるまで、以下の流れで処理される。

1. **WebFrontController** (ServletFilter) がリクエストを受信
2. **ルーティングアダプタ** (RoutesMapping) がURIをもとに呼び出すアクションクラス・メソッドを決定
3. **BodyConvertHandler** がリクエストボディ（JSON）をアクションメソッドで受け取るFormクラスに変換（`@Consumes`で指定したMIMEタイプに対応するBodyConverterを使用）
4. **JaxRsBeanValidationHandler** が変換済みFormにバリデーションを実行（`@Valid`が付いている場合）
5. **アクションクラス** が業務ロジック（DB登録）を実行
6. **JaxRsResponseHandler** がレスポンスをクライアントへ返却

### 最小ハンドラ構成

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外時のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラー時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得/解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始/コミット/ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | BodyConvertHandler | JSONボディ ⇔ Formクラスの変換 |
| 7 | JaxRsBeanValidationHandler | Formのバリデーション実行 |

### JSON変換の仕組み

`BodyConvertHandler`は、アクションメソッドの`@Consumes`アノテーションで指定されたMIMEタイプに対応する`BodyConverter`を使って変換する。JSONの場合、`Jackson2BodyConverter`が使用される。

Jersey環境ではJerseyアダプタ、RESTEasy環境ではRESTEasyアダプタを使うと、`Jackson2BodyConverter`を含むBodyConvertHandlerが自動的に設定される。

```xml
<!-- Jersey環境の場合 -->
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

### アクションクラスの実装例

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm project) {
        // BeanUtilでFormをEntityに変換し、UniversalDaoでDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

実装のポイント:
- `@Path("/projects")` + `@POST` でPOSTリクエスト時のマッピングを定義
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言
- `@Valid` でFormへのバリデーションを有効化（JaxRsBeanValidationHandlerが実行）
- `BeanUtil.createAndCopy(Entity.class, form)` でFormをEntityに変換
- `UniversalDao.insert(entity)` でDB登録（SQLは不要、Jakarta Persistenceアノテーションから自動構築）
- 戻り値はステータスコード`201`（リソース作成完了）を表すHttpResponse

### フォームクラスの実装例

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // getter/setter省略
}
```

### ユニバーサルDAOの設定

ユニバーサルDAOを使用するには、コンポーネント定義に以下を追加する。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**: `@Consumes`に設定したMIMEとリクエストの`Content-Type`が異なる場合は、ステータスコード`415`（Unsupported Media Type）が返却される。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6

## 参照ナレッジ

- [プロジェクト情報を登録する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md#プロジェクト情報を登録する) (s1)
- [RESTfulウェブサービスの処理の流れ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#restfulウェブサービスの処理の流れ) (s2)
- [最小ハンドラ構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#最小ハンドラ構成) (s4)
- [リクエストボディをFormに変換する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#リクエストボディをformに変換する) (s5)
- [Jersey環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#jersey環境下でrestfulウェブサービスを使用する) (s2)
- [SQLを書かなくても単純なCRUDができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#sqlを書かなくても単純なcrudができる) (s2)
- [変換処理を行うコンバータを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md#変換処理を行うコンバータを設定する) (s4)
- [RESTEasy環境下でRESTfulウェブサービスを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md#resteasy環境下でrestfulウェブサービスを使用する) (s3)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)
- [RESTfulウェブサービスで使用するハンドラ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md#restfulウェブサービスで使用するハンドラ) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly states that Jackson2BodyConverter is used for JSON conversion ('JSONの場合、`Jackson2BodyConverter`が使用される') and also mentions it in the context of BodyConvertHandler. This directly confirms the single expected fact that 'JSONのボディ変換はJackson2BodyConverterが担当する'. The fact is clearly present and accurately represented. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing the request to create a process for receiving JSON via REST API and registering it to a DB. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「JSONのボディ変換はJackson2BodyConverterが担当する」は回答の「JSONの場合、`Jackson2BodyConverter`が使用される。」（JSON変換の仕組みセクション）に含まれている |
| answer_relevancy | OK | 回答は「REST APIでJSONを受け取ってDBに登録する処理」という質問に対して、処理の流れ・最小ハンドラ構成・JSON変換の仕組み・アクションクラスの実装例・フォームクラスの実装例・UniversalDAOの設定をすべて提示しており、的外れな内容は含まれていない。 |
| faithfulness | OK | 回答の内容はナレッジファイルと一致している。処理フローはrestful-web-service-architecture.mdの記述と一致し、最小ハンドラ構成表（7ハンドラの順序・役割）も同ファイルの表と一致する。アクションクラスの実装例（@Path、@POST、@Consumes、@Valid、BeanUtil.createAndCopy、UniversalDao.insert、HttpResponse(201)）はrestful-web-service-getting-started-create.mdのコード例と一致する。フォームクラスの実装例も同様に一致しており、ナレッジの内容と矛盾する記述は見当たらない。 |

### 参照事実（expected_facts）

- JSONのボディ変換はJackson2BodyConverterが担当する
