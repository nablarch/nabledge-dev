**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録する場合、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、引数にフォームクラスを受け取って `UniversalDao.insert()` でDB登録します。

**根拠**:

**① フォームクラスの作成**

受信するJSONのフィールドをString型プロパティとして持つフォームを作成します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- プロパティは全て `String` 型で宣言します。

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

- `@Consumes(MediaType.APPLICATION_JSON)` — JSONリクエストを受け付けることを宣言します。リクエストボディ変換ハンドラがこのアノテーションを見て `application/json` に対応したコンバータでフォームに変換します。
- `@Valid` — Jakarta RESTful Web Services Bean Validationハンドラがフォームに対してバリデーションを実行します。バリデーションエラー時は `ApplicationException` が送出されます。
- `BeanUtil.createAndCopy()` — フォームをエンティティに変換します。
- `UniversalDao.insert()` — エンティティをDBに登録します。
- 戻り値に `HttpResponse.Status.CREATED.getStatusCode()`（ステータスコード `201`）を返します。

**③ メソッドのシグネチャ選択指針**

| 引数定義 | ユースケース |
|---|---|
| フォーム(Java Beans) | リクエストボディから変換したフォームで処理する場合 |
| `JaxRsHttpRequest` | パスパラメータ・クエリパラメータ・HTTPヘッダを取得する場合 |
| 組み合わせ | フォームとリクエスト情報を両方使う場合 |

**注意点**:
- `Consumes` に設定したMIMEとリクエストヘッダの `Content-Type` が一致しない場合、ステータスコード `415` が返却されます。
- リクエストボディ変換ハンドラはルーティングアダプタより後ろに、Bean Validationハンドラはリクエストボディ変換ハンドラより後ろに設定する必要があります。
- RESTfulウェブサービスでは `排他制御` ライブラリは使用できません。楽観的ロックが必要な場合は、リクエストボディに直接バージョン番号を含めてください。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4