### Answer

NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録する実装手順を説明します。

---

## 1. フォームクラスの作成

クライアントから送信されたJSONを受け付けるフォームクラスを作成します。プロパティは**全てString型**で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ
}
```

---

## 2. アクションクラスの実装

`@Consumes(MediaType.APPLICATION_JSON)` でJSON受付を宣言し、`@Valid` でバリデーションを行います。DBへの登録は `UniversalDao.insert()` を使います。

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

**ポイント：**
- `@Path` + `@POST` でPOSTリクエストのURLマッピングを定義
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換
- 登録成功時はステータスコード `201` を返却

---

## 3. アダプタの設定（コンポーネント設定）

使用するアプリサーバに応じてアダプタを選択します。ブランクプロジェクトには**Jersey用アダプタ**が組み込まれています。

**Jersey環境の場合：**
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

**RESTEasy環境の場合：** `JerseyJaxRsHandlerListFactory` の代わりに `ResteasyJaxRsHandlerListFactory` を使用します。

いずれのアダプタを使用しても、以下のハンドラが自動設定されます：
- **リクエストボディ変換ハンドラ**（JSONコンバータ: `Jackson2BodyConverter`）
- **Jakarta RESTful Web Services Bean Validationハンドラ**

---

## 4. 処理の流れ

1. WebフロントコントローラがリクエストをHTTPで受信
2. ハンドラキューがリクエストを処理（BodyConvertHandlerがJSONをフォームに変換）
3. アクションクラスがバリデーション後にDBへ登録
4. `HttpResponse(201)` をクライアントに返却

---

## 補足

- アプリサーバにJacksonがバンドルされていない場合は、Jacksonモジュールをアプリケーションと一緒にデプロイしてください
- ルーティングアダプタを使ったURLマッピングには `@Path` アノテーションを使用します