# review-06 — run-1

## 質問

REST APIでURLパスの一部を受け取ったり、検索条件をURL末尾のパラメータで渡す実装はどう書く？ルーティングの設定も含めて確認したい

## 回答

**結論**: NablarchのRESTfulウェブサービスでは、パスパラメータ・クエリーパラメータともに `JaxRsHttpRequest` を使って取得する。ルーティングはXMLの `routes.xml`（`:パラメータ名` 記法）か `@Path` アノテーション（`{パラメータ名}` 記法）の2方式で設定できる。

---

**根拠**

### ルーティング設定：2つの方式

#### 方式A：XMLルート定義ファイル（routes.xml）

`RoutesMapping` をディスパッチハンドラとして設定し、クラスパス直下に `routes.xml` を作成する。

```xml
<!-- コンポーネント定義 -->
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="basePackage" value="sample.web.action" />
</component>
```

パスパラメータの場合、`:パラメータ名` で定義し、`requirements` で書式制約を指定できる：

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

クエリーパラメータの場合、ルーティングはクエリー部を除いたパスで定義する：

```xml
<routes>
  <get path="users/search" to="Users#search"/>
</routes>
```

#### 方式B：`@Path` アノテーション（Jakarta RESTful Web Services準拠）

`PathOptionsProviderRoutesMapping` + `JaxRsPathOptionsProvider` を使用する：

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

アクションクラスでは `{パラメータ名}` 記法でパスパラメータを定義する：

```java
@Path("/sample")
public class TestAction {

    @GET
    @Path("/foo/{param}")
    @Produces(MediaType.APPLICATION_JSON)
    public Person foo(JaxRsHttpRequest request) {
        String param = request.getPathParam("param");
        // 省略
    }

    @GET
    @Path("/bar/{id : \\d+}")   // 正規表現で書式制約
    @Produces(MediaType.APPLICATION_JSON)
    public Person bar(JaxRsHttpRequest request) {
        int id = Integer.parseInt(request.getPathParam("id"));
        // 省略
    }
}
```

---

### パスパラメータの取得（リソースクラス実装）

`JaxRsHttpRequest` を引数に定義し、`getPathParam("パラメータ名")` で取得する。ルーティング設定で使ったパラメータ名と一致させる：

```java
@Produces(MediaType.APPLICATION_JSON)
public User find(JaxRsHttpRequest req) {
    Long id = Long.valueOf(req.getPathParam("id"));
    return UniversalDao.findById(User.class, id);
}
```

---

### クエリーパラメータの取得（リソースクラス実装）

`JaxRsHttpRequest` を引数に定義し、`getParamMap()` で取得後、`BeanUtil.createAndCopy` でFormクラスにマッピングする：

```java
public HttpResponse search(JaxRsHttpRequest req) {

    // リクエストパラメータをBeanに変換
    UserSearchForm form = BeanUtil.createAndCopy(UserSearchForm.class, req.getParamMap());

    // バリデーションの実行
    ValidatorUtil.validate(form);

    // 業務ロジックを実行する（省略）
}

public class UserSearchForm {
    private String name;
    // 省略
}
```

---

**注意点**

- Jakarta RESTful Web Servicesで規定されている `@PathParam` アノテーションは**使用できない**
- 同様に `@QueryParam` アノテーションも**使用できない**
- `@Path` アノテーション方式は、JBoss/WildFlyなどvfsを使用するアプリケーションサーバでは使用不可。その場合はXMLルート定義方式を使うこと

参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s4, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9, restful-web-service-resource-signature.json:s1

## 参照ナレッジ

- [パスパラメータを扱う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-resource-signature.md#パスパラメータを扱う) (s2)
- [クエリーパラメータを扱う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-resource-signature.md#クエリーパラメータを扱う) (s3)
- [ディスパッチハンドラを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#ディスパッチハンドラを設定する) (s3)
- [ルート定義ファイルを作成する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#ルート定義ファイルを作成する) (s4)
- [ディスパッチハンドラを変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#ディスパッチハンドラを変更する) (s7)
- [マッピングの実装方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#マッピングの実装方法) (s8)
- [パスパラメータの定義](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md#パスパラメータの定義) (s9)
- [リソースクラスのメソッドのシグネチャ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-resource-signature.md#リソースクラスのメソッドのシグネチャ) (s1)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The actual output covers both expected facts comprehensively. It explicitly explains that path parameters are defined in routing configuration (both XML routes.xml with ':paramName' notation and @Path annotation with '{paramName}' notation) and received in resource classes via JaxRsHttpRequest.getPathParam(). It also explicitly covers that query parameters are obtained from JaxRsHttpRequest using getParamMap(). Both key facts from the expected output are fully addressed with detailed code examples and explanations. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about REST API implementation, covering URL path parameters, query parameters, and routing configuration with no irrelevant statements. Great job! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「パスパラメータはルーティング設定で名前を定義しリソースクラスで受け取る」は回答の「routes.xmlで`:id`を定義し`getPathParam("id")`で取得」および「`@Path("/foo/{param}")`で定義し`getPathParam("param")`で取得」に含まれている。参照事実「クエリーパラメータはJaxRsHttpRequestから取得する」は回答の「`JaxRsHttpRequest`を引数に定義し、`getParamMap()`で取得後、`BeanUtil.createAndCopy`でFormクラスにマッピング」に含まれている。 |
| answer_relevancy | NG | 回答末尾に「参照: restful-web-service-resource-signature.json:s2, restful-web-service-resource-signature.json:s3, adapters-router-adaptor.json:s3, adapters-router-adaptor.json:s4, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, adapters-router-adaptor.json:s9, restful-web-service-resource-signature.json:s1」という内部参照記法がユーザー向け回答に含まれており不適切。 |
| faithfulness | OK | ナレッジ内容と矛盾なし。`@PathParam`・`@QueryParam`不使用の注意、JBoss/WildFlyでの`@Path`方式不可、`getPathParam()`によるパスパラメータ取得、`getParamMap()`によるクエリーパラメータ取得、いずれもナレッジ（restful-web-service-resource-signature.md・adapters-router-adaptor.md）の記述と一致している。 |

### 参照事実（expected_facts）

- パスパラメータはルーティング設定で名前を定義しリソースクラスで受け取る
- クエリーパラメータはJaxRsHttpRequestから取得する
