`read_sections` として記録:
- `restful-web-service-getting-started-create.json:s1`
- `restful-web-service-resource-signature.json:s1`
- `handlers-body-convert-handler.json:s5`
- `handlers-jaxrs-bean-validation-handler.json:s4`
- `adapters-router-adaptor.json:s8`
- `adapters-router-adaptor.json:s6`
- `adapters-router-adaptor.json:s7`

**Step 5: 回答生成**

全セクションを読みました。回答を生成します。

**結論**: RESTfulウェブサービスでJSONを受け取りDBに登録するには、`@Path`/`@POST`/`@Consumes(MediaType.APPLICATION_JSON)`/`@Valid` アノテーションを組み合わせたリソースクラスメソッドを実装し、`BeanUtil.createAndCopy` でFormをEntityに変換して `UniversalDao.insert` で登録する。

**Step 6: Verify**

回答に含まれるNablarch固有クレームを検証します。

- `@Consumes(MediaType.APPLICATION_JSON)` → s1, s5で確認済み ✅
- `@Valid` アノテーション → s1, s4で確認済み ✅
- `UniversalDao.insert` → s1で確認済み ✅
- `BeanUtil.createAndCopy` → s1で確認済み ✅
- `HttpResponse.Status.CREATED.getStatusCode()` (201) → s1で確認済み ✅
- `@Path`, `@POST` → s1, s8で確認済み ✅
- `JaxRsHttpRequest` → s1で確認済み ✅
- `PathOptionsProviderRoutesMapping` → s7で確認済み ✅

verify_result = PASS

---

**結論**: `@Path`/`@POST`/`@Consumes(MediaType.APPLICATION_JSON)`/`@Valid` アノテーションを持つリソースクラスのメソッドを実装し、`BeanUtil.createAndCopy` でFormをEntityに変換して `UniversalDao.insert` でDBに登録する。登録成功時はステータスコード `201 Created` の `HttpResponse` を返す。

**根拠**:

### 1. Formクラスの作成

リクエストボディ（JSON）を受け取るFormクラスを作成する。プロパティは**全てString型**で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

### 2. リソースクラス（アクションクラス）の実装

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

**実装のポイント:**
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付ける。リクエストボディ変換ハンドラがこのアノテーションを元にJSONをFormオブジェクトに変換する。
- `@Valid`: このアノテーションを付与することで、Jakarta RESTful Web Services Bean ValidationハンドラがFormに対してBean Validationを自動実行する。
- `BeanUtil.createAndCopy(Project.class, project)`: FormからEntityへ変換する。
- `UniversalDao.insert(...)`: Entityをデータベースに登録する。
- 戻り値に `HttpResponse.Status.CREATED.getStatusCode()`（201）を指定する。

### 3. URLマッピング（ルーティングアダプタ）

`@Path` アノテーションによるマッピングを使用する場合、ディスパッチハンドラとして `PathOptionsProviderRoutesMapping` を設定する。

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

### メソッドシグネチャの選択肢

| 引数定義 | 使用場面 |
|----------|----------|
| フォーム(Java Beans) | リクエストボディから変換したFormで処理する場合 |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータ、HTTPヘッダを取得する場合 |
| 組み合わせ | 複数の情報が必要な場合 |

**注意点**: `@Path` アノテーションによるルーティングは、JBossやWildflyなど一部のウェブアプリケーションサーバ（vfsを使うもの）では使用できない。その場合はXMLによるルート定義ファイルを使用すること。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s6, adapters-router-adaptor.json:s7, adapters-router-adaptor.json:s8

---