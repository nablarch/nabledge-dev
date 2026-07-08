**結論**: UniversalDaoでの検索は `UniversalDao.findAllBySqlFile(EntityClass, "SQL_ID")` を使い、SQLファイルにSQLを記述してSQL IDで呼び出します。検索条件がある場合は第3引数に条件Beanを渡します。

**根拠**:

**1. 事前設定**

コンポーネント定義に `BasicDaoContextFactory` を追加する必要があります。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**2. SQLファイルの作成**

SQLファイルのパスはBeanのクラスから導出されます。たとえば `sample.entity.User` クラスを使う場合、クラスパス配下の `sample/entity/User.sql` に SQL を記述します。

```sql
FIND_BY_NAME =
SELECT USER_ID, USER_NAME
FROM USERS
WHERE USER_NAME = :userName
```

**3. 条件なし検索**

```java
// SQL IDを指定して全件取得
List<User> users = UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

**4. 条件を指定した検索**

```java
// 検索条件Beanを用意する
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", searchCondition);
```

> 検索条件は、Entityではなく検索条件を持つ専用のBeanを指定する。ただし、1つのテーブルのみへのアクセスの場合は、Entityを指定しても良い。

**5. ページングを伴う検索**

```java
EntityList<User> users = UniversalDao.per(20).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
// ページング情報の取得
Pagination pagination = users.getPagination();
```

**6. 大量データの遅延ロード**

大量データを処理する場合は `defer()` を使用します。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

**注意点**:
- 遅延ロードは `DeferredEntityList#close` を必ず呼び出すこと（try-with-resources を使用するのが安全）
- 遅延ロード中にトランザクション制御を行うとカーソルがクローズされる可能性があるため注意
- EntityクラスにはJakarta Persistenceアノテーション（`@Entity`、`@Id`等）の付与が必要

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  SQLを書かなくても単純なCRUDができる
  検索結果をBeanにマッピングできる
  ユニバーサルDAOを使うための設定を行う
  任意のSQL(SQLファイル)で検索する
  条件を指定して検索する
  ページングを行う
  検索結果を遅延ロードする