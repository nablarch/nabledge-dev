**結論**: RESTfulウェブサービスでJSONを受け取ってDBに登録するには、アクションクラスのメソッドに`@Consumes(MediaType.APPLICATION_JSON)`と`@Valid`アノテーションを設定し、引数で受け取ったBeanを`UniversalDao.insert()`でDBに登録する。

**根拠**:

アクションクラスの実装例:

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public HttpResponse save(Person person) {
    UniversalDao.insert(person);
    return new HttpResponse();
}
```

- `@Consumes(MediaType.APPLICATION_JSON)` を指定すると、リクエストボディ変換ハンドラ（`BodyConvertHandler`）が `application/json` に対応した `BodyConverter` でリクエストボディを `Person` オブジェクトに変換する。
- `@Valid` を付けると、`JaxRsBeanValidationHandler` がFormに対してBean Validationを実行する。バリデーションエラー時は後続処理に委譲せず `ApplicationException` を送出する。
- `UniversalDao.insert(person)` でDBへの登録を行う。

ユニバーサルDAOのコンポーネント設定（コンポーネント定義ファイルへの追加が必要）:

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:

- `BodyConvertHandler` はルーティングアダプタよりも後ろに設定すること（アクションクラスのアノテーション情報を元に変換処理を行うため）。
- `JaxRsBeanValidationHandler` は `BodyConvertHandler` よりも後ろに設定すること（`BodyConvertHandler` が変換したBeanに対してバリデーションを行うため）。
- ユニバーサルDAOを使用するには、データベースアクセス（JDBCラッパー）の設定に加えて `BasicDaoContextFactory` の設定が必要。

参照: handlers-body-convert-handler.json:s5, handlers-jaxrs-bean-validation-handler.json:s3, handlers-jaxrs-bean-validation-handler.json:s4, libraries-universal-dao.json:s6