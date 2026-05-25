Step 5〜7: 回答を生成し、検証します。

**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、Form クラスを定義してアクションメソッドで `@Consumes`・`@Valid` を付加し、`BeanUtil.createAndCopy` でエンティティに変換したうえで `UniversalDao.insert` を呼び出す。

**根拠**:

**① Form クラスの作成**

クライアントから受け取る値を格納する Form クラスを定義する。プロパティは必ずすべて `String` 型で宣言する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② アクションクラスの実装（URLマッピング込み）**

`@Path` でURLパスを、`@POST` でHTTPメソッドをマッピングする。メソッドには `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付加し、`BeanUtil.createAndCopy` でエンティティに変換してから `UniversalDao.insert` でDB登録する。

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

- `@Consumes(MediaType.APPLICATION_JSON)` を指定することで、リクエストボディ変換ハンドラが `application/json` として Form クラスへ変換する
- `@Valid` を指定することで、Jakarta RESTful Web Services Bean Validation ハンドラがフォームに対してバリデーションを実行する
- 正常登録時は `201 Created` を返す

**③ ハンドラキューの設定**

最小構成では以下のハンドラが必要。リクエストボディ変換ハンドラ（BodyConvertHandler）と Bean Validation ハンドラはルーティングアダプタ（RoutesMapping）配下に設定する。

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <list>
          <component class="nablarch.fw.jaxrs.BodyConvertHandler">
            <property name="bodyConverters">
              <list>
                <!-- JSON対応コンバータ等を設定 -->
              </list>
            </property>
          </component>
          <component class="nablarch.fw.jaxrs.JaxRsBeanValidationHandler" />
        </list>
      </property>
    </component>
  </property>
</component>
```

> なお、`JaxRsAdaptor`（Jakarta RESTful Web Services アダプタ）を使用する場合は、BodyConvertHandler と Bean Validation ハンドラが自動的に追加される。

**注意点**:

- Form のプロパティは**必ずすべて `String` 型**で定義すること。`String` 以外の型を使用すると、不正な入力値がきた場合にバリデーション前の Bean 変換処理で例外が発生し障害になる
- RESTfulウェブサービスでは ETag / If-Match を使った楽観的ロックは**サポートされていない**。楽観的ロックが必要な場合は、リクエストボディにバージョン番号を直接含める設計にすること

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, libraries-bean-validation.json:s8, adapters-router-adaptor.json:s8, restful-web-service-feature-details.json:s4

---