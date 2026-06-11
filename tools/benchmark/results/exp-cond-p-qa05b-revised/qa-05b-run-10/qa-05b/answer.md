**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`を付与し、`BeanUtil.createAndCopy()`でフォームをエンティティに変換後、`UniversalDao.insert()`でDBに登録する。フレームワークが「JSON→Form変換 → バリデーション → アクション実行 → トランザクションコミット」という流れを自動で処理する。

---

**根拠**:

### 処理の流れ

リクエストはWebFrontControllerが受信し、以下のハンドラキューを通過してアクションに到達する。

| No. | ハンドラ | 主な役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外ログ出力 |
| 2 | JaxRsResponseHandler | レスポンス書き込み・エラー時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | `@Path`/`@POST`を元に呼び出すアクションを決定 |
| 6 | **BodyConvertHandler** | **JSONリクエストボディをFormクラスに変換** |
| 7 | **JaxRsBeanValidationHandler** | **`@Valid`によりFormのバリデーションを実行** |

JSONを受け取るポイントは**BodyConvertHandler**（No.6）。アクションメソッドに設定した`@Consumes(MediaType.APPLICATION_JSON)`を見て、対応するBodyConverterがリクエストボディをFormオブジェクトに変換する。変換されたFormはNo.7でBean Validationにかけられ、エラーがあれば`ApplicationException`を送出してアクションには渡らない。

### 実装例

**Formクラス**（受け取るJSONのフィールドをプロパティに対応させる）:
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

**仕組みのポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` — BodyConvertHandlerに「このメソッドはJSONを受け取る」と伝える
- `@Valid` — JaxRsBeanValidationHandlerにバリデーション対象であることを伝える
- `BeanUtil.createAndCopy(Project.class, project)` — FormからエンティティへのBeanコピー
- `UniversalDao.insert(...)` — エンティティをDBに登録（INSERT）
- `HttpResponse(201)` — リソース作成完了を示すステータスコードで返却

**BodyConvertHandlerの設定例**（application/json対応のコンバータを追加する場合）:
```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
      <component class="nablarch.fw.jaxrs.FormUrlEncodedConverter" />
      <!-- JSON用コンバータをここに追加 -->
    </list>
  </property>
</component>
```

**注意点**:
- Formクラスのプロパティは**全てString型**で宣言する（Bean Validationの仕様）
- BodyConvertHandlerに**application/jsonに対応したBodyConverter**が設定されていないと、サポートしていないメディアタイプとしてステータスコード`415`が返却される
- ルーティングアダプタより後ろのハンドラ（BodyConvertHandler、JaxRsBeanValidationHandler）は、ルーティングアダプタに対して設定する

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4