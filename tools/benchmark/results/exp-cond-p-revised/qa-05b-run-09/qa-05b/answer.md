**結論**: アクションクラスに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、受け取ったフォームを `BeanUtil.createAndCopy()` でエンティティに変換後、`UniversalDao.insert()` でDBに登録する。ステータスコード `201` の `HttpResponse` を返す。

**根拠**:

リクエストが来てからDB登録されるまでの仕組みは次の流れになる。

1. **リクエストの変換** — `BodyConvertHandler`（リクエストボディ変換ハンドラ）が `Content-Type: application/json` のリクエストボディをアクションメソッドの引数型（フォームクラス）に変換する。変換に使うコンバータは `bodyConverters` プロパティで設定する。
2. **バリデーション** — `JaxRsBeanValidationHandler`（Jakarta RESTful Web Servcies Bean Validationハンドラ）が変換されたフォームに対して Bean Validation を実行する。バリデーションエラー時は `ApplicationException` を送出して処理を終了する。
3. **業務処理** — アクションクラスがフォームをエンティティに変換してDBに登録する。

**アクションクラスの実装例:**

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

**フォームクラスの実装ポイント:**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;  // プロパティは全てString型で宣言する

    // ゲッタ及びセッタ
}
```

**ハンドラの最小構成（BodyConvertHandler の設定例）:**

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/json に対応したコンバータ -->
      <component class="nablarch.fw.jaxrs.Jackson2BodyConverter" />
    </list>
  </property>
</component>
```

**ユニバーサルDAO の設定（コンポーネント定義に追加）:**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームクラスのプロパティは **全てString型** で宣言すること。
- `@Valid` アノテーションを付けないとバリデーションが実行されない。
- `Consumes` に設定したMIMEとリクエストの `Content-Type` が一致しない場合、ステータスコード `415` が返却される。
- `BodyConvertHandler` と `JaxRsBeanValidationHandler` はルーティングアダプタより **後ろ** に設定すること（Jakarta RESTful Web Servicesアダプタを使うと自動設定される）。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6