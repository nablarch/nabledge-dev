# review-06 — run-3

## 質問

REST APIでURLパスの一部を受け取ったり、検索条件をURL末尾のパラメータで渡す実装はどう書く？ルーティングの設定も含めて確認したい

## 回答

**結論**: パスパラメータは `JaxRsHttpRequest#getPathParam(String)` で取得し、クエリーパラメータは `req.getParamMap()` を `BeanUtil.createAndCopy` でFormに変換して利用する。ルーティングはXMLファイル（`routes.xml`）か `@Path` アノテーションの2方式で設定できる。

---

**根拠**

## パスパラメータ

### ① XMLによるルーティング定義（`routes.xml`）

`routes.xml` にパスパラメータ部を `:パラメータ名` で記述し、`RoutesMapping` をハンドラキューの末尾に設定する。

```xml
<!-- routes.xml -->
<routes>
  <get path="users/:id" to="UsersResource#find">
    <requirements>
      <requirement name="id" value="\d+$" />
    </requirements>
  </get>
</routes>
```

コンポーネント設定（`RoutesMapping` を使う場合）:

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>
```

### ② `@Path` アノテーションによるルーティング定義

`PathOptionsProviderRoutesMapping` + `JaxRsPathOptionsProvider` を設定し、`@Path("{パラメータ名}")` で定義する。正規表現で書式制限も可能。

```java
@Path("/sample")
public class TestAction {

    @GET
    @Path("/bar/{id : \\d+}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

コンポーネント設定（`@Path` を使う場合）:

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="pathOptionsProvider">
    <component class="nablarch.integration.router.jaxrs.JaxRsPathOptionsProvider">
      <property name="applicationPath" value="${nablarch.webApi.applicationPath}" />
      <property name="basePackage" value="${nablarch.commonProperty.basePackage}" />
    </component>
  </property>
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

### アクション側でのパスパラメータ取得

いずれの方式でも、アクションメソッドの引数に `JaxRsHttpRequest` を受け取り、`getPathParam` で値を取得する。

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

---

## クエリーパラメータ

ルーティング定義ではクエリーパラメータを含めずパスのみを設定し、アクション側で `req.getParamMap()` を `BeanUtil.createAndCopy` でFormに変換する。

ルーティング（`@Path` 方式）:

```java
@Path("/projects")
public class ProjectAction {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public List<Project> find(JaxRsHttpRequest req) {

        // リクエストパラメータをBeanに変換
        ProjectSearchForm form =
                BeanUtil.createAndCopy(ProjectSearchForm.class, req.getParamMap());

        // BeanValidation実行
        ValidatorUtil.validate(form);

        ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, form);
        return UniversalDao.findAllBySqlFile(Project.class, "FIND_PROJECT", searchCondition);
    }
}
```

XML方式の場合のルーティング定義（クエリーパラメータはパスから除外）:

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

---

**注意点**

- Jakarta RESTful Web Servicesで規定されている `@PathParam` / `@QueryParam` アノテーションは使用できない。`JaxRsHttpRequest` を使って取得すること。
- `@Path` アノテーション方式は、JBoss/WildFly のようにクラスパスをvfsで管理するサーバでは使用できない。その場合はXML方式（`routes.xml` + `RoutesMapping`）を使うこと。
- Formクラスのプロパティは全て `String` 型で宣言すること。

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9, restful-web-service-getting-started-search.json:s1

## 参照ナレッジ

- [パスパラメータを扱う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-resource-signature.md#パスパラメータを扱う) (s2)
- [クエリーパラメータを扱う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-resource-signature.md#クエリーパラメータを扱う) (s3)
- [ディスパッチハンドラを変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#ディスパッチハンドラを変更する) (s7)
- [マッピングの実装方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#マッピングの実装方法) (s8)
- [パスパラメータの定義](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#パスパラメータの定義) (s9)
- [ディスパッチハンドラを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#ディスパッチハンドラを設定する) (s3)
- [プロジェクト情報を検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-search.md#プロジェクト情報を検索する) (s1)
- [リソースクラスのメソッドのシグネチャ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-resource-signature.md#リソースクラスのメソッドのシグネチャ) (s1)
- [URIとリソース(アクション)クラスのマッピング](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-feature-details.md#uriとリソースアクションクラスのマッピング) (s5)
- [パスパラメータやクエリーパラメータ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-feature-details.md#パスパラメータやクエリーパラメータ) (s6)
- [ルート定義ファイルを作成する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#ルート定義ファイルを作成する) (s4)
- [Jakarta RESTful Web ServicesのPathアノテーションでマッピングする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#jakarta-restful-web-servicesのpathアノテーションでマッピングする) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both facts from the Expected Output checklist. Fact 1 (path parameters are defined in routing configuration and received in the resource class) is well covered through detailed XML and @Path annotation examples showing how path parameters are named in routing and retrieved via JaxRsHttpRequest#getPathParam. Fact 2 (query parameters are obtained from JaxRsHttpRequest) is also covered, showing req.getParamMap() usage. Both required facts are explicitly addressed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is perfectly relevant to the input, addressing REST API URL path parameters, query parameters, and routing configuration without any irrelevant statements. Great job! |
| faithfulness | 0.99 | 0.93 | NG | The score is 0.93 because the actual output incorrectly states that path parameter notation uses ':パラメータ名' (http-request-router notation), when the retrieval context specifies that it follows the Jakarta RESTful Web Services specification using '{パラメータ名}' notation. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- パスパラメータはルーティング設定で名前を定義しリソースクラスで受け取る
- クエリーパラメータはJaxRsHttpRequestから取得する
