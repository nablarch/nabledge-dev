**結論**: `UniversalDao.exists` でSQL_IDを指定する場合、`UniversalDao.exists(EntityClass.class, "SQL_ID")` または `UniversalDao.exists(EntityClass.class, "SQL_ID", params)` を呼び出します。データが存在すれば `true`、存在しなければ `false` を返します。

**根拠**:

2つのオーバーロードがあります。

**バインド変数なし**:
```java
public static boolean exists(Class<T> entityClass, String sqlId)
```
SQL_IDをもとに検索し、データが存在するか否かを確認する。存在すれば `true` を返す。

**バインド変数あり**:
```java
public static boolean exists(Class<T> entityClass, String sqlId, Object params)
```
SQL_IDをもとにバインド変数を展開して検索し、データが存在するか否かを確認する。検索用のSQLを変換して使用する。存在すれば `true` を返す。

**実装例（クライアントの存在確認）**:

```java
// データベースを検索して入力されたIDを持つ顧客が存在するか確認する
if (form.hasClientId()) {
    if (!UniversalDao.exists(Client.class, "FIND_BY_CLIENT_ID",
            new Object[] {Integer.parseInt(form.getClientId()) })) {
        throw new ApplicationException(
            MessageUtil.createMessage(MessageLevel.ERROR,
                "errors.nothing.client", form.getClientId()));
    }
}
```

対応するSQLファイル（`client.sql`）:
```sql
FIND_BY_CLIENT_ID =
SELECT
    CLIENT_ID,
    CLIENT_NAME,
    INDUSTRY_CODE
FROM
    CLIENT
WHERE
    CLIENT_ID = :clientId
```

**注意点**:
- 存在チェックのSQLはSELECT文として記述します。`exists` メソッド内部でSELECT文を件数チェック用のSQLに変換して実行します。
- データベースを参照するバリデーション（存在チェック）はBean Validationではなくアクションメソッド内で実装します。

参照: `javadoc-nablarch-common-dao-UniversalDao.json:s17`, `javadoc-nablarch-common-dao-UniversalDao.json:s18`, `processing-pattern/web-application/web-application-getting-started-project-update.json`