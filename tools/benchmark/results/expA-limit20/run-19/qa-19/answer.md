**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`アノテーションを付けたアクションメソッドを実装し、`BeanUtil`でフォームをエンティティに変換して`UniversalDao.insert()`でDBに登録する。URLは`@Path`と`@POST`アノテーションでマッピングする。

---

**根拠**:

#### 全体の処理の流れ

リクエストを受け取ってからDB登録されるまでの流れは以下のとおり。

1. `WebFrontController`（Filterの実装）がリクエストを受信
2. ハンドラキューに処理を委譲
3. ルーティングアダプタ（`DispatchHandler`）がURIを元にアクションクラスを特定
4. **`BodyConvertHandler`** がリクエストボディをアクションのフォームクラスに変換
5. アクションクラスが業務ロジックを実行（DB登録）
6. `JaxRsResponseHandler`がレスポンスを返却

#### 必要なハンドラ構成（最小構成）

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外ログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス生成・書き込み |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | **リクエストボディ変換ハンドラ** | JSONリクエストボディをFormに変換 |
| 7 | Bean Validationハンドラ | バリデーション実行 |

#### JSON変換の仕組み

`BodyConvertHandler`はアクションメソッドの`@Consumes`アノテーションに基づいてリクエストボディをFormに変換する。`Content-Type: application/json`の場合、`Jackson2BodyConverter`が使用される。

Jerseyアダプタを使う場合、`JerseyJaxRsHandlerListFactory`を設定するだけで`Jackson2BodyConverter`を含むコンバータが自動的に設定される:

```xml
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

#### アクションの実装例

**フォームクラス**（JSONのプロパティに対応するクラス）:

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` — JSONリクエストを受け付ける
- `@Valid` — リクエストのバリデーションを実行（`JaxRsBeanValidationHandler`が処理）
- `BeanUtil.createAndCopy()` — フォームからエンティティを生成・コピー
- `UniversalDao.insert()` — エンティティをDBに登録
- ステータスコード`201`（CREATED）を返却

#### ユニバーサルDAOの設定

DB登録にユニバーサルDAOを使う場合、コンポーネント定義に以下を追加する:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

エンティティクラスにはJakarta Persistenceアノテーション（`@Table`、`@Id`、`@Column`など）を付けることで、SQLを書かずに単純な登録（`insert`）、更新（`update`）、削除（`delete`）、主キー検索（`findById`）が行える。

---

**注意点**:
- フォームのプロパティは全て`String`型で宣言する（バリデーションルールの設定方法の要件）
- `Content-Type`が`application/json`以外の場合、ステータスコード`415`（Unsupported Media Type）が返却される
- ユニバーサルDAOは簡易的なO/Rマッパーであり、主キー以外の条件を指定した更新・削除はデータベースアクセス（JDBCラッパー）を使用する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6