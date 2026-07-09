**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションクラスに `@POST` / `@Consumes(MediaType.APPLICATION_JSON)` / `@Valid` アノテーションを付け、`UniversalDao.insert()` でDB登録する。ハンドラキューには `BodyConvertHandler`（Jacksonコンバータ付き）と `JaxRsBeanValidationHandler` が必要。

---

**根拠**:

### 全体の処理の流れ

1. リクエストを受信したWebフロントコントローラがハンドラキューに処理を委譲
2. `RoutesMapping`（ルーティングアダプタ）がURLからアクションクラスを特定
3. `BodyConvertHandler` がリクエストボディ（JSON）をFormクラスに変換
4. `JaxRsBeanValidationHandler` がFormに対してBean Validationを実行
5. アクションクラスが `UniversalDao.insert()` でDB登録し、201レスポンスを返す

### 最小ハンドラ構成

| No | ハンドラ | 役割 |
|----|---------|-----|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み・エラー処理 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ（RoutesMapping） | URLとアクションの紐付け |
| 6 | リクエストボディ変換ハンドラ（BodyConvertHandler） | JSONボディ→Formクラスへの変換 |
| 7 | Bean Validationハンドラ | Formのバリデーション |

### JSONコンバータの設定（Jersey/Jackson使用）

JerseyアダプタはJSONコンバータ（`Jackson2BodyConverter`）を自動的に設定する：

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyアダプタがJackson2BodyConverter等を自動設定 -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
  ...
</component>
```

### アクションクラスの実装例（URLマッピング含む）

```java
@Path("/projects")        // URLマッピング
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)   // JSON受信を宣言
    @Valid                                   // Bean Validationを実行
    public HttpResponse save(ProjectForm project) {
        // BeanUtilでFormをEntityに変換し、UniversalDaoでDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode()); // 201
    }
}
```

### フォームクラスの作成ポイント

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;   // プロパティは全てString型で宣言する
    // getter/setter省略
}
```

**注意点**:
- `@Valid` が付いたメソッドのFormに対してのみバリデーションが実行される（`JaxRsBeanValidationHandler` が処理）
- `BodyConvertHandler` はルーティングアダプタより後ろに設定する必要がある
- `UniversalDao` を使用するには、コンポーネント定義に `BasicDaoContextFactory` を追加する必要がある

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

参照:
- 登録機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-getting-started-create.md
  プロジェクト情報を登録する
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/restful-web-service/restful-web-service-architecture.md
  RESTfulウェブサービスの処理の流れ
  最小ハンドラ構成
- リクエストボディ変換ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-body-convert-handler.md
  変換処理を行うコンバータを設定する
  リクエストボディをFormに変換する
- Jakarta RESTful Web Servcies Bean Validationハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-jaxrs-bean-validation-handler.md
  リソース(アクション)で受け取るForm(Bean)に対してバリデーションを実行する
- Jakarta RESTful Web Servicesアダプタ
  .claude/skills/nabledge-6/docs/component/adapters/adapters-jaxrs-adaptor.md
  Jersey環境下でRESTfulウェブサービスを使用する
- ルーティングアダプタ
  .claude/skills/nabledge-6/docs/component/adapters/adapters-router-adaptor.md
  マッピングの実装方法
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  ユニバーサルDAOを使うための設定を行う