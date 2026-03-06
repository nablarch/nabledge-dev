**結論**: UniversalDaoでページングを実装するには、`UniversalDao.per(件数/ページ).page(ページ番号)` を検索メソッド呼び出し前にチェーンします。

**根拠**:

`UniversalDao#per` と `UniversalDao#page` を使ってページングを実行します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

- `per(long)` : 1ページあたりの件数を指定します
- `page(long)` : 取得するページ番号（1始まり）を指定します

**ページング情報の取得**: 取得した `EntityList` から `Pagination` オブジェクトを取り出せます。

```java
Pagination pagination = users.getPagination();
```

`Pagination` オブジェクトには総件数や総ページ数などの情報が含まれます。

---

**性能チューニング（件数取得SQLのカスタマイズ）**:

ページング処理では、実際の範囲指定取得の前に件数取得SQLが自動で発行されます。デフォルトでは元SQLを `SELECT COUNT(*) FROM (...)` で包んだ形式になります。元SQLに `ORDER BY` 句が含まれる場合、件数取得時に不要な処理負荷が発生することがあります。

その場合は、使用しているダイアレクトをカスタマイズして `Dialect#convertCountSql` の実装を変更することで最適化できます。

```java
public class CustomH2Dialect extends H2Dialect {
    private Map<String, String> sqlMap;

    @Override
    public String convertCountSql(String sqlId, Object params, StatementFactory statementFactory) {
        if (sqlMap.containsKey(sqlId)) {
            return statementFactory.getVariableConditionSqlBySqlId(sqlMap.get(sqlId), params);
        }
        return convertCountSql(statementFactory.getVariableConditionSqlBySqlId(sqlId, params));
    }

    public void setSqlMap(Map<String, String> sqlMap){
        this.sqlMap = sqlMap;
    }
}
```

**設定例**:

```xml
<component name="dialect" class="com.nablarch.example.app.db.dialect.CustomH2Dialect">
  <property name="sqlMap">
    <map>
      <entry key="com.nablarch.example.app.entity.Project#SEARCH_PROJECT"
             value="com.nablarch.example.app.entity.Project#SEARCH_PROJECT_FORCOUNT"/>
    </map>
  </property>
</component>
```

**注意点**:
- ページング処理は内部でデータベースアクセス（JDBCラッパー）の範囲指定検索機能を使用しています
- 件数取得SQLは先に発行されるため、性能が問題になる場合は件数取得用のSQLをカスタマイズしてください
- 件数取得SQLは元SQLと**同一の検索条件**を持つ必要があります（差分が発生しないよう注意）
- 大量データを処理する場合の代替手段として遅延ロード（`UniversalDao.defer()`）がありますが、カーソルのトランザクション制御の問題が発生するRDBMSでは代わりにページングを使用することが推奨されています

参照: `libraries-universal_dao.json#paging`, `libraries-universal_dao.json#extension-examples`, `libraries-universal_dao.json#lazy-load`
