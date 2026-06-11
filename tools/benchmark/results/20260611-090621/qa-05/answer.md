**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、①Formクラス（全プロパティString型）、②アクションクラス（`@Path`/`@POST`/`@Consumes`/`@Valid`）、③Entityクラス（Jakarta Persistenceアノテーション付き）の3クラスを作成し、`BeanUtil.createAndCopy()`でForm→Entity変換後に`UniversalDao.insert()`でDBに登録する。

---

**根拠**:

**① Formクラスの作成**

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

プロパティは**全てString型**で宣言すること。String以外の型があると、不正な値が送信された際にBeanへの変換処理が失敗し、バリデーション前に例外が送出される。

**② アクションクラスの実装**

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

| アノテーション | 役割 |
|---|---|
| `@Path("/projects")` | クラスをURLパス `/projects` にマッピング |
| `@POST` | POSTリクエストとメソッドを紐づける |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSON形式で受け付ける（異なるContent-Typeが来た場合はステータス415を返す） |
| `@Valid` | `JaxRsBeanValidationHandler` によりFormへのバリデーションを実行する |

`BeanUtil.createAndCopy(Project.class, form)` でFormをEntityに変換し、`UniversalDao.insert()` でDBへ登録する。登録完了時はステータスコード `201` を返す。

**③ Entityクラスの作成**

```java
@Entity
@Table(name = "PROJECT")
public class Project {

    @Id
    @Column(name = "PROJECT_ID")
    private Long projectId;

    @Column(name = "PROJECT_NAME")
    private String projectName;

    // ゲッタ及びセッタ
}
```

`UniversalDao.insert()` を使うには、EntityクラスにJakarta Persistenceアノテーションが必要。使用できる主なアノテーション：`@Entity`（必須）、`@Table`（テーブル名を明示する場合）、`@Id`（主キー）、`@Column`（カラム名を明示する場合）、`@GeneratedValue`（自動採番）。

**④ ハンドラキューの設定（Jersey環境の場合）**

Jersey環境では`JerseyJaxRsHandlerListFactory`を使うことで、JSONコンバータ（`Jackson2BodyConverter`）と`JaxRsBeanValidationHandler`が自動設定される：

```xml
<component name="packageMapping" class="nablarch.integration.router.PathOptionsProviderRoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
  <!-- ... -->
</component>
```

最小ハンドラキューの構成順序（後段ほど先に処理）:
1. グローバルエラーハンドラ
2. JaxRsResponseHandler（レスポンス書き込み）
3. データベース接続管理ハンドラ
4. トランザクション制御ハンドラ
5. ルーティングアダプタ（ここ以降はmethodBinderFactoryに設定）
6. BodyConvertHandler（JSON→Form変換）
7. JaxRsBeanValidationHandler（@Validによるバリデーション）

---

**注意点**:
- FormクラスのプロパティをString以外の型にすると、不正入力時にバリデーションエラーではなく変換例外が発生する
- `BodyConvertHandler`はルーティングアダプタより後ろに設定する必要がある（アクションメソッドのアノテーション情報に基づいて変換するため）
- RESTfulウェブサービスではETagやIf-Matchを使った楽観的ロックは非対応。楽観的ロックを行う場合はリクエストボディに直接バージョン番号を含めること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, libraries-universal-dao.json:s24, libraries-bean-validation.json:s8, adapters-jaxrs-adaptor.json:s2, adapters-router-adaptor.json:s8