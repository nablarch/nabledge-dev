**結論**: RESTful web serviceでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付けたアクションメソッドを作成し、`BeanUtil.createAndCopy()` でEntityに変換後 `UniversalDao.insert()` でDBに登録する。

---

**根拠**:

### 1. フォームクラスの作成

クライアントから送信されたJSONを受け取るフォームを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

### 2. アクションメソッドの実装とURLマッピング

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

- `@Consumes(MediaType.APPLICATION_JSON)`: JSON形式のリクエストを受け付けることを指定
- `@Valid`: リクエストのBean Validationを有効化
- `@Path` + `@POST`: POSTリクエストとURLのマッピングを定義

### 3. 処理の仕組み（ハンドラキューの流れ）

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | JaxRsResponseHandler | レスポンスの書き込み・エラー時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得と解放 |
| 4 | トランザクション制御ハンドラ | 正常時コミット・例外時ロールバック |
| 5 | ルーティングアダプタ | URIからアクションメソッドを特定 |
| 6 | **BodyConvertHandler** | **リクエストボディのJSONをFormに変換** |
| 7 | **JaxRsBeanValidationHandler** | **@ValidのあるメソッドのFormをBean Validation** |

#### BodyConvertHandlerの動作
`@Consumes` で指定されたメディアタイプに対応したBodyConverterがリクエストボディをFormオブジェクトに変換する。Content-TypeがConsumesの指定と一致しない場合はステータスコード `415` を返す。

```java
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse saveJson(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

#### JaxRsBeanValidationHandlerの動作
`@Valid` アノテーションが設定されたメソッドのForm(Bean)に対してBean Validationを実行する。バリデーションエラー発生時は `ApplicationException` を送出して処理を終了する。

### 4. ユニバーサルDAOの設定

`UniversalDao.insert()` を使用するには、コンポーネント定義に以下の設定が必要。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- `@Consumes(MediaType.APPLICATION_JSON)` はリクエストボディの変換フォーマットを指定するため必須。指定がないとJSONがFormに変換されない
- `UniversalDao.insert()` は主キー以外の条件での更新/削除には対応していない。そのような場合はデータベースアクセス(JDBCラッパー)を使用すること
- 登録成功時のレスポンスはステータスコード `201`(CREATED) を返すのが標準的

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6