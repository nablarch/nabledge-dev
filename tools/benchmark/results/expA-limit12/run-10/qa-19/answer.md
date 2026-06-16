**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付け、`BodyConvertHandler`がJSONをFormに自動変換した後、`BeanUtil.createAndCopy()`でEntityに変換して`UniversalDao.insert()`でDBに保存します。

**根拠**:

**① アクションクラスの実装例**

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
- `@Consumes(MediaType.APPLICATION_JSON)` を指定してJSONリクエストを受け付ける
- `@Valid` でBean Validationを実行する
- `BeanUtil.createAndCopy()` でFormをEntityに変換する
- `UniversalDao.insert()` でDBに登録する
- 戻り値としてステータスコード `201`（リソース作成完了）の`HttpResponse`を返却する

**② フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

フォームのプロパティは全て`String`型で宣言する。

**③ ハンドラキューの仕組み（処理の流れ）**

| No. | ハンドラ | 役割 |
|-----|--------|------|
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット |
| 5 | ルーティングアダプタ | URLとアクションのマッピング |
| 6 | **リクエストボディ変換ハンドラ** | **JSONをFormに変換** |
| 7 | Bean Validationハンドラ | Formのバリデーション実行 |

**④ JSON変換の設定（BodyConvertHandlerのコンバータ設定）**

Jersey環境では、`JerseyJaxRsHandlerListFactory`を使用すると`Jackson2BodyConverter`が自動的に設定される。手動設定の場合は以下のように`bodyConverters`にコンバータを設定する:

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/jsonに対応したJSONコンバータ -->
      <component class="nablarch.integration.jaxrs.jackson.Jackson2BodyConverter" />
    </list>
  </property>
</component>
```

`@Consumes`に指定したMIMEタイプと一致するコンバータが選択される。サポートしていないMIMEの場合はステータスコード`415`が返却される。

**注意点**:
- `BodyConvertHandler`は`ルーティングアダプタ`よりも**後ろ**に設定すること（アクションクラスのアノテーション情報が必要なため）
- `JerseyJaxRsHandlerListFactory`を使用した場合、`BodyConvertHandler`と`JaxRsBeanValidationHandler`が自動的にハンドラキューに追加される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2