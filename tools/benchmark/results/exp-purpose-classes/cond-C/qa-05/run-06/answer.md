**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、フォームクラス＋リソース（アクション）クラスの2つを実装し、`@Path`/`@POST`/`@Consumes`/`@Valid` アノテーションで定義します。

**根拠**:

#### 1. フォームクラスを作成する

JSON→フォームの変換は `リクエストボディ変換ハンドラ`（`BodyConvertHandler`）が自動で行います。受け取り用フォームを実装します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ・セッタは省略
}
```

**ポイント**: プロパティは全て `String` 型で宣言します。

#### 2. リソース（アクション）クラスを実装する

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

**ポイント**:
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを指定する。`BodyConvertHandler` がこのアノテーションを見て自動変換します
- `@Valid` を付けると、`JaxRsBeanValidationHandler` がフォームに対してBean Validationを実行します。エラー時は `ApplicationException` をスローして処理を終了します
- `BeanUtil.createAndCopy(Project.class, form)` でフォームをエンティティに変換し、`UniversalDao.insert(...)` でDBに登録します
- 戻り値として `201 Created` を返す `HttpResponse` を返却します

#### 3. URL→クラスのマッピング（`@Path`アノテーション方式）

`@Path` アノテーション方式を使う場合、`PathOptionsProviderRoutesMapping` をディスパッチハンドラとして設定します。上の実装例では `@Path("/projects")` + `@POST` で `POST /projects` のリクエストが `save` メソッドにマッピングされます。

**注意点**:
- `BodyConvertHandler` の `bodyConverters` に JSON用コンバータ（`Jackson2BodyConverter` 等）を設定しておく必要があります。未対応MIMEには `415 Unsupported Media Type` が返ります
- バリデーションエラー時のレスポンス形式は `JaxRsResponseHandler` の設定に依存します
- `UniversalDao.insert` は主キー以外の条件を指定した更新/削除には対応していないため、その場合は `データベースアクセス(JDBCラッパー)` を使用します

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, adapters-router-adaptor.json:s8