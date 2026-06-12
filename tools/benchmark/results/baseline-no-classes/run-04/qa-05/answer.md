**結論**: RESTful Web ServiceでJSONを受け取りDBに登録するには、Formクラスを作成し、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、`BeanUtil.createAndCopy()` でEntityに変換後 `UniversalDao.insert()` で登録します。

**根拠**:

**① Formクラスの作成**

受信するJSONのフィールドに対応したFormクラスを作成します。プロパティは**全てString型**で宣言します。

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

ポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でバリデーションを実行（`JaxRsBeanValidationHandler` が処理）
- `BeanUtil.createAndCopy()` でFormをEntityに変換
- `UniversalDao.insert()` でDBに登録
- 登録完了を示すステータスコード `201` を持つ `HttpResponse` を返却
- `@Path` と `@POST` でURLとHTTPメソッドをマッピング

**③ BodyConvertHandlerの設定**

コンポーネント定義でJSON変換用の `BodyConverter` を設定する必要があります。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- JSON用コンバータをプロジェクトに合わせて設定 -->
    </list>
  </property>
</component>
```

**注意点**:
- `BodyConvertHandler` は `ルーティングアダプタ` よりも後ろのハンドラキューに設定すること
- `Content-Type` が `application/json` でないリクエストが来た場合、ステータスコード `415` が返却される
- RESTfulウェブサービスでは `排他制御` ライブラリ（taglibとの連動前提）は使用できない。楽観的ロックが必要な場合はリクエストボディに直接バージョン番号を含めること

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, component/handlers/handlers-body-convert-handler.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/handlers/handlers-jaxrs-bean-validation-handler.json:s4, component/adapters/adapters-router-adaptor.json:s8