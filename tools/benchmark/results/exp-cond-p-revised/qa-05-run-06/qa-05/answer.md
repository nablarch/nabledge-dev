**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、リソースクラスのメソッドに `@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` を付与し、`BeanUtil.createAndCopy` でEntityに変換後、`UniversalDao.insert` でDBに登録する。

**根拠**:

**1. Formクラスの作成**

受信したJSONをマッピングするFormクラスを作成する。プロパティは**全てString型**で宣言すること。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. リソース(アクション)クラスの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)`: リクエストをJSON形式で受け付ける指定
- `@Valid`: リクエストのバリデーションを実行する
- `BeanUtil.createAndCopy(Project.class, project)`: FormをEntityに変換する
- `UniversalDao.insert(...)`: Entityをデータベースに登録する
- 戻り値にステータスコード `201`（リソース作成完了）を返却する

**3. ユニバーサルDAOの設定（コンポーネント定義ファイル）**

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- FormのプロパティはすべてString型で宣言すること。String以外の型を使うと、不正な値が送信された際にバリデーション前に変換処理が失敗し、予期せぬ例外が発生する
- Content-TypeヘッダとConsumesのMIMEが一致しない場合はステータスコード `415` が返却される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s5, libraries-bean-validation.json:s8, libraries-universal-dao.json:s6