セクション読み込み完了。回答を生成します（Step 5）。

---

**結論**: `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたメソッドでFormを引数に受け取り、`BeanUtil.createAndCopy()` でEntityに変換して `UniversalDao.insert()` でDB登録する。

**根拠**:

**1. Formクラスの作成**

リクエストボディのJSONをマッピングするFormクラスを作成する。プロパティは**全てString型**で宣言すること。

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソースクラスのメソッド実装**

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

実装ポイント:
- `@Path` と `@POST` でURLとメソッドをマッピングする
- `@Consumes(MediaType.APPLICATION_JSON)` を付けると、リクエストボディ変換ハンドラがJSONをFormに自動変換する（Content-Typeが不一致の場合は415を返す）
- `@Valid` でBean Validationによるバリデーションを実行する
- `BeanUtil.createAndCopy()` でFormをEntityに変換し、`UniversalDao.insert()` でDB登録する
- 戻り値は `201 Created` を示す `HttpResponse` を返す

**3. メソッド引数・戻り値の選択肢**

| 引数定義 | 用途 |
|---|---|
| フォーム(Java Beans) | リクエストボディのJSONをFormに変換して受け取る（今回のケース） |
| `JaxRsHttpRequest` | パスパラメータやクエリパラメータが必要な場合 |
| 組み合わせ | Formと`JaxRsHttpRequest`を同時に定義することも可能 |

**注意点**:
- Formのプロパティは全てString型で宣言すること（Bean Validationの仕様上の制約）
- BodyConvertHandlerにJSONコンバータ（`application/json`対応の`BodyConverter`実装クラス）が設定されている必要がある
- `UniversalDao`を使用するにはコンポーネント定義に`BasicDaoContextFactory`の設定が必要

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, handlers-body-convert-handler.json:s5

---