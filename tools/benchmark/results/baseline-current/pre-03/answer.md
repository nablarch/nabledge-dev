**結論**: UniversalDaoでマスタテーブルを検索するには、主キー検索は`UniversalDao.findById()`、任意のSQL検索は`UniversalDao.findAllBySqlFile()`を使います。

**根拠**:

**1. 主キーを指定した検索（SQLファイル不要）**

EntityクラスにJakarta Persistenceアノテーションを付けるだけで、SQLを書かずに主キー検索できます。

```java
// 主キーを指定した検索（SQLは自動生成）
User user = UniversalDao.findById(User.class, userId);
```

EntityクラスにはJakarta Persistenceアノテーションを設定します:

```java
@Entity
@Table(name = "USERS")
public class User {
    @Id
    @Column(name = "USER_ID")
    public Long getId() { ... }

    @Column(name = "USER_NAME")
    public String getName() { ... }
    // getter/setter省略
}
```

**2. 任意のSQL（SQLファイル）で全件または条件付き検索**

マスタテーブルの全件取得や複雑な条件での検索には、SQLファイルを作成して`findAllBySqlFile()`を使います。

```java
// 全件検索
List<User> users = UniversalDao.findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

SQLファイルのパスはマッピングするBeanのクラスから自動導出されます。`sample.entity.User`クラスなら、クラスパス配下の`sample/entity/User.sql`が対象です。

**3. 条件を指定した検索**

検索条件を持つBeanを引数に渡すことで条件付き検索ができます:

```java
// 検索条件Beanを用意
MasterSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索
List<MasterEntity> results = UniversalDao.findAllBySqlFile(
    MasterEntity.class, "SEARCH_MASTER", condition);
```

重要: 検索条件にはEntityではなく専用のBeanを使うのが推奨。ただし単一テーブルへのアクセスのみならEntityでも可。

**前提設定**: `BasicDaoContextFactory`のコンポーネント定義が必要です。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- ユニバーサルDAOは主キーを指定した更新/削除はできますが、主キー以外の条件を指定した更新/削除は不可。その場合はデータベースアクセス(JDBCラッパー)を使用すること
- 検索結果のマッピングはBeanのプロパティ名とSELECT句の名前が一致する項目のみ対象となる
- 使用できるデータタイプは`String`, `Integer`, `Long`, `BigDecimal`, `java.sql.Date`, `java.sql.Timestamp`, `LocalDate`, `LocalDateTime`等に限定される

参照: `libraries-universal-dao.json#s2`, `libraries-universal-dao.json#s7`, `libraries-universal-dao.json#s10`, `libraries-universal-dao.json#s3`, `libraries-universal-dao.json#s6`