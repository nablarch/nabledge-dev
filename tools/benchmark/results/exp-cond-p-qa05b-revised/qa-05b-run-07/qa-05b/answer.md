**結論**: NablarchのRESTfulウェブサービスでJSONを受け取りDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付けたアクションメソッドを作成し、`BeanUtil.createAndCopy()`でFormをEntityに変換後、`UniversalDao.insert()`で登録する。

---

**根拠**:

**1. 処理の流れ（仕組み）**

リクエストが来ると以下の順で処理される：

1. `WebFrontController`（`jakarta.servlet.Filter`の実装）がリクエストを受信
2. ハンドラキューに処理を委譲
3. ルーティングアダプタがURIをもとに呼び出すアクションを決定
4. `BodyConvertHandler` がリクエストボディ（JSON）をFormクラスに変換
5. `JaxRsBeanValidationHandler` がバリデーションを実行
6. アクションクラスが業務ロジックを実行し `HttpResponse` を返却
7. `JaxRsResponseHandler` がレスポンスをクライアントに返却

**2. 最小ハンドラ構成**

| No. | ハンドラ | 役割 |
|-----|----------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションの紐付け |
| 6 | BodyConvertHandler | リクエストボディ ↔ Formの変換 |
| 7 | JaxRsBeanValidationHandler | バリデーション実行 |

**3. 実装例**

フォームクラス（`ProjectForm.java`）:
```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

アクションクラス（`ProjectAction.java`）:
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

**4. BodyConvertHandlerの設定（JSONコンバータが必要な場合）**

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/jsonに対応したコンバータを設定する -->
      <component class="nablarch.fw.jaxrs.Jackson2BodyConverter" />
    </list>
  </property>
</component>
```

**5. ユニバーサルDAOの設定**

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- フォームのプロパティは**全てString型**で宣言する（バリデーションルールの仕様）
- `@Valid`アノテーションを付けることでリクエストのBean Validationが自動実行される
- `Consumes`に設定されたMIMEとリクエストの`Content-Type`が異なる場合、ステータスコード`415`を返却する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, libraries-universal-dao.json:s6