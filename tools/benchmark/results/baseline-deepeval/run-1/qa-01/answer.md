セクション内容を確認しました。Step 5〜7: 回答を生成・検証します。

---

**結論**: NablarchバッチでDBの大量データを1件ずつ読み込むには、`createReader`メソッドで`DatabaseRecordReader`を返し、フレームワーク管理のループ（DataReader機構）を使う。または`UniversalDao.defer()`による遅延ロードを使う。`handle`メソッド内でSELECTを発行して自前ループするのはアンチパターン。

---

**根拠**:

### 方法1: DatabaseRecordReader を createReader で使う（推奨）

Nablarchバッチの`DataReader`は1件ずつデータを提供する仕組みになっており、`DatabaseRecordReader`を`createReader`で返すだけでフレームワークが1件ずつ`handle`を呼び出す。

```java
public class MyBatchAction extends BatchAction<SqlRow> {

    @Override
    public Result handle(SqlRow inputData, ExecutionContext ctx) {
        // inputData は 1件分のデータ
        // ここで更新処理を行う
        return new Result.Success();
    }

    @Override
    public DataReader<SqlRow> createReader(ExecutionContext ctx) {
        return new DatabaseRecordReader(); // DBから1件ずつ読み込む
    }
}
```

フレームワークが処理対象データがなくなるまで自動的にループし、一定間隔でコミットも行われる。

### 方法2: UniversalDao.defer() による遅延ロード

ウェブや一部バッチで`UniversalDao`を使う場合、`defer()`を先に呼ぶことで1件ずつロードできる。

```java
// try-with-resourcesを使ったclose呼び出し。
// DeferredEntityListはダウンキャストして取得する。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

`DeferredEntityList#close`を必ず呼ぶ（`try-with-resources`を使う）。

### やってはいけないアンチパターン

```java
// NG: handleメソッド内でSELECTを発行して自前ループ
public Result handle(ExecutionContext context) {
   SqlResultSet sqlResultSet = search("SEARCH");
   for (SqlRow row : sqlResultSet) {
       // 更新処理
   }
}
```

大量件数になるとトランザクションログが逼迫する。`handle`内のSQLは`createReader`に移すこと。

---

**注意点**:
- `UniversalDao.defer()`はサーバサイドカーソルを内部で使用するため、カーソルオープン中にトランザクション制御を行うとカーソルがクローズされてエラーになる場合がある。DBベンダーのマニュアルを確認するか、ページングで回避すること。
- 自前でループ内にコミット処理を入れる実装もアンチパターン。フレームワークのループ制御に委ねること。

参照: `libraries-universal-dao.json:s9`, `nablarch-batch-architecture.json:s3`, `nablarch-batch-architecture.json:s7`, `nablarch-patterns-Nablarchアンチパターン.json:s9`, `nablarch-patterns-Nablarchアンチパターン.json:s10`, `nablarch-patterns-Nablarchアンチパターン.json:s11`

---