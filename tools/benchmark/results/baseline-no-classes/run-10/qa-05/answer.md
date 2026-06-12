**結論**: RESTful ウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたリソースメソッドでFormを受け取り、`BeanUtil.createAndCopy()` でエンティティに変換した後、`UniversalDao.insert()` でDBに登録します。

**根拠**:

**1. Formクラスの作成**

クライアントから送信されるJSONを受け付けるFormクラスを作成します。プロパティは全てString型で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソース（アクション）クラスの実装**

```java
@Path("/projects")
public class ProjectAction {

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid
    public HttpResponse save(ProjectForm form) {
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストをJSON形式で受け付ける
- `@Valid` を付けることでリクエストBodyをFormに変換した後にBean Validationが実行される
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録
- 登録完了時はステータスコード `201` を返す

**3. ハンドラの設定**

JSONのリクエスト/レスポンス変換には `BodyConvertHandler` にJSONコンバータを設定します。また `JaxRsBeanValidationHandler` は `BodyConvertHandler` より後ろに配置します。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/jsonに対応したコンバータを設定 -->
      <!-- （Jacksonなど使用するコンバータを追加） -->
    </list>
  </property>
</component>
```

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの動作要件）
- `@Valid` を付け忘れるとバリデーションが実行されない
- `BodyConvertHandler` はルーティングアダプタより後ろ、`JaxRsBeanValidationHandler` は `BodyConvertHandler` より後ろにハンドラキューへ配置すること

参照: restful-web-service-getting-started-create.json:s1, handlers-jaxrs-bean-validation-handler.json:s4, handlers-body-convert-handler.json:s4