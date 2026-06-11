**結論**: RESTfulウェブサービスでJSONをPOSTで受け取りDBに登録するには、アクションクラスに `@Path`・`@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与したメソッドを実装し、`BeanUtil.createAndCopy()` でフォームをエンティティに変換後、`UniversalDao.insert()` で登録する。

---

**根拠**:

#### 1. フォームクラスの作成

リクエストボディ（JSON）を受け取るフォームを作成する。プロパティは **全て `String` 型** で宣言し、Bean Validationアノテーションでバリデーションルールを定義する。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. アクションメソッドの実装

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

| アノテーション / API | 役割 |
|---|---|
| `@Path("/projects")` | クラス全体のURLプレフィックスを定義 |
| `@POST` | POSTリクエストをこのメソッドにマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSONとして変換することをリクエストボディ変換ハンドラに指示 |
| `@Valid` | Jakarta RESTful Web Services Bean ValidaionハンドラによるBean Validationを有効化 |
| `BeanUtil.createAndCopy(Project.class, project)` | フォームをエンティティクラスにコピー変換 |
| `UniversalDao.insert(...)` | エンティティをDBに登録（SQLは実行時に自動生成） |
| `HttpResponse.Status.CREATED.getStatusCode()` | ステータスコード `201` を返却 |

#### 3. 処理の流れ

```
POST /projects (application/json)
  ↓
リクエストボディ変換ハンドラ (@Consumes を参照し JSON → ProjectForm に変換)
  ↓
Bean Validationハンドラ (@Valid を参照し ProjectForm をバリデーション)
  ↓
ProjectAction#save(ProjectForm) 実行
  ↓
BeanUtil.createAndCopy → UniversalDao.insert → DB登録
  ↓
201 Created を返却
```

---

**注意点**:
- フォームのプロパティを `String` 以外の型（`int` など）にするとバリデーション・変換の挙動が変わるため、原則 `String` 型で宣言する
- `@Valid` を付けない場合、Bean Validationが実行されないためバリデーションエラーが検知されない
- `UniversalDao.insert()` は主キー採番が必要な場合、エンティティにシーケンス用アノテーション（`@GeneratedValue` 等）を設定する必要がある

参照: restful-web-service-getting-started-create.json:s1 / restful-web-service-resource-signature.json:s1 / handlers-body-convert-handler.json:s5 / handlers-jaxrs-bean-validation-handler.json:s4 / adapters-router-adaptor.json:s8