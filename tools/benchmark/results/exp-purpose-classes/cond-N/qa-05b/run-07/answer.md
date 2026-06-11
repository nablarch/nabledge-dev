**結論**: RESTful ウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、引数としてフォームを受け取り、`BeanUtil.createAndCopy` でエンティティに変換したうえで `UniversalDao.insert` で登録します。

**根拠**:

**① フォームクラスの作成**

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で宣言する。

**② リソースクラスの実装**

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

主要なポイント:

| 要素 | 説明 |
|---|---|
| `@Path("/projects")` | URLとリソースクラスをマッピングする |
| `@POST` | POSTリクエスト時にこのメソッドを呼び出す |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストをJSON形式で受け付けることを宣言する |
| `@Valid` | リクエストボディに対してバリデーションを実行する |
| `BeanUtil.createAndCopy(Project.class, project)` | フォームをエンティティに変換する |
| `UniversalDao.insert(...)` | エンティティをDBに登録する |
| `HttpResponse.Status.CREATED (201)` | リソース作成完了を示すステータスコードを返す |

**③ リクエストボディ変換の仕組み**

`@Consumes` に指定されたMIMEタイプに対応する `BodyConverter` が、リクエストボディをフォームに変換します。JSON用の `BodyConverter` は `BodyConvertHandler` の `bodyConverters` プロパティに設定します。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/json に対応するコンバータを追加する -->
      ...
    </list>
  </property>
</component>
```

**注意点**:
- `@Consumes` に設定したMIMEと異なるContent-Typeのリクエストが来た場合、ステータスコード `415`（サポートしていないメディアタイプ）が返される。
- メソッドの引数としてフォームを受け取る場合、`BodyConvertHandler` がルーティングアダプタよりも後ろに設定されている必要がある。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4