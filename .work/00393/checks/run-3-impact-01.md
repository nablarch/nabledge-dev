# impact-01 — run-3

## 質問

業務トランザクションとは別のトランザクションでSQLを実行する方法はあるか？ロールバックされても別トランザクションの更新は残したい

## 回答

**結論**: Nablarchバッチでは、業務トランザクションとは別のトランザクションを `SimpleDbTransactionManager` で定義し、`SimpleDbTransactionExecutor`（JDBCラッパー使用時）または `UniversalDao.Transaction`（ユニバーサルDAO使用時）を通じて実行することで、業務トランザクションがロールバックされても別トランザクションの更新を確定させることができます。

**根拠**:

#### JDBCラッパーを使用する場合

**コンポーネント設定ファイル**に `SimpleDbTransactionManager` を定義します:

```xml
<component name="update-login-failed-count-transaction"
    class="nablarch.core.db.transaction.SimpleDbTransactionManager">
  <!-- ConnectionFactory実装クラスを設定する -->
  <property name="connectionFactory" ref="connectionFactory" />
  <!-- TransactionFactory実装クラスを設定する -->
  <property name="transactionFactory" ref="transactionFactory" />
  <!-- トランザクションを識別するための名前を設定する -->
  <property name="dbTransactionName" value="update-login-failed-count-transaction" />
</component>
```

**実装例**（`SimpleDbTransactionExecutor` を使用）:

```java
SimpleDbTransactionManager dbTransactionManager =
    SystemRepository.get("update-login-failed-count-transaction");

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

#### ユニバーサルDAOを使用する場合

`UniversalDao.Transaction` を継承したクラスを作成し、`execute()` メソッド内にユニバーサルDAOの処理を実装します:

```java
private static final class FindPersonsTransaction extends UniversalDao.Transaction {
    private EntityList<Person> persons;

    FindPersonsTransaction() {
        // コンポーネント定義で指定した名前を指定する
        super("find-persons-transaction");
    }

    @Override
    protected void execute() {
        persons = UniversalDao.findAllBySqlFile(Person.class, "FIND_PERSONS");
    }

    public EntityList<Person> getPersons() {
        return persons;
    }
}
```

```java
FindPersonsTransaction findPersonsTransaction = new FindPersonsTransaction();
EntityList<Person> persons = findPersonsTransaction.getPersons();
```

#### Domaアダプタを使用する場合

`DomaConfig#getTransactionManager()` で取得した `TransactionManager` を使って別トランザクションを制御します:

```java
DomaConfig.singleton()
        .getTransactionManager()
        .requiresNew(() ->
                DomaDaoRepository.get(ProjectDao.class).insert(project));
```

**注意点**: `execute()` メソッドが正常終了するとトランザクションがコミットされ、例外やエラーが送出された場合はロールバックされます。業務トランザクションとは独立したトランザクションなので、業務トランザクション側のロールバックによる影響は受けません。

参照: libraries-database.json:s29, libraries-universal-dao.json:s20, adapters-doma-adaptor.json:s8

## 参照ナレッジ

- [現在のトランザクションとは異なるトランザクションでSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#現在のトランザクションとは異なるトランザクションでsqlを実行する) (s29)
- [現在のトランザクションとは異なるトランザクションで実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#現在のトランザクションとは異なるトランザクションで実行する) (s20)
- [別トランザクションで実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-doma-adaptor.md#別トランザクションで実行する) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the expected fact that SimpleDbTransactionManager is used to define a separate/individual transaction. The response explicitly shows how to define a SimpleDbTransactionManager component in the configuration file and how to use it to execute transactions independently from the business transaction. The core expected fact is fully addressed. |
| answer_relevancy | 0.95 | 0.96 | OK | The score is 0.96 because the response was highly relevant in addressing how to execute SQL in a separate transaction from the business transaction (so that updates persist even after a rollback), but it lost a small amount of points for including a reference/citation list that does not directly contribute to answering the question. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「SimpleDbTransactionManagerを使って個別トランザクションを定義する」は回答の「コンポーネント設定ファイルに `SimpleDbTransactionManager` を定義します」および結論文に明示されており、XMLコード例も付随している |
| answer_relevancy | OK | 回答は「業務トランザクションとは別のトランザクションでSQLを実行する方法」という質問に直接答えており、JDBCラッパー・ユニバーサルDAO・Domaアダプタの3つの方法を具体的なコード例とともに説明している。質問と無関係な情報は含まれていない。 |
| faithfulness | OK | JDBCラッパーのXML設定例・Javaコード例はlibraries-database.mdのs29セクションと一致。ユニバーサルDAOの実装例（FindPersonsTransactionクラス）はlibraries-universal-dao.mdのs20セクションと一致。注意点の「execute()メソッドが正常終了するとコミット、例外やエラーが送出された場合はロールバック」もナレッジの記述と矛盾しない。 |

### 参照事実（expected_facts）

- SimpleDbTransactionManagerを使って個別トランザクションを定義する
