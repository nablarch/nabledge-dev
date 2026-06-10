**結論**: JSONを受け取ってDBに登録するには、リソースクラスに `@Path` / `@POST` / `@Consumes(MediaType.APPLICATION_JSON)` / `@Valid` を組み合わせてメソッドを定義し、`BeanUtil.createAndCopy` でフォームをエンティティに変換したうえで `UniversalDao.insert` でDB登録します。

---

**根拠**:

#### 1. フォームクラスの作成

JSONの各フィールドに対応するフォームクラスを作成します。プロパティは**全てString型**で宣言します。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタ
}
```

#### 2. リソースクラスのメソッド実装

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

| アノテーション | 役割 |
|---|---|
| `@Path("/projects")` | クラスとURLを紐付け |
| `@POST` | POSTリクエストとこのメソッドを紐付け |
| `@Consumes(MediaType.APPLICATION_JSON)` | リクエストボディをJSON→フォームへ変換（リクエストボディ変換ハンドラが処理） |
| `@Valid` | フォームに対してBean Validationを実行（JaxRsBeanValidationHandlerが処理） |

#### 3. 処理の流れ

1. POSTリクエスト受信 → `@Consumes` によりリクエストボディ変換ハンドラがJSONを `ProjectForm` に変換
2. `@Valid` により `JaxRsBeanValidationHandler` がバリデーションを実行
3. バリデーションOKなら `save` メソッドが呼ばれる
4. `BeanUtil.createAndCopy(Project.class, project)` でフォームをエンティティに変換
5. `UniversalDao.insert` でDB登録
6. `201 Created` を返却

**注意点**: 
- フォームのプロパティは全てString型で宣言する必要があります（Bean Validationの仕様のため）
- JSONのContent-Typeが `application/json` 以外だった場合、`415 Unsupported Media Type` が返却されます

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4

---