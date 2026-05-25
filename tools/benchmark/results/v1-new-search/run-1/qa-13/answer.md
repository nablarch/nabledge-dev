**結論**: RESTfulウェブサービスでフォームデータをDBに登録するには、①フォームクラス（全プロパティはString型）を作成し、②アクションクラスのメソッドに `@POST`・`@Consumes(MediaType.APPLICATION_JSON)`・`@Valid` を付与し、③`BeanUtil.createAndCopy` でエンティティに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

### 実装の流れ

#### 1. フォームクラスの作成

クライアントから送信された値を受け付けるフォームクラスを作成する。**プロパティは全てString型**で宣言すること。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

#### 2. アクションクラスの実装

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

実装のポイント:
- `@Consumes(MediaType.APPLICATION_JSON)` でリクエストをJSON形式で受け付けることを指定する。`BodyConvertHandler`（リクエストボディ変換ハンドラ）がJSONをフォームクラスに変換する。
- `@Valid` アノテーションを付与することで、`JaxRsBeanValidationHandler`（Bean Validationハンドラ）がフォームに対してバリデーションを実行する。バリデーションエラー時は `ApplicationException` が送出され、後続処理は実行されない。
- `BeanUtil.createAndCopy` でフォームをエンティティに変換し、`UniversalDao.insert` でDBに登録する。
- 登録完了時のレスポンスはステータスコード `201` (CREATED) を返却する。

#### 3. 最小ハンドラ構成（参考）

DB登録処理に必要なハンドラの構成（設定順）:

| No. | ハンドラ | 役割 |
|---|---|---|
| 1 | グローバルエラーハンドラ | 例外発生時のログ出力 |
| 2 | Jakarta RESTful Web Servicesレスポンスハンドラ | レスポンス書き込み・例外時レスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを決定 |
| 6 | リクエストボディ変換ハンドラ | リクエストボディ→フォームクラス変換 |
| 7 | Bean Validationハンドラ | フォームのバリデーション実行 |

#### 4. ユニバーサルDAOの設定

コンポーネント設定ファイルに `BasicDaoContextFactory` を追加する:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- フォームクラスのプロパティは必ず `String` 型で定義すること。String以外の型があると、不正な値が送信された際にBeanへの変換が失敗し、バリデーション前に予期せぬ例外が発生する。
- `BodyConvertHandler` の `bodyConverters` プロパティに、使用するMIMEに対応した `BodyConverter` を設定すること。未対応のMIMEの場合はステータスコード `415` が返却される。

参照:
- restful-web-service-getting-started-create.json:s1
- restful-web-service-architecture.json:s4
- handlers-body-convert-handler.json:s5
- handlers-jaxrs-bean-validation-handler.json:s4
- libraries-bean-validation.json:s8
- libraries-universal-dao.json:s6

---