**結論**: NablarchのRESTfulウェブサービスでは、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けることで、リクエストボディのJSONが自動的にFormクラスに変換・バリデーションされ、`UniversalDao.insert()` でDBに登録できる。

**根拠**:

#### 全体の処理の流れ

リクエストがDBに登録されるまでは以下のハンドラキューを通る：

| No. | ハンドラ | 役割 |
|---|---|---|
| 1-2 | グローバルエラーハンドラ / JaxRsResponseハンドラ | エラー処理・レスポンス書き込み |
| 3-4 | DBConnection管理ハンドラ / トランザクション制御ハンドラ | DB接続・トランザクション管理 |
| 5 | ルーティングアダプタ | URIからアクションクラスを特定 |
| 6 | **リクエストボディ変換ハンドラ** | JSONボディ → Formクラスに変換 |
| 7 | **Bean Validationハンドラ** | Formクラスにバリデーション実行 |

#### JSON → Formへの変換の仕組み

`BodyConvertHandler` が `@Consumes` アノテーションで指定されたMIMEタイプを元に変換処理を行う。`application/json` の場合、Jersey環境では `JerseyJaxRsHandlerListFactory` が自動的に `Jackson2BodyConverter` を設定するため、個別のコンバータ設定は不要。

```java
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse saveJson(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

#### 具体的な実装例（登録機能）

**1. Formクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ・セッタは省略
}
```

プロパティは全て `String` 型で宣言する。

**2. アクションメソッドの実装**

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

ポイント：
- `@Path("/projects")` + `@POST` でURLとHTTPメソッドのマッピングを定義
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを宣言
- `@Valid` でBean Validationを有効化（バリデーションエラー時は `ApplicationException` がスローされ後続処理は実行されない）
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録
- ステータスコード `201`（Created）を返却

**3. UniversalDAOの設定**

コンポーネント定義に `BasicDaoContextFactory` を追加する必要がある：

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `Content-Type: application/json` がリクエストヘッダに設定されていない場合、ステータスコード `415`（Unsupported Media Type）が返却される
- `@Consumes` に設定したMIMEタイプと異なるMIMEがリクエストに設定されていた場合も同様

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, adapters-router-adaptor.json:s8, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6