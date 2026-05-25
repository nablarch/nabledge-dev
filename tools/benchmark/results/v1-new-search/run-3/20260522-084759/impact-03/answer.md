Step 5〜7: 回答を生成し検証します。

**結論**: Bean Validationのカスタムバリデータ内でDB検索するのは**やってはいけない実装**です。重複チェックは`@Valid`によるBean Validation完了後、業務アクションメソッド内で実施してください。

**根拠**:

Bean Validationの実行中はまだ入力値の安全性が保証されていないため、その状態でDBアクセスするとSQLインジェクションなどの脆弱性につながります（Nablarchのガイダンスによる明示的な禁止事項）。

RESTfulウェブサービスでの正しい実装パターンは以下の通りです：

**1. フォームクラス（Bean Validationアノテーションのみ）**
```java
public class ProjectForm implements Serializable {
    @Required
    @Domain("projectName")
    private String projectName;
    // ゲッタ及びセッタは省略
}
```

**2. 業務アクション（`@Valid`後に重複チェック）**
```java
@Path("/projects")
public class ProjectAction {
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Valid  // ← ここでBean Validationが実行される（入力値チェック）
    public HttpResponse save(ProjectForm form) {
        // ↓ Bean Validation通過後の安全な値でDB検索する
        boolean exists = UniversalDao.findAllBySqlFile(
                Project.class, "CHECK_DUPLICATE").size() > 0;
        if (exists) {
            throw new ApplicationException(
                ValidationUtil.createMessageForProperty(
                    "form.projectName", "duplicate.projectName"));
        }
        UniversalDao.insert(BeanUtil.createAndCopy(Project.class, form));
        return new HttpResponse(HttpResponse.Status.CREATED.getStatusCode());
    }
}
```

`ValidationUtil#createMessageForProperty`を使うことで、エラーを特定のフォームフィールドに紐付けてハイライト表示できます。

**注意点**:
- Bean ValidationはJakarta仕様上、バリデーションの実行順序が保証されないため、単項目チェック前に相関バリデーションが走ることがあります。DB検索を業務アクション後に移すことで、この問題も同時に回避できます
- `@Valid`アノテーションが機能するには、ハンドラキューでJAX-RS Bean ValidatorハンドラをリクエストBody変換ハンドラより後に設定する必要があります

参照: `libraries-bean-validation.json:s12`, `libraries-bean-validation.json:s13`, `handlers-jaxrs-bean-validation-handler.json:s4`, `restful-web-service-getting-started-create.json:s1`

---