**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Path`・`@POST`・`@Consumes(APPLICATION_JSON)`・`@Valid` を付けたリソースクラスのメソッドを実装し、`BeanUtil.createAndCopy` でフォームをエンティティに変換して `UniversalDao.insert` を呼び出す。

---

**根拠**:

### 1. フォームクラスの作成

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

### 2. リソースクラスの実装

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
- `@Path("/projects")` + `@POST` でURLとメソッドをマッピング
- `@Consumes(MediaType.APPLICATION_JSON)` で、リクエストボディをフォームクラスに変換するフォーマットをJSON指定
- `@Valid` でリクエストのバリデーションを実行
- `BeanUtil.createAndCopy` でフォームをエンティティに変換し、`UniversalDao.insert` でDB登録
- 戻り値としてリソース作成完了（ステータスコード `201`）を表す `HttpResponse` を返却

### 3. ルーティング設定（@Path アノテーション方式）

`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定し、`JaxRsPathOptionsProvider` で `applicationPath`（パス共通プレフィックス）と `basePackage`（@Pathアノテーションを検索するルートパッケージ）を指定する。

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

### 4. ハンドラ設定（最小構成）

| No. | ハンドラ | 役割 |
|---|---|---|
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | リクエストURIとアクションを紐付けるハンドラ | URLからアクションを特定 |
| 6 | リクエストボディ変換ハンドラ | JSONをフォームクラスに変換 |
| 7 | JaxRs Bean Validationハンドラ | @Valid によるバリデーション実行 |

Jersey アダプタ（`JerseyJaxRsHandlerListFactory`）を使用すると、No.6・No.7 が自動設定され、JSONコンバータには `Jackson2BodyConverter` が使用される。

---

**注意点**:
- フォームのプロパティは必ず `String` 型で宣言すること。`String` 以外の型を使うと、不正な値が入力された際にバリデーション実行前の変換処理が失敗し予期せぬ例外が発生する。
- `@Path` アノテーション方式は、JBoss/Wildfly など vfs でクラスパスを管理しているサーバでは使用できない。その場合はXMLによるルーティング定義を使用すること。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2, adapters-router-adaptor.json:s6, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8, libraries-bean-validation.json:s8