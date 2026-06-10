**結論**: JSONを受け取ってDBに登録するリソースクラスは、`@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` アノテーションをメソッドに付け、フォームを引数で受け取り `UniversalDao.insert()` でDB登録するパターンで実装する。

---

**根拠**:

**フォームクラスの作成**

リクエストボディのJSONを受け取るフォームを作成する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

- フォームのプロパティは全て `String` 型で宣言する。

**リソースクラスの実装**

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

- `@Path` + `@POST` でURLとPOSTメソッドのマッピングを定義する。
- `@Consumes(MediaType.APPLICATION_JSON)` でJSONリクエストを受け付けることを指定する。これにより、リクエストボディ変換ハンドラがJSONをフォームに変換する。
- `@Valid` アノテーションを付けることで、Jakarta RESTful Web Services Bean Validationハンドラがフォームに対してバリデーションを実行する。バリデーションエラー時は `ApplicationException` が送出される。
- `BeanUtil.createAndCopy()` でフォームをエンティティに変換し、`UniversalDao.insert()` でDB登録する。
- 戻り値として `201 Created` を表す `HttpResponse` を返す。

**URLマッピングの設定 (ルーティングアダプタ)**

ルーティングアダプタで `@Path` アノテーションを使ったマッピングを使用する場合、`@Path` と `@POST` アノテーションがマッピングの定義として機能する。

---

**注意点**:
- フォームのプロパティは全て `String` 型で宣言すること（数値型・日付型への変換はバリデーション/BeanUtil変換で行う）。
- `Content-Type: application/json` 以外のリクエストが来た場合、ステータスコード `415` (Unsupported Media Type) が返される。
- バリデーションエラー発生時はリソースクラスのメソッドには処理が届かない。

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4