# impact-01 — run-1

## 質問

業務トランザクションとは別のトランザクションでSQLを実行する方法はあるか？ロールバックされても別トランザクションの更新は残したい

## 回答

**結論**: `SimpleDbTransactionManager` と `SimpleDbTransactionExecutor` を使用することで、業務トランザクションとは独立した別トランザクションでSQLを実行できます。この別トランザクションは独自にコミット・ロールバックするため、業務トランザクションがロールバックされても更新は残ります。

**根拠**:

**1. コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する**

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <!-- ConnectionFactory実装クラスを設定 -->
  <property name="connectionFactory" ref="connectionFactory" />
  <!-- TransactionFactory実装クラスを設定 -->
  <property name="transactionFactory" ref="transactionFactory" />
  <!-- トランザクションを識別する名前 -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**2. `SimpleDbTransactionExecutor` を使って別トランザクションでSQLを実行する（JDBCラッパー使用時）**

```java
// システムリポジトリからSimpleDbTransactionManagerを取得
SimpleDbTransactionManager dbTransactionManager =
    SystemRepository.get("update-login-failed-count-transaction");

// SimpleDbTransactionExecutorを使用してトランザクションを実行
SqlResultSet resultSet = new SimpleDbTransactionExecutor<SqlResultSet>(dbTransactionManager) {
  @Override
  public SqlResultSet execute(AppDbConnection connection) {
    SqlPStatement statement = connection.prepareStatementBySqlId(
        "jp.co.tis.sample.action.SampleAction#findUser");
    statement.setLong(1, userId);
    return statement.retrieve();
  }
}.doTransaction();
```

**ユニバーサルDAO使用時は `UniversalDao.Transaction` を使う**

```java
// UniversalDao.Transactionを継承したクラスを作成
private static final class MyTransaction extends UniversalDao.Transaction {
    FindPersonsTransaction() {
        super("find-persons-transaction"); // コンポーネント名を指定
    }
    @Override
    protected void execute() {
        // ここが別トランザクションで実行される
        UniversalDao.insert(entity);
    }
}
// インスタンス化すると自動的に別トランザクションで実行される
new MyTransaction();
```

**注意点**:
- `SimpleDbTransactionManager` を直接使うのではなく、必ず `SimpleDbTransactionExecutor`（JDBCラッパー）または `UniversalDao.Transaction`（UniversalDAO）を使うこと。
- `doTransaction()` 呼び出し時点でコミットが確定するため、その後の業務トランザクションのロールバックとは無関係に更新が確定する。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20

## 参照ナレッジ

- [現在のトランザクションとは異なるトランザクションでSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#現在のトランザクションとは異なるトランザクションでsqlを実行する) (s29)
- [現在のトランザクションとは異なるトランザクションで実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#現在のトランザクションとは異なるトランザクションで実行する) (s20)
- [別トランザクションで実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-doma-adaptor.md#別トランザクションで実行する) (s8)
- [アプリケーションで複数のトランザクションを使用する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-transaction-management-handler.md#アプリケーションで複数のトランザクションを使用する) (s7)
- [データベースに対するトランザクション制御](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-transaction.md#データベースに対するトランザクション制御) (s5)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the key fact from the Expected Output: using SimpleDbTransactionManager to define an individual transaction. It not only mentions SimpleDbTransactionManager but also provides detailed XML configuration examples and code samples showing how to define and use it for separate transactions. The core fact is fully addressed. |
| answer_relevancy | 0.95 | 0.92 | NG | The score is 0.92 because the actual output largely addresses the question about executing SQL in a separate transaction from the business transaction and retaining updates even after rollback. However, the score is slightly reduced due to two reference citations included in the output that do not directly contribute to answering the question, making them irrelevant to the input. |
| faithfulness | 0.99 | 0.83 | NG | The score is 0.83 because the actual output contains two contradictions: it incompletely describes the UniversalDao.Transaction constructor by only mentioning the component definition name, omitting that it can also accept a SimpleDbTransactionManager object; and it incorrectly implies that instantiation of a class inheriting UniversalDao.Transaction triggers execution in a separate transaction, when in fact it is the execute method that is automatically executed in the separate transaction. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「SimpleDbTransactionManagerを使って個別トランザクションを定義する」は回答の「コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義する」およびXML設定例に含まれている |
| answer_relevancy | NG | 回答末尾の「参照: libraries-database.json:s29, libraries-universal-dao.json:s20」という内部参照記法がユーザー向け回答に含まれており不適切 |
| faithfulness | OK | ナレッジ内容と矛盾なし。コンストラクタでSimpleDbTransactionManagerオブジェクトも指定できる旨の言及省略は不完全だが矛盾ではなく、「インスタンス化すると自動的に別トランザクションで実行される」はナレッジの`new FindPersonsTransaction()`呼び出しパターンと整合している |

### 参照事実（expected_facts）

- SimpleDbTransactionManagerを使って個別トランザクションを定義する
