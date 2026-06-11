**結論**: `@Consumes(MediaType.APPLICATION_JSON)` + `@Valid` を付けたリソースメソッドでFormを受け取り、`BeanUtil.createAndCopy` でEntityへ変換後に `UniversalDao.insert` でDB登録する。登録完了時は `HttpResponse(201)` を返す。

---

**根拠**:

### 1. リソースクラスの実装（完全例）

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
| `@Path("/projects")` | クラスのURIプレフィックスを定義 |
| `@POST` | POSTリクエストにマッピング |
| `@Consumes(MediaType.APPLICATION_JSON)` | このアノテーションを参照してBodyConvertHandlerがリクエストボディをFormに変換する |
| `@Valid` | JaxRsBeanValidationHandlerがFormに対してBean Validationを実行する |

---

### 2. Formクラスの実装

```java
public class ProjectForm implements Serializable {

    @Required
    @Domain("projectName")
    private String projectName;

    // getter/setter省略
}
```

---

### 3. メソッドシグネチャのパターン

**引数として使用できる型:**

| 引数 | 説明 |
|---|---|
| 引数なし | パラメータ・ボディ不要な場合 |
| フォーム(Java Beans) | リクエストボディから変換したFormを処理する場合 |
| `JaxRsHttpRequest` | パス/クエリパラメータ・HTTPヘッダが必要な場合 |
| `ExecutionContext` | スコープ変数にアクセスする場合 |
| 組み合わせ | 例: `public HttpResponse sample(SampleForm form, JaxRsHttpRequest request)` |

**戻り値として使用できる型:**

| 戻り値 | 説明 |
|---|---|
| `void` | ボディ空の `204: NoContent` を返す |
| フォーム(Java Beans) | BodyConvertHandlerがレスポンスボディに変換して返す |
| `HttpResponse` | HTTPレスポンスをそのままクライアントに返す |

---

### 4. 処理の流れ（ハンドラキュー）

```
リクエスト受信
  → WebFrontController（jakarta.servlet.Filterの実装）
  → ハンドラキュー
       1. グローバルエラーハンドラ
       2. JaxRsResponseHandler        ← 復路でレスポンス書き込み
       3. DB接続管理ハンドラ           ← 往路でDB接続取得、復路で解放
       4. トランザクション制御ハンドラ  ← 往路で開始、復路でコミット
       5. ルーティングアダプタ          ← URIからアクションを決定
       6. BodyConvertHandler           ← JSONボディ→Formに変換
       7. JaxRsBeanValidationHandler   ← Formに対してバリデーション実行
       8. アクションクラス（リソースクラス）
```

---

### 5. Entityクラスの定義

`UniversalDao.insert` で使用するEntityには Jakarta Persistence アノテーションを設定する:

```java
@Entity
@Table(name = "PROJECT")
public class Project {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    @Column(name = "PROJECT_ID")
    private Long projectId;

    @Column(name = "PROJECT_NAME")
    private String projectName;

    // getter/setter
}
```

主なアノテーション:

| アノテーション | 用途 |
|---|---|
| `@Entity` | クラス名からテーブル名を自動導出（パスカルケース→スネークケース大文字変換） |
| `@Table` | テーブル名を明示指定する場合 |
| `@Id` | 主キーカラムに設定 |
| `@Column` | カラム名を明示指定する場合 |
| `@GeneratedValue` | 自動採番を使用する場合 |

---

**注意点**:

- **FormのプロパティはすべてString型で宣言する**: String以外の型があると、不正な値が送信された際にBean変換処理が失敗して予期せぬ例外が発生する。外部からの値をString以外の型に変換したい場合は、バリデーション実施後に変換すること。
- **BodyConvertHandlerの設定が必要**: `application/json` に対応した `BodyConverter` 実装クラスをコンポーネント定義に設定しておく必要がある。設定がない場合、サポートしていないメディアタイプを示すステータスコード `415` が返される。

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-resource-signature.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-bean-validation.json:s8, libraries-universal-dao.json:s24