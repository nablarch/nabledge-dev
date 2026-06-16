**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録する処理は、`BodyConvertHandler`がリクエストボディをFormクラスに自動変換し、アクションクラスで`BeanUtil.createAndCopy()`によりEntityに変換後、`UniversalDao.insert()`でDBに登録する構成で実現します。

---

**根拠**:

### 処理の流れ

1. `WebFrontController`(jakarta.servlet.Filter実装)がリクエストを受信
2. ハンドラキューに処理を委譲
3. ディスパッチハンドラがURIをもとにアクションクラスを特定
4. アクションクラスがFormクラス・Entityクラスを使って業務ロジックを実行
5. `JaxRsResponseHandler`がレスポンスをクライアントに返却

---

### 最小ハンドラ構成

JSON登録処理に必要な最小ハンドラキューの構成：

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 例外のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンスの書き込み・エラー処理 |
| 3 | データベース接続管理ハンドラ | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | リクエストパス→アクション決定 |
| 6 | **リクエストボディ変換ハンドラ** | request bodyをFormクラスに変換 |
| 7 | **Bean Validationハンドラ** | Formクラスのバリデーション実行 |

JerseyまたはRESTEasyアダプタを使用すれば、No.6・7の設定（`Jackson2BodyConverter`含む）が自動的に追加されます：

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- JerseyのJSONコンバータ(Jackson2BodyConverter)とBean Validationが自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

---

### アクションクラスの実装

**Formクラス（バリデーションルール定義）**：

```java
public class ProjectForm implements Serializable {
    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**業務アクションメソッド**：

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)  // JSONリクエストを受け付ける
    @Valid                                  // Formに対してBean Validationを実行
    public HttpResponse save(ProjectForm project) {
        // BeanUtilでFormをEntityに変換し、UniversalDaoでDB登録
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, project));
        // ステータスコード201(Created)を返却
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

**ポイント**：
- `@Consumes(MediaType.APPLICATION_JSON)`：JSON形式のリクエストを受け付けることを宣言。`BodyConvertHandler`がこのアノテーションを元に変換処理を行います
- `@Valid`：`JaxRsBeanValidationHandler`がこのアノテーション付きメソッドのFormに対してバリデーションを実行します。エラーがあれば`ApplicationException`をスローして後続処理に委譲しません
- `BeanUtil.createAndCopy()`：FormのプロパティをEntityにコピー（Formのプロパティは全てString型で宣言）
- `UniversalDao.insert()`：Entityをもとにinsert SQLを自動生成してDB登録

---

**注意点**:
- FormクラスのプロパティはすべてString型で宣言すること（`@Domain`アノテーションによるバリデーション・型変換の仕組み上の制約）
- JSON変換は`BodyConvertHandler`の`bodyConverters`プロパティに設定された`BodyConverter`実装クラスで行われる。Jersey/RESTEasyアダプタ使用時はJSONコンバータとして`Jackson2BodyConverter`が自動設定されます
- `@Consumes`に設定したMIMEと異なるContent-Typeでリクエストされた場合は、ステータスコード`415`が返却されます

参照: restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, adapters-jaxrs-adaptor.json:s2, handlers-jaxrs-bean-validation-handler.json:s4