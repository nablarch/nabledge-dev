**結論**: RESTfulウェブサービスでJSON受信・DB登録を行うには、リソースクラスに `@Path` + `@POST` + `@Consumes(MediaType.APPLICATION_JSON)` を設定し、受け取ったフォームを `BeanUtil.createAndCopy()` でエンティティに変換して `UniversalDao.insert()` で登録する。

**根拠**:

**1. フォームクラスを作成する**

クライアントから送信されたJSONを受け付けるフォームを作成する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラスの実装**

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

各アノテーション・メソッドの役割:

| 要素 | 役割 |
|---|---|
| `@Path("/projects")` | リソースクラスとパス `/projects` を紐づける |
| `@POST` | POSTリクエスト時にこのメソッドを呼び出す |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSON形式で受け付ける（リクエストボディ変換ハンドラがJSONをフォームに変換） |
| `@Valid` | Bean Validationを実行する（エラー時は `ApplicationException` が送出される） |
| `BeanUtil.createAndCopy()` | フォームをエンティティクラスに変換する |
| `UniversalDao.insert()` | エンティティをDBに登録する |
| `HttpResponse.Status.CREATED` | 登録成功を示すステータスコード `201` を返す |

**3. BodyConvertHandlerの設定（application/json対応）**

ハンドラキューに `BodyConvertHandler` を設定し、`bodyConverters` プロパティにJSON用のコンバータを含める必要がある。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/json対応のコンバータを設定 -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
    </list>
  </property>
</component>
```

**注意点**:
- フォームのプロパティは全て `String` 型で宣言する（型変換はエンティティコピー時に行われる）
- `@Consumes` に設定したMIMEと異なる `Content-Type` がリクエストヘッダに設定されていた場合、ステータスコード `415` が返却される
- `JaxRsBeanValidationHandler` はリクエストボディ変換ハンドラよりも後ろに設定する必要がある

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8