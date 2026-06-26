**結論**: SQLファイル内で `$if(プロパティ名) {SQL文の条件}` という特殊構文を使うことで、入力があった項目だけをwhere句の条件に含める動的SQLを実現できます。Javaコード側では `prepareParameterizedSqlStatementBySqlId` で Beanを渡すだけで、Nablarchが自動的に条件の組み立てを行います。

**根拠**:

**可変条件の記述ルール**

可変条件は `$if(プロパティ名) {SQL文の条件}` で記述します。プロパティ値が以下の場合にその条件が除外されます:

- 配列や `java.util.Collection` の場合: null またはサイズが 0
- それ以外の型（String 等）: null または空文字列

制約:
- **使用できるのは `where` 句のみ**
- `$if` の中に `$if` は使用できない

**SQLの記述例**

`userName` と `userKbn` が可変条件の例:

```none
select
  user_id,
  user_name,
  user_kbn
from
  user
where
  $if (userName) {user_name like :userName%}
  and $if (userKbn) {user_kbn in ('1', '2')}
  and birthday = :birthday
```

**Java実装例**

`userName` だけ値が設定されている場合、`userKbn` の条件は自動的に除外されます:

```java
// beanを生成しプロパティに値を設定
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");

// DbConnectionContextからデータベース接続を取得する
AppDbConnection connection = DbConnectionContext.getConnection();

// SQLIDを元にステートメントを生成する
// 2番めの引数には、条件を持つBeanオブジェクトを指定する。
// このBeanオブジェクトの状態を元にSQLの可変条件の組み立てが行われる。
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#insertUser", entity);

// entityのプロパティの値をバインド変数に設定しSQLが実行される
SqlResultSet result = statement.retrieve(entity);
```

**注意点**:

- この機能はウェブアプリケーションの検索画面のように**ユーザの入力内容によって検索条件が変わる場合**に使うものです。条件だけが異なる複数のSQLを共通化するために使用するものではありません。安易に共通化すると、SQL変更時に思わぬ不具合を埋め込む原因になるため、**必ずSQLを複数定義してください**。
- in句の条件を可変にしたい場合は、名前付きパラメータの末尾に `[]` を付け（例: `:userKbn[]`）、`$if` と組み合わせて使用します。

参照: libraries-database.json:s6, libraries-database.json:s21, libraries-database.json:s22