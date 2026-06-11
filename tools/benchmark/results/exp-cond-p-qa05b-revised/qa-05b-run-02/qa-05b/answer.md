**結論**: NablarchのRESTfulウェブサービスでJSONを受け取ってDBへ登録するには、`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`アノテーションを付けた業務アクションメソッドを実装し、`UniversalDao.insert`でDB登録する。JSON→Formへの変換はリクエストボディ変換ハンドラ（`BodyConvertHandler`）が自動で行う。

---

**根拠**:

**処理の流れ（アーキテクチャ）**

1. Webフロントコントローラがリクエストをハンドラキューへ委譲
2. ルーティングアダプタがURIからアクションクラスを特定
3. **リクエストボディ変換ハンドラ**（`BodyConvertHandler`）がリクエストボディをFormクラスへ変換
4. **Bean Validationハンドラ**（`JaxRsBeanValidationHandler`）がFormに対してバリデーション実行
5. 業務アクションメソッドでDB登録処理を実行
6. `JaxRsResponseHandler`がレスポンスをクライアントへ返却

**フォームクラスの作成**

```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

- プロパティは全てString型で宣言する

**業務アクションメソッドの実装**

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

- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストボディをJSON形式で受け付けるよう指定
- `@Valid`: `JaxRsBeanValidationHandler`によりFormに対してBean Validationが実行される。バリデーションエラー時は`ApplicationException`が送出され、以降の処理は実行されない
- `BeanUtil.createAndCopy`: FormをEntityに変換
- `UniversalDao.insert`: EntityをDBへ登録（SQLを書かずにINSERT可能）
- `HttpResponse.Status.CREATED`（ステータスコード`201`）を返却

**最小ハンドラ構成**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | グローバルエラーハンドラ | 実行時例外のログ出力 |
| 2 | `JaxRsResponseHandler` | レスポンス書き込み・エラーレスポンス生成 |
| 3 | データベース接続管理ハンドラ | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ | トランザクション開始・コミット・ロールバック |
| 5 | ルーティングアダプタ | URIからアクションを決定 |
| 6 | **`BodyConvertHandler`** | JSONボディ→Formへ変換 |
| 7 | **`JaxRsBeanValidationHandler`** | Formに対してバリデーション実行 |

> **Tip**: Jakarta RESTful Web Servicesアダプタを使用すると、`BodyConvertHandler`と`JaxRsBeanValidationHandler`が自動的にハンドラキューへ追加される。

**UniversalDAOのコンポーネント設定**

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

**注意点**:
- `BodyConvertHandler`に`application/json`対応の`BodyConverter`が設定されていない場合、ステータスコード`415`（サポートしていないメディアタイプ）が返却される
- `BodyConvertHandler`は必ずルーティングアダプタより後ろに設定すること（アクションのアノテーション情報が必要なため）
- `JaxRsBeanValidationHandler`は`BodyConvertHandler`より後ろに設定すること（変換後のFormが必要なため）
- RESTfulウェブサービスでは`ETag`/`If-Match`を使用した楽観的ロックには対応していない

参照: restful-web-service-getting-started-create.json:s1, restful-web-service-architecture.json:s2, restful-web-service-architecture.json:s3, restful-web-service-architecture.json:s4, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s2, libraries-universal-dao.json:s6