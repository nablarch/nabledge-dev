これで必要な情報が揃いました。回答を生成します。

Step 5: 回答の生成と Step 6: 検証を行います。

---

## RESTfulウェブサービスでのDB登録実装パターン

**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、Formクラスを作成し、アクションメソッドに `@Consumes`・`@Valid`・`@POST` アノテーションを付与して、`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` で登録する。

---

**根拠**:

### 1. Formクラスの作成

クライアントから受け取る値を保持するFormクラスを作成する。**プロパティは全てString型で宣言**すること。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

### 2. 業務アクションメソッドの実装

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

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディをJSONとして受け付ける指定。リクエストボディ変換ハンドラ（`BodyConvertHandler`）がこのアノテーションを元にFormへの変換処理を行う
- `@Valid`: Bean Validationハンドラ（`JaxRsBeanValidationHandler`）がFormに対してバリデーションを実行する。バリデーションエラー時は `ApplicationException` が送出され、後続処理は実行されない
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する
- `UniversalDao.insert(...)`: Entityをデータベースに登録する
- 戻り値: `201 Created` を表す `HttpResponse` を返す

### 3. BodyConvertHandlerの設定（コンポーネント定義）

JSONをサポートするには、`BodyConvertHandler` に対応する `BodyConverter` を設定する。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- JSON用コンバータ等をプロジェクトに応じて設定 -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
      <component class="nablarch.fw.jaxrs.FormUrlEncodedConverter" />
    </list>
  </property>
</component>
```

---

**注意点**:

- Formのプロパティは全てString型で宣言すること（Bean Validationのバリデーションルール設定の制約）
- `BeanUtil.createAndCopy` でFormをEntityに変換する際、型変換が行われる。不正な値がシステムに取り込まれないよう、`@Valid` によるバリデーションを事前に実施すること
- `BodyConvertHandler` は `ルーティングアダプタ` より後ろに、`JaxRsBeanValidationHandler` は `BodyConvertHandler` より後ろに設定すること

---

参照:
- `restful-web-service-getting-started-create.json:s1`
- `handlers-body-convert-handler.json:s4`
- `handlers-body-convert-handler.json:s5`
- `handlers-jaxrs-bean-validation-handler.json:s4`

---