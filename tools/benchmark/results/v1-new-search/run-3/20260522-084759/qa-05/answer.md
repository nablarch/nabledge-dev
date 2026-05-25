必要なセクションは既に読み込み済みです。Step 5でアンサーを生成します。

**結論**: リソースクラスに `@Path`/`@POST`/`@Consumes(APPLICATION_JSON)` を付与し、Formクラスでリクエストボディを受け取り、`BeanUtil.createAndCopy` + `UniversalDao.insert` でDBに登録する。ステータスコード201の `HttpResponse` を返却する。

---

**結論**: リソースクラスに `@Path`/`@POST`/`@Consumes(APPLICATION_JSON)` を付与し、Formクラスでリクエストボディを受け取り、`BeanUtil.createAndCopy` + `UniversalDao.insert` でDBに登録する。ステータスコード201を返却する。

**根拠**:

**① Formクラスの作成**

受け取るJSONのプロパティをString型で宣言し、バリデーションアノテーションを付与する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**② リソースクラスのメソッド実装**

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

各アノテーションの役割:
- `@Path("/projects")` + `@POST`: POSTリクエスト時にこのメソッドを呼び出すよう、ルーティングアダプタがマッピングする
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディをJSONとして受け付けることを宣言する。`BodyConvertHandler` がこのアノテーションを元にJSONをFormへ変換する
- `@Valid`: `JaxRssBeanValidationHandler` がFormに対してBean Validationを実行する
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する
- `UniversalDao.insert(...)`: EntityをDBに登録する（SQLを書かずにINSERT可能）
- 戻り値の `HttpResponse(201)`: リソース作成完了（Created）をクライアントに返す

**③ BodyConvertHandlerの設定（JSON対応コンバータが必要）**

ハンドラのコンポーネント設定で、`application/json` に対応したコンバータを `bodyConverters` プロパティに設定する必要がある。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- application/jsonに対応したコンバータ -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
    </list>
  </property>
</component>
```

**注意点**:
- フォームのプロパティは**全てString型**で宣言すること（Nablarchのバリデーション仕様）
- `BodyConvertHandler` はルーティングアダプタより**後ろ**に設定すること
- `Content-Type: application/json` がリクエストに指定されていない場合、ステータスコード `415` が返される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4

---