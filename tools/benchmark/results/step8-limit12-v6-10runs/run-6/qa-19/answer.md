**結論**: `BodyConvertHandler`がリクエストのJSONをFormクラスへ自動変換し、アクションメソッドで受け取ったFormを`BeanUtil.createAndCopy()`でEntityに変換後、`UniversalDao.insert()`でDBに登録する。

---

**根拠**:

#### 処理の流れ

リクエスト受信からDB登録までの流れは以下のとおり：

1. `WebFrontController`がHTTPリクエストを受信
2. `RoutesMapping`（ルーティングアダプタ）がURIをもとに呼び出すアクションを決定
3. **`BodyConvertHandler`** がリクエストボディ（JSON）をアクションの引数となるFormクラスへ変換
4. **`JaxRsBeanValidationHandler`** がFormに対してBean Validationを実行
5. アクションメソッドがFormを受け取り、DB登録処理を実行
6. `JaxRsResponseHandler`がレスポンスを返却

#### 最小ハンドラ構成（コンポーネント定義）

```xml
<!-- リクエストURIとアクションを紐付けるハンドラ -->
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <!-- Jersey用アダプタを使うと下記が自動設定される -->
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

Jersey用アダプタ（`JerseyJaxRsHandlerListFactory`）を使用すると、`BodyConvertHandler`に以下のコンバータが自動設定される：
- JSON: `Jackson2BodyConverter`
- XML: `JaxbBodyConverter`
- form-urlencoded: `FormUrlEncodedConverter`

#### Formクラスの作成

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

プロパティは全てString型で宣言する。

#### アクションメソッドの実装

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

ポイント：
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを宣言する。`BodyConvertHandler`はこのアノテーションを参照してJSONコンバータを選択する
- `@Valid` を付けることで`JaxRsBeanValidationHandler`がFormのBean Validationを実行する。バリデーションエラー時は`ApplicationException`が送出され、後続処理は行われない
- `BeanUtil.createAndCopy(Project.class, project)` でFormからEntityに変換し、`UniversalDao.insert()`でDB登録
- 戻り値は`HttpResponse(201)`（リソース作成完了）

---

**注意点**:
- `@Consumes`に設定したMIMEとリクエストの`Content-Type`が異なる場合、ステータスコード`415`（Unsupported Media Type）が返却される
- `BodyConvertHandler`は必ず`RoutesMapping`より後ろのハンドラキューに設定すること（アクションのアノテーション情報を参照するため）

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, handlers-jaxrs-bean-validation-handler.json:s4, adapters-jaxrs-adaptor.json:s2