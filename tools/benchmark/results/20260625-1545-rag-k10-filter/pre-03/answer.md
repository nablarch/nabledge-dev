UniversalDaoでデータベースを検索する方法は、主に以下の4パターンです。

---

## 1. SQLファイルを使った全件検索

SQLファイルを作成し、SQL IDを指定して検索します。検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目に自動マッピングされます。

```java
// User.class が sample.entity.User の場合、
// SQLファイルのパスは sample/entity/User.sql
EntityList<User> users = UniversalDao.findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

## 2. 検索条件を指定した検索

検索条件を持つBeanを第3引数に渡します。

```java
// 検索条件Beanを用意
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索（複数件）
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);

// 1件取得（該当なしの場合はNoDataExceptionがスロー）
Book condition = new Book();
condition.setId(1L);
Book book = UniversalDao.findBySqlFile(Book.class, "FIND_BY_ID", condition);
```

> **重要:** 検索条件はEntityではなく専用のBeanを使うことが推奨されています（単一テーブルアクセスの場合はEntityも可）。

## 3. ページングを使った検索

`per()`（1ページあたりの件数）と `page()`（ページ番号）を先に呼び出します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

## 4. 大量データの遅延ロード

大量データを一度にメモリに展開できない場合は `defer()` を使います。使用後は必ず `close()` が必要です。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

## 別のSQLファイルを参照する場合

SQL IDに`#`を含めると「SQLファイルのパス#SQL ID」として解釈されます。

```java
// sample/entity/Member.sql の FIND_BY_NAME を使用
UniversalDao.findAllBySqlFile(GoldUser.class, "sample.entity.Member#FIND_BY_NAME");
```

---

**まとめ:** 通常は `findAllBySqlFile`（複数件）または `findBySqlFile`（1件）を使い、検索条件をBeanで渡します。大量データにはページングか遅延ロードを使い分けてください。