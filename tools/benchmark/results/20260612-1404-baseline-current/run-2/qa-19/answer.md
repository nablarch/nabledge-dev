**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録する処理は、`BodyConvertHandler`がリクエストボディをFormに変換し、アクションメソッドで`UniversalDao.insert()`を呼び出すことで実現します。

**根拠**:

**処理の流れ（仕組み）**

リクエスト受信からDB登録までの流れは以下のとおりです。

1. `WebFrontController`（`jakarta.servlet.Filter`の実装クラス）がリクエストを受信し、ハンドラキューに委譲する
2. ルーティングアダプタ（`DispatchHandler`）がURIを元にアクションクラスを特定する
3. **`BodyConvertHandler`** がリクエストボディをアクションメソッドが受け取るFormクラスに変換する
4. **`JaxRsBeanValidationHandler`** が`@Valid`アノテーションのあるメソッドのFormに対してバリデーションを実行する
5. アクションメソッドがFormをエンティティに変換し、`UniversalDao.insert()`でDBに登録する
6. `JaxRsResponseHandler`がレスポンスをクライアントに返す

**必要な最小ハンドラ構成**

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseハンドラ | レスポンスの書き込み・エラーレスポンス生成 |
| 3 | DB接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | コミット・ロールバック |
| 5 | ルーティングアダプタ | URIとアクションのマッピング |
| 6 | **BodyConvertHandler** | リクエストボディ⇔Formの変換 |
| 7 | **JaxRsBeanValidationHandler** | Formのバリデーション実行 |

**`BodyConvertHandler`の仕組み**

アクションメソッドの`@Consumes`アノテーションで指定したMIMEタイプに対応した`BodyConverter`を使ってJSON→Formの変換を行います。Content-TypeがConsumesと一致しない場合は`415`を返します。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/json対応のコンバータ（Jacksonアダプタ等） -->
    </list>
  </property>
</component>
```

**アクションクラスの実装例**

```java
@Path("/projects")
public class ProjectAction {

  @POST
  @Consumes(MediaType.APPLICATION_JSON)
  @Valid
  public HttpResponse save(ProjectForm project) {
      // BeanUtilでFormをEntityに変換してDBに登録
      UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
      // ステータスコード201（作成完了）を返す
      return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
  }
}
```

**Formクラスの実装上の注意**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する
    // getter/setter省略
}
```

**注意点**:
- FormのプロパティはすべてString型で宣言する（Bean Validationの制約）
- `@Valid`アノテーションをメソッドに付けることで`JaxRsBeanValidationHandler`がバリデーションを実行する。バリデーションエラー時は`ApplicationException`が送出され、後続処理は実行されない
- DB登録にはFormをそのまま使わず、`BeanUtil.createAndCopy()`でEntityに変換してから`UniversalDao.insert()`に渡す

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4