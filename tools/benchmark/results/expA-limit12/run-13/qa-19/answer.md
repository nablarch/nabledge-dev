**結論**: REST APIでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` を付けたアクションメソッドでFormクラスを受け取り、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDBに登録します。リクエストボディのJSON→Form変換はフレームワーク（`BodyConvertHandler` + `Jackson2BodyConverter`）が自動的に行います。

---

**根拠**:

#### 処理の流れ

1. Webフロントコントローラがリクエストを受信し、ハンドラキューに委譲
2. **リクエストボディ変換ハンドラ**（`BodyConvertHandler`）がJSONボディをアクションのFormクラスに変換
3. **Bean Validationハンドラ**がFormに対してバリデーションを実行
4. アクションクラスが業務ロジックを実行し、`HttpResponse` を返却

#### アクションクラスの実装例

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm form) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付けることを宣言
- `@Valid` でBean Validationを有効化
- `BeanUtil.createAndCopy(Project.class, form)` でFormをEntityに変換
- `UniversalDao.insert()` でDB登録
- ステータスコード `201 Created` を返却

#### Formクラスの作成

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ
}
```

- **Formのプロパティは全てString型**で宣言すること

#### ハンドラ構成（最小構成）

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンスの書き込み |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | リクエストボディ変換ハンドラ | JSONボディ → Formへの変換 |
| 7 | Bean Validationハンドラ | Formのバリデーション |

#### JSON変換コンバータの設定（Jersey環境の場合）

Jersey環境では `JerseyJaxRsHandlerListFactory` を使用すると、`Jackson2BodyConverter`（JSON変換）が自動的に設定されます：

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

---

**注意点**:
- JSON変換には `nablarch-jackson-adaptor` モジュールと `nablarch-jersey-adaptor`（または `nablarch-resteasy-adaptor`）の依存関係が必要
- リクエストの `Content-Type` が `@Consumes` と一致しない場合、ステータスコード `415 Unsupported Media Type` が返却される
- `UniversalDao` を使用するには、`BasicDaoContextFactory` のコンポーネント定義が別途必要

参照: processing-pattern/restful-web-service/restful-web-service-getting-started-create.json:s1, processing-pattern/restful-web-service/restful-web-service-architecture.json:s2, processing-pattern/restful-web-service/restful-web-service-architecture.json:s4, component/handlers/handlers-body-convert-handler.json:s5, component/adapters/adapters-jaxrs-adaptor.json:s2