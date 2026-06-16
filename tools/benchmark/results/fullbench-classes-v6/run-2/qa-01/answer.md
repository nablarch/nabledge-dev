Nablarchバッチで大量データをメモリに乗せずに処理する方法は、**ユニバーサルDAOの遅延ロード**です。

## ユニバーサルDAOの遅延ロードを使う

`UniversalDao.defer()` を先に呼び出すだけで遅延ロードが使用できます。内部でサーバサイドカーソルを使用し、1件ずつロードするのでメモリが足りなくなりません。

`DeferredEntityList` は使用後に `close()` を呼び出す必要があります。**try-with-resources で記述するのが確実です。**

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

> **注意:** 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされます。遅延ロードを使った大量データ処理中にコミットなどのトランザクション制御を行う場合、クローズ済みカーソルを参照してエラーになる可能性があるため、データベースベンダーのマニュアルでカーソルの挙動を確認してください。

なお、JDBCのフェッチサイズによってメモリ使用量は変わります。詳細はデータベースベンダーのマニュアルを参照してください。

## 参考: DatabaseRecordReader（バッチフレームワークの標準データリーダ）

Nablarchバッチでは、`DatabaseRecordReader` という標準データリーダも提供されています。これはバッチのハンドラキューを介してフレームワークがDBを読み込む仕組みで、アクションハンドラが1件ずつデータを受け取る処理フローになります。

どちらを使うかは処理の構造次第です。業務ロジック内でUniversalDAOを使って検索する場合は遅延ロード、バッチフレームワークの標準フロー（DataReader → アクションハンドラ）を使う場合は `DatabaseRecordReader` を選びます。