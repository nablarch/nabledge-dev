`exists`メソッドの情報が取得できました。Step 4に進みます。

**read_sections**: `javadoc-nablarch-common-dao-UniversalDao.json:s17`, `javadoc-nablarch-common-dao-UniversalDao.json:s18`, `component/libraries/libraries-universal-dao.json:s7`

---

**Step 5: 回答生成**

**結論**: `UniversalDao.exists` でSQL_IDを指定してデータ存在チェックをするには、`exists(entityClass, sqlId)` または `exists(entityClass, sqlId, params)` メソッドを使用します。SQLファイルに検索用SQLを定義してSQL_IDで呼び出すと、`true`/`false` で存在有無が返ります。

**根拠**:

バインド変数なしの場合:
```java
boolean result = UniversalDao.exists(User.class, "FIND_BY_STATUS");
```

バインド変数ありの場合:
```java
// 検索条件Beanを用意する
User condition = new User();
condition.setStatus("active");

boolean result = UniversalDao.exists(User.class, "FIND_BY_STATUS", condition);
```

SQLファイル（`sample/entity/User.sql`）の記述例:
```sql
FIND_BY_STATUS =
SELECT
    user_id
FROM
    user
WHERE
    status = :status
```

- `sqlId` は通常のファイル検索と同じルールで指定する（`#` を使って `SomeClass#FIND_BY_STATUS` と明示的に指定することも可能）
- `params` はバインド変数を持つBeanまたはMapで指定する
- SQLファイルのパスは、第1引数 `entityClass` のFQCNからパス導出される（例: `sample.entity.User` → `sample/entity/User.sql`）

**注意点**: `exists` は内部的に検索用SQLを件数取得SQLに変換して実行するため、存在確認専用のSQLを別途作成する必要はない。

参照: `javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s17`, `javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s18`, `component/libraries/libraries-universal-dao.json:s7`

---

**Step 6: verify**

Nablarch固有クレームの確認:

| クレーム | 根拠 |
|----------|------|
| `UniversalDao.exists(entityClass, sqlId)` メソッドが存在する | s17に明記 |
| `UniversalDao.exists(entityClass, sqlId, params)` メソッドが存在する | s18に明記 |
| 戻り値は `boolean`（存在すれば`true`） | s17, s18に明記 |
| 検索用SQLを変換して件数取得SQLとして実行する | s18「検索用のSQLを変換して使用する」 |
| `#` を使ったSQL_ID指定が可能 | s7に明記 |
| SQLファイルパスはBeanクラスから導出 | s7に明記 |

→ `verify_result = PASS`

---

**結論**: `UniversalDao.exists` でSQL_IDを指定してデータ存在チェックをするには、`exists(entityClass, sqlId)` または `exists(entityClass, sqlId, params)` メソッドを使用します。

**根拠**:

バインド変数なしの場合:
```java
boolean result = UniversalDao.exists(User.class, "FIND_BY_STATUS");
```

バインド変数ありの場合:
```java
// 検索条件Beanを用意する
User condition = new User();
condition.setStatus("active");

boolean result = UniversalDao.exists(User.class, "FIND_BY_STATUS", condition);
```

SQLファイル（`sample/entity/User.sql`）の記述例:
```sql
FIND_BY_STATUS =
SELECT
    user_id
FROM
    user
WHERE
    status = :status
```

- 第1引数: 検索結果をマッピングするエンティティクラス（SQLファイルのパス導出にも使用）
- 第2引数: SQL_ID（`ClassName#SQL_ID` 形式でファイルを明示的に指定することも可能）
- 第3引数（任意）: バインド変数を保持するBeanまたはMap

**注意点**: `exists` は内部的に検索用SQLを件数取得SQLに変換して実行するため、専用の存在確認SQLを別途作成する必要はない。

参照: `javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s17`, `javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s18`, `component/libraries/libraries-universal-dao.json:s7`

---