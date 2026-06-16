**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたフォームクラスを受け取り、`BeanUtil`でエンティティに変換後、`UniversalDao.insert()` でDBに登録します。

**根拠**:

#### 1. 処理の流れ（アーキテクチャ）

リクエストは以下の順でハンドラキューを通過します：

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外ログ出力 |
| 2 | JaxRsResponseHandler | レスポンス生成・書き込み |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | リクエストボディ変換ハンドラ | JSONをFormクラスに変換 |
| 7 | Bean Validationハンドラ | バリデーション実行 |

**リクエストボディ変換ハンドラ**（`BodyConvertHandler`）が、`@Consumes` アノテーションに設定されたMIMEタイプに基づいてJSONをFormクラスに変換します。

#### 2. フォームクラスの作成

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言します。

#### 3. アクションクラスの実装

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSONリクエストを受け付けることを指定
- `@Valid`: Bean Validationハンドラがバリデーションを実行
- `BeanUtil.createAndCopy(Project.class, project)`: FormからEntityへ変換
- `UniversalDao.insert()`: DBへ登録
- 戻り値: ステータスコード`201`（作成完了）を表す`HttpResponse`

#### 4. JSONコンバータの設定

JerseyやRESTEasyを使用している場合は、`JerseyJaxRsHandlerListFactory`（または`ResteasyJaxRsHandlerListFactory`）を使うと、Jacksonを利用したJSONコンバータ（`Jackson2BodyConverter`）が自動的に設定されます。

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

#### 5. ユニバーサルDAOの設定

`UniversalDao`を使うには、コンポーネント定義に以下を追加します：

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `@Consumes`に設定したMIMEと異なるContent-Typeがリクエストに含まれていた場合、ステータスコード`415`（サポートしていないメディアタイプ）が返却されます。
- `@Context`アノテーションを使用したServletリソースのインジェクションやCDIは使用できません（Nablarchウェブアプリケーションベースのため）。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s6