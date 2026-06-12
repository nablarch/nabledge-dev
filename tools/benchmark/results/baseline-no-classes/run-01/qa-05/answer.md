**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、`@Consumes(MediaType.APPLICATION_JSON)` と `@Valid` アノテーションを付けたアクションメソッドを作成し、`BeanUtil.createAndCopy()` でEntityに変換後、`UniversalDao.insert()` でDB登録する。

---

**根拠**:

**1. Formクラスの作成**

リクエストのJSONフィールドを受け取るFormを作成する。プロパティは全てString型で宣言する。

```java
public class ProjectForm implements Serializable {

    /** プロジェクト名 */
    @Required
    @Domain("projectName")
    private String projectName;

    // ゲッタ及びセッタは省略
}
```

**2. アクションメソッドの実装**

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
- `@Consumes(MediaType.APPLICATION_JSON)` でJSON形式のリクエストを受け付ける
- `@Valid` でBean Validationによるバリデーションを実行する
- `BeanUtil.createAndCopy()` でFormをEntityに変換する
- `UniversalDao.insert()` でDB登録する
- 正常登録時はステータスコード `201` を返す

**3. BodyConvertHandlerの設定確認**

コンポーネント定義ファイルに、JSON用のBodyConverterが設定されていること。ブランクプロジェクトでは既定で設定済みだが、カスタム環境では確認が必要。

```xml
<component class="nablarch.fw.jaxrs.BodyConvertHandler">
  <property name="bodyConverters">
    <list>
      <!-- JSON用コンバータを追加 -->
      <component class="nablarch.fw.jaxrs.JaxbBodyConverter" />
    </list>
  </property>
</component>
```

**注意点**:
- FormのプロパティはすべてString型で宣言すること（バリデーション・変換の仕様上の要件）
- `@Valid` によるバリデーションエラー時は `ApplicationException` が送出されてリクエストが中断される（後続のDB登録処理は実行されない）
- Content-TypeがJSONでないリクエストが来た場合、ステータスコード `415` が返却される

参照: restful-web-service-getting-started-create.json:s1, handlers-body-convert-handler.json:s4, handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6