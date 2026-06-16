**結論**: REST APIでJSONを受け取ってDBに登録するには、アクションクラスに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたメソッドを実装し、`BeanUtil.createAndCopy` でフォームをエンティティに変換した後、`UniversalDao.insert` でDBに登録する。

**根拠**:

処理の流れは以下のとおり。

1. **WebフロントコントローラがリクエストをHTTPリクエスト→ハンドラキューへ委譲**  
2. **リクエストボディ変換ハンドラ (BodyConvertHandler)** がJSON本文をフォームクラスに変換  
3. **Bean Validationハンドラ** がバリデーションを実行  
4. **アクションクラス**が業務ロジックを実行してDBに登録

**フォームクラスの実装**:

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタは省略
}
```

**アクションクラスの実装**:

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

- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける旨を指定する
- `@Valid` でBean Validationによるバリデーションを有効にする
- `BeanUtil.createAndCopy` でフォームをエンティティに変換し、`UniversalDao.insert` でDBに登録する
- 戻り値としてステータスコード `201`（Created）を返却する
- URLマッピングは `@Path` と `@POST` アノテーションで定義する

**ハンドラ設定（JSON変換の設定）**:

Jersey環境の場合、`JerseyJaxRsHandlerListFactory` を使用すると `Jackson2BodyConverter` (JSON用) が自動的に設定される:

```xml
<component name="packageMapping" class="nablarch.integration.router.RoutesMapping">
  <property name="methodBinderFactory">
    <component class="nablarch.fw.jaxrs.JaxRsMethodBinderFactory">
      <property name="handlerList">
        <component class="nablarch.integration.jaxrs.jersey.JerseyJaxRsHandlerListFactory"/>
      </property>
    </component>
  </property>
</component>
```

**注意点**:
- フォームクラスのプロパティはすべて `String` 型で宣言すること
- `BodyConvertHandler` はルーティングアダプタより後ろに設定する必要がある
- Content-TypeヘッダがConsumesに設定したMIMEと異なる場合はステータスコード `415` が返却される

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, adapters-jaxrs-adaptor.json:s2, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5