**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付け、フォームクラスを引数に受け取り、`UniversalDao.insert()` でDB登録します。JSONからフォームへの変換は `BodyConvertHandler` が自動的に行います。

**根拠**:

**処理の流れ（ハンドラキュー）**

| ハンドラ | 役割 |
|---|---|
| ルーティングアダプタ | URIからアクションメソッドを特定 |
| リクエストボディ変換ハンドラ | JSONボディをフォームクラスに変換 |
| Bean Validationハンドラ | フォームクラスをバリデーション |
| アクションクラス | 業務ロジック（DB登録）を実行 |

`Jakarta RESTful Web Servicesアダプタ`（JerseyまたはRESTEasy用）を使うと、リクエストボディ変換ハンドラとBean Validationハンドラが自動的にハンドラキューに追加されます。JSONの変換には `Jackson2BodyConverter` が使われます。

**フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // プロパティは全てString型で宣言する
    // ゲッタ及びセッタ省略
}
```

**アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSON形式のリクエストを受け付けることを宣言
- `@Valid`: リクエストのBean Validationを実行
- `BeanUtil.createAndCopy(Project.class, form)`: フォームをEntityに変換
- `UniversalDao.insert()`: EntityをDBに登録
- ステータスコード `201`（作成完了）を返す

**ユニバーサルDAOの設定**（コンポーネント定義ファイル）

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- `BodyConvertHandler` は `ルーティングアダプタ` よりも後ろに設定する必要があります
- リクエストのContent-Typeが `@Consumes` に指定したMIMEと異なる場合、ステータスコード `415`（Unsupported Media Type）が返されます
- `UniversalDao` を使う場合、`データベースアクセス(JDBCラッパー)` の設定も別途必要です

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-body-convert-handler.json:s4, adapters-jaxrs-adaptor.json:s2, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6