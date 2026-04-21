# データベースアクセス

<details>
<summary>keywords</summary>

データベースアクセス, ユニバーサルDAO, JDBCラッパー, SQL実行, データベース接続, universal_dao, database, functional_comparison

</details>

データベースへの接続や、SQLを実行する機能を提供する。

Nablarchでは、以下の2種類のデータベースアクセス機能を提供している。

上記のどちらの機能を使用した場合でも、SQLを実行できるが、
以下の理由により ユニバーサルDAO を使用することを推奨する。

* CRUDのSQL文をEntityから自動的に生成しSQLが実行できる
* 検索結果がBeanオブジェクトとして取得できるため、IDEの補完機能が有効活用でき開発効率が良い

> **Important:** `ユニバーサルDAO <universal_dao>` を使用した場合でも、 データベースへの接続やSQL実行は JDBCのラッパー機能 を使用している。 このため、 JDBCのラッパー機能 を使うための設定などは必要になる。
> **Tip:** ユニバーサルDAO とJakarta Persistenceとの機能比較は、 database-functional_comparison を参照。
