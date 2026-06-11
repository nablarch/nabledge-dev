**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、①リクエストボディ変換ハンドラ（BodyConvertHandler）がJSONをフォームクラスに変換し、②Bean Validationで入力チェックを行い、③アクションクラスでUniversalDao.insert()によってDBに登録する、という流れで実装する。

---

**根拠**:

### 処理の流れ

1. クライアントからのJSONリクエストをWebFrontControllerが受信し、ハンドラキューに委譲する
2. **BodyConvertHandlerが`@Consumes`アノテーションのMIMEタイプに基づいてリクエストボディをフォームクラスに変換する**（JSON変換にはJackson2BodyConverterが使用される）
3. JaxRsBeanValidationHandlerが変換されたフォームに対してバリデーションを実行する
4. アクションクラスが業務ロジック（DB登録）を実行し、HttpResponseを返却する

### 最小ハンドラ構成

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションへのマッピング |
| 6 | リクエストボディ変換ハンドラ | JSONボディ→フォームクラスへの変換 |
| 7 | Bean Validationハンドラ | フォームクラスへのバリデーション実行 |

### 実装例

**フォームクラス**（JSONのマッピング先）:
```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**アクションクラス**:
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

- `@Path`と`@POST`でURLとHTTPメソッドのマッピングを定義する
- `@Consumes(MediaType.APPLICATION_JSON)`でJSON形式のリクエストを受け付けることを指定する
- `@Valid`でBean Validationを有効にする
- `BeanUtil.createAndCopy()`でフォームからエンティティに変換し、`UniversalDao.insert()`でDB登録する
- 戻り値はステータスコード`201`（リソース作成完了）を表すHttpResponseを返す

### BodyConvertHandlerの設定例（Jersey環境）

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyJaxRsHandlerListFactoryにより自動的にJackson2BodyConverter等が設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

---

**注意点**:
- フォームクラスのプロパティは**すべてString型**で宣言すること（バリデーションルールの設計上の制約）
- `JerseyJaxRsHandlerListFactory`を使うと、BodyConvertHandlerとBean ValidationハンドラがJSON（Jackson）・XML・フォームURLエンコードに対応した状態で自動設定される

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2, processing-pattern/restful-web-service/restful-web-service-application-design.json:s1