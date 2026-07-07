# qa-01 — run-2

## 質問

大量データを検索するとメモリが足りなくなる。1件ずつ読み込む方法はないか？

## 回答

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

## 参照ナレッジ

（なし）

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts: it explicitly mentions using `UniversalDao.defer()` for deferred loading, and it states that `DeferredEntityList` requires calling `close()` after use. Both facts from the Expected Output checklist are fully covered. |
| answer_relevancy | 0.95 | 0.94 | NG | The score is 0.94 because the response was largely relevant and addressed the question about memory issues when searching large datasets and how to read records one at a time. However, it lost a small amount of points for including a statement that merely directed to external documentation without providing substantive information directly useful to the question. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「UniversalDao.deferメソッドで遅延ロードを使用する」は回答の「UniversalDao.defer()を先に呼び出すだけで遅延ロードが使用できます」に含まれている。参照事実「DeferredEntityListのcloseメソッドを呼び出す必要がある」は回答の「DeferredEntityListは使用後にclose()を呼び出す必要があります」に含まれている。 |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- UniversalDao.deferメソッドで遅延ロードを使用する
- DeferredEntityListのcloseメソッドを呼び出す必要がある
