**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@POST` + `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーションを付けたアクションメソッドを作成し、`BeanUtil.createAndCopy` でフォームをエンティティに変換して `UniversalDao.insert` を呼び出す形で実装します。

**根拠**:

**処理の流れ**

リクエストがフレームワークに届いてからDB登録が完了するまでの流れは以下のとおりです。

1. WebFrontController（`jakarta.servlet.Filter`）がリクエストを受信
2. ハンドラキューに処理を委譲
3. ルーティングアダプタがURIをもとにアクションクラスを特定
4. **リクエストボディ変換ハンドラ（BodyConvertHandler）** がJSONボディをフォームクラス（Form）に変換
5. **Bean Validationハンドラ** がフォームに対してバリデーションを実行
6. アクションクラスがDB登録処理を実行
7. **JaxRsResponseHandler** がレスポンスをクライアントに返却

**最小ハンドラ構成**（ハンドラキューの設定例）

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラー対応 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションの開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションのマッピング |
| 6 | BodyConvertHandler | JSONリクエストボディ→Formへの変換 |
| 7 | JaxRsBeanValidationHandler | Formに対するバリデーション実行 |

**実装例**

フォームクラス（プロパティは全て `String` 型で宣言する）:

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

アクションクラス:

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

**BodyConvertHandlerの設定例**（JSON対応コンバータを使用する場合）:

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/json 対応コンバータを設定する -->
    </list>
  </property>
</component>
```

**UniversalDAOの設定**（コンポーネント定義に追加）:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームのプロパティは必ず `String` 型で宣言すること。他の型（`int` など）を使うと、不正な値が送信された際にバリデーション前に例外が発生する
- `@Consumes` に指定したMIMEタイプとリクエストのContent-Typeが一致しない場合、ステータスコード `415`（Unsupported Media Type）が返却される
- DB登録後のレスポンスはステータスコード `201`（Created）を返すのが一般的
- トランザクション制御はフレームワーク（トランザクション制御ハンドラ）が自動的に行う。正常終了でコミット、例外発生でロールバック

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6, libraries-bean-validation.json:s8