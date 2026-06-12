**結論**: NablarchのRESTfulウェブサービスでJSON受信→DB登録を行うには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドを定義し、`BodyConvertHandler` がJSONをFormに変換、`JaxRsBeanValidationHandler` がバリデーションを行い、アクション内で `UniversalDao.insert()` でDBに登録する流れになる。

---

**根拠**:

**全体の処理の流れ（ハンドラキュー順）**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込みとエラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクションのコミット・ロールバック |
| 5 | ルーティングアダプタ | URIに対応するアクションメソッドを決定 |
| 6 | **BodyConvertHandler** | リクエストボディ（JSON）をFormクラスに変換 |
| 7 | **JaxRsBeanValidationHandler** | Formクラスのバリデーション実行 |

`BodyConvertHandler` は、アクションメソッドの `@Consumes` アノテーションで指定されたMIMEタイプに対応した `BodyConverter` を使ってJSONをFormに変換する。

**Formクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

- プロパティは**全てString型**で宣言する（バリデーションルールの設定方法の要件）

**アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)` : リクエストをJSON形式で受け付ける指定。`BodyConvertHandler` はこのアノテーションを参照してJSON→Form変換を行う
- `@Valid` : `JaxRsBeanValidationHandler` がこのアノテーションを見てバリデーションを実行する
- `BeanUtil.createAndCopy()` : FormをEntityに変換
- `UniversalDao.insert()` : EntityをDBに登録
- ステータスコード `201`（Created）を返却

**BodyConvertHandlerの設定例（コンポーネント定義）**

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
      <component class="nablarch.fw.jaxrs.FormUrlEncodedConverter" />
    </list>
  </property>
</component>
```

JSON対応のConverterを `bodyConverters` に追加することでJSON受信が有効になる。対応していないMIMEタイプが指定された場合はステータスコード `415` を返却する。

---

**注意点**:
- `@Path` と `@POST` アノテーションはルーティングアダプタの「Jakarta RESTful Web ServicesのPathアノテーションでマッピングする」機能を使って設定する
- RESTfulウェブサービスではETagやIf-Matchを使った楽観的ロックには対応していない。楽観的ロックを使う場合はリクエストボディにバージョン番号を含める

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4