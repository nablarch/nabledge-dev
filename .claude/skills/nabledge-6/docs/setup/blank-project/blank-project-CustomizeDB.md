# 使用するRDBMSの変更手順

## 概要

Nablarchのアーキタイプを使用して作成したプロジェクトは、 **初期状態ではH2 Database Engine** (以下H2)を使用するように設定されている。

別のRDBMSを使用するように設定変更する手順を記述する。


# 前提

以下を前提とする。

* 各アーキタイプから生成した直後のプロジェクトを対象とする。
* RDBMSには、接続に使用するユーザや、スキーマが作成済みであること。また、RDBMS上のユーザには適切な権限が付与済みであること。



# Mavenリポジトリへのファイル登録

## JDBCドライバの登録

使用するJDBCドライバについては、以下のいずれかを満たす必要がある。

* Mavenのセントラルリポジトリに登録されている。
* プロジェクトのMavenリポジトリに登録されている。
* ローカルのMavenリポジトリに登録されている。


ここでは、Mavenのセントラルリポジトリに公開されていないJDBCドライバについて、ローカルのMavenリポジトリにJDBCドライバを登録する方法を説明する。手順中のドライバのバージョンについては適宜読み替えること。

> **Important:** * JDBCドライバはCI環境構築までに、プロジェクトのMavenリポジトリに登録することを強く推奨する。 * 以降でJDBCドライバの入手方法についても説明する。JDBCドライバを入手する際には、ライセンスを確認した上で入手すること。

<details>
<summary>keywords</summary>

H2 Database Engine, RDBMS設定変更, アーキタイプ生成プロジェクト, データベース接続前提条件, Mavenリポジトリ, ファイル登録, JDBCドライバ, customizeDBAddFileMavenRepo, JDBCドライバ登録, Mavenリポジトリ, CI環境, ライセンス確認

</details>

## H2

H2の場合、JDBCドライバはMavenのセントラルリポジトリに公開されているため登録は不要である。

<details>
<summary>keywords</summary>

H2, JDBCドライバ, Mavenセントラルリポジトリ, 登録不要

</details>

## Oracle

Oracleの場合、JDBCドライバはMavenのセントラルリポジトリに公開されているため登録は不要である。

<details>
<summary>keywords</summary>

Oracle, JDBCドライバ, Mavenセントラルリポジトリ, 登録不要

</details>

## PostgreSQL

PostgreSQLの場合、JDBCドライバはMavenのセントラルリポジトリに公開されているため登録は不要である。

<details>
<summary>keywords</summary>

PostgreSQL, JDBCドライバ, Mavenセントラルリポジトリ, 登録不要

</details>

## DB2

DB2のJDBCドライバはMavenのセントラルリポジトリに公開されていないため、ローカルのMavenリポジトリに登録する必要がある。

JDBCドライバをWebから取得する場合は、以下のサイトから入手する。

| 配布サイトの名前 | URL |
|---|---|
| IBM DB2 JDBC Driver Versions \|br\| and Downloads | https://www.ibm.com/support/pages/db2-jdbc-driver-versions-and-downloads (外部サイト、英語) |
以下に、入手したJDBCドライバをローカルのMavenリポジトリに登録するコマンドの例を示す。

```bash
mvn install:install-file -DgroupId=com.ibm -DartifactId=db2jcc4 -Dversion=10.5.0.7 -Dpackaging=jar -Dfile=db2jcc4.jar
```

<details>
<summary>keywords</summary>

DB2, JDBCドライバ, db2jcc4, ローカルMavenリポジトリ登録, mvn install:install-file

</details>

## SQLServer

SQLServerの場合、JDBCドライバはMavenのセントラルリポジトリに公開されているため登録は不要である。



# ファイル修正

<details>
<summary>keywords</summary>

SQL Server, JDBCドライバ, Mavenセントラルリポジトリ, 登録不要

</details>

## propertiesファイルの修正

env.properties内の以下の箇所を修正する。

| プロパティ名 | 説明 | 使用するプロジェクト/モジュール |
|---|---|---|
| nablarch.connectionFactory. \|br\| jndiResourceName | JNDIでDataSourceを取得する際のリソース名 | * 各アーキタイプから生成したプロジェクト \|br\| (JNDIからコネクションを取得する環境のpropertiesファイル(後述)に設定) |
| nablarch.db.jdbcDriver | JDBCドライバのクラス名 | * 各アーキタイプから生成したプロジェクト \|br\| (ローカルにコネクションプールを作成する環境のpropertiesファイル(後述)に設定) |
| nablarch.db.url | データベースの接続URL | * 各アーキタイプから生成したプロジェクト \|br\| (ローカルにコネクションプールを作成する環境のpropertiesファイル(後述)に設定) |
| nablarch.db.user | データベースアクセスユーザ名 | * 各アーキタイプから生成したプロジェクト \|br\| (ローカルにコネクションプールを作成する環境のpropertiesファイル(後述)に設定) |
| nablarch.db.password | データベースアクセスユーザのパスワード | * 各アーキタイプから生成したプロジェクト \|br\| (ローカルにコネクションプールを作成する環境のpropertiesファイル(後述)に設定) |
| nablarch.db.schema | 接続するスキーマ名 | * Nablarchのテスティングフレームワーク |
アーキタイプからプロジェクトを生成した直後は、「JNDIからコネクションを取得する環境のpropertiesファイル」に以下が該当する。


| プロジェクト種別 | JNDIからコネクションを取得する環境のpropertiesファイル |
|---|---|
| * ウェブ * RESTfulウェブサービス | * 本番環境用properties(src/env/prod/resources/env.properties) |
| * Jakarta Batchに準拠したバッチ * Nablarchバッチ * コンテナ版ウェブ * コンテナ版RESTfulウェブサービス * コンテナ版Nablarchバッチ | なし |
アーキタイプからプロジェクトを生成した直後は、「ローカルにコネクションプールを作成する環境のpropertiesファイル」に以下が該当する。

| プロジェクト種別 | ローカルにコネクションプールを作成する環境のpropertiesファイル |
|---|---|
| * ウェブ * RESTfulウェブサービス | * 単体試験環境(打鍵テスト)用properties(src/env/dev/resources/env.properties) |
| * Jakarta Batchに準拠したバッチ * Nablarchバッチ | * 単体試験環境(打鍵テスト)用properties(src/env/dev/resources/env.properties) * 本番環境用properties(src/env/prod/resources/env.properties) |
| * コンテナ版ウェブ * コンテナ版RESTfulウェブサービス * コンテナ版Nablarchバッチ | * src/main/resources/env.properties ※解説 |
以下に、ローカルにコネクションプールを作成する環境のpropertiesファイル設定例を示す。

<details>
<summary>keywords</summary>

ファイル修正, RDBMS設定, env.properties, pom.xml, customizeDBNotExistPjRepo, env.properties, nablarch.db.jdbcDriver, nablarch.db.url, nablarch.db.user, nablarch.db.password, nablarch.db.schema, nablarch.connectionFactory.jndiResourceName, JNDI, コネクションプール, 大文字小文字区別

</details>

## H2の設定例(デフォルト)

```text
nablarch.db.jdbcDriver=org.h2.Driver
nablarch.db.url=jdbc:h2:./h2/db/SAMPLE
nablarch.db.user=SAMPLE
nablarch.db.password=SAMPLE
nablarch.db.schema=PUBLIC
```

<details>
<summary>keywords</summary>

H2設定例, org.h2.Driver, nablarch.db.jdbcDriver, jdbc:h2

</details>

## Oracleの設定例

```text
nablarch.db.jdbcDriver=oracle.jdbc.driver.OracleDriver
# jdbc:oracle:thin:@ホスト名:ポート番号:データベースのSID
nablarch.db.url=jdbc:oracle:thin:@localhost:1521/xe
nablarch.db.user=sample
nablarch.db.password=sample
nablarch.db.schema=sample
```

<details>
<summary>keywords</summary>

Oracle設定例, oracle.jdbc.driver.OracleDriver, jdbc:oracle:thin, nablarch.db.url

</details>

## PostgreSQLの設定例

```text
nablarch.db.jdbcDriver=org.postgresql.Driver
# jdbc:postgresql://ホスト名:ポート番号/データベース名
nablarch.db.url=jdbc:postgresql://localhost:5432/postgres
nablarch.db.user=sample
nablarch.db.password=sample
nablarch.db.schema=sample
```

<details>
<summary>keywords</summary>

PostgreSQL設定例, org.postgresql.Driver, jdbc:postgresql, nablarch.db.url

</details>

## DB2の設定例

```text
nablarch.db.jdbcDriver=com.ibm.db2.jcc.DB2Driver
# jdbc:db2://ホスト名:ポート番号/データベース名
nablarch.db.url=jdbc:db2://localhost:50000/SAMPLE
nablarch.db.user=sample
nablarch.db.password=sample
nablarch.db.schema=sample
```

<details>
<summary>keywords</summary>

DB2設定例, com.ibm.db2.jcc.DB2Driver, jdbc:db2, nablarch.db.url

</details>

## SQL Serverの設定例

```text
nablarch.db.jdbcDriver=com.microsoft.sqlserver.jdbc.SQLServerDriver
# jdbc:sqlserver://ホスト名:ポート番号;instanceName=インスタンス名
nablarch.db.url=jdbc:sqlserver://localhost:1433;instanceName=SQLEXPRESS
nablarch.db.user=SAMPLE
nablarch.db.password=SAMPLE
nablarch.db.schema=SAMPLE
```
> **Important:** DBによっては、ユーザ名、パスワード、スキーマの大文字小文字を区別する。 DBに設定した通りに、propertiesファイルにも設定すること。

<details>
<summary>keywords</summary>

SQL Server設定例, com.microsoft.sqlserver.jdbc.SQLServerDriver, jdbc:sqlserver, instanceName

</details>

## コンテナの本番環境設定

コンテナ用のプロジェクトでは、プロファイルによる環境設定の切り替えは行わない。
代わりに、アプリケーションを動かす環境のOS環境変数を使って、 `env.properties` に宣言した設定値を上書きする。

したがって、OS環境変数を設定していない環境では `src/main/resources/env.properties` に書かれた設定がそのまま使用される。
本番等のコンテナ環境で動かすときは、OS環境変数を使って `nablarch.db.url` などの環境依存値を適切に上書きしなければならない。

OS環境変数で設定を上書きする方法については、 OS環境変数を使って環境依存値を上書きする を参照。

また、プロファイルではなくOS環境変数で設定を切り替えるようにしている理由については、 [The Twelve-Factor App の III. 設定](https://12factor.net/ja/config) (外部サイト)を参照。

<details>
<summary>keywords</summary>

コンテナ設定, OS環境変数, env.properties上書き, プロファイル切り替え不使用, Twelve-Factor App, container_production_config

</details>

## pom.xmlファイルの修正

<details>
<summary>keywords</summary>

pom.xml, Maven依存関係, JDBCドライバ依存設定, customizeDBProfiles, customizeDB_pom_dependencies, JDBCドライバ設定, profiles要素, JNDI接続, Maven依存関係, データベース切替, com.h2database, com.oracle.database.jdbc, org.postgresql, com.ibm.db2, com.microsoft.sqlserver, h2, ojdbc11, postgresql, jcc, mssql-jdbc, JDBCドライバ設定, ローカルコネクションプール, dependencies要素, Maven依存関係, com.h2database, Dialectクラス設定, コンポーネント設定ファイル, JNDI接続, データベース方言, nablarch.core.db.dialect.OracleDialect, nablarch.core.db.dialect.PostgreSQLDialect, nablarch.core.db.dialect.DB2Dialect, nablarch.core.db.dialect.SqlServerDialect, nablarch.core.db.dialect.H2Dialect, web-component-configuration.xml, rest-component-configuration.xml, Dialectクラス設定, data-source.xml, ローカルコネクションプール, データベース方言, テスト設定, ユニットテスト, データベース設定, Oracle設定, nablarch.test.core.db.GenericJdbcDbInfo, test-db-info-oracle.xml, テーブル作成, DDL実行, DB2設定, gsp-dba-maven-plugin, db/ddl/, データ投入, Insert文, DB2設定, 初期データ, db/data/

</details>

## (本番環境でJNDIからコネクションを取得するプロジェクトの場合)profiles要素内

profiles要素内で、JDBCドライバの依存関係が記述されている箇所を修正する。


> **Tip:** 本番環境でJNDIからコネクションを取得するプロジェクトの場合、ローカルでコネクションプールを作るときだけ明示的に依存関係に入れる必要があるので、profiles要素内に記載されている。 (JNDIからコネクションを取得する場合は、APサーバのクラスローダから、JDBCドライバを取得できるはずである。)
以下、データベース毎の設定例を記述する。

<details>
<summary>keywords</summary>

H2 Database Engine, RDBMS設定変更, アーキタイプ生成プロジェクト, データベース接続前提条件, Mavenリポジトリ, ファイル登録, JDBCドライバ, customizeDBAddFileMavenRepo, JDBCドライバ登録, Mavenリポジトリ, CI環境, ライセンス確認, H2, JDBCドライバ, Mavenセントラルリポジトリ, 登録不要, Oracle, JDBCドライバ, Mavenセントラルリポジトリ, 登録不要, PostgreSQL, JDBCドライバ, Mavenセントラルリポジトリ, 登録不要, DB2, JDBCドライバ, db2jcc4, ローカルMavenリポジトリ登録, mvn install:install-file, SQL Server, JDBCドライバ, Mavenセントラルリポジトリ, 登録不要, ファイル修正, RDBMS設定, env.properties, pom.xml, customizeDBNotExistPjRepo, env.properties, nablarch.db.jdbcDriver, nablarch.db.url, nablarch.db.user, nablarch.db.password, nablarch.db.schema, nablarch.connectionFactory.jndiResourceName, JNDI, コネクションプール, 大文字小文字区別, H2設定例, org.h2.Driver, nablarch.db.jdbcDriver, jdbc:h2, Oracle設定例, oracle.jdbc.driver.OracleDriver, jdbc:oracle:thin, nablarch.db.url, PostgreSQL設定例, org.postgresql.Driver, jdbc:postgresql, nablarch.db.url, DB2設定例, com.ibm.db2.jcc.DB2Driver, jdbc:db2, nablarch.db.url, SQL Server設定例, com.microsoft.sqlserver.jdbc.SQLServerDriver, jdbc:sqlserver, instanceName, コンテナ設定, OS環境変数, env.properties上書き, プロファイル切り替え不使用, Twelve-Factor App, container_production_config, pom.xml, Maven依存関係, JDBCドライバ依存設定, customizeDBProfiles, customizeDB_pom_dependencies, JDBCドライバ設定, profiles要素, JNDI接続, Maven依存関係, データベース切替, com.h2database, com.oracle.database.jdbc, org.postgresql, com.ibm.db2, com.microsoft.sqlserver, h2, ojdbc11, postgresql, jcc, mssql-jdbc

</details>

## H2の設定例(デフォルト)

```xml
<profiles>
  <!-- 中略 -->
  <profile>
    <!-- 中略 -->
    <dependencies>
      <!-- 中略 -->
      <dependency>
        <groupId>com.h2database</groupId>
        <artifactId>h2</artifactId>
        <version>2.2.220</version>
        <scope>runtime</scope>
      </dependency>
      <!-- 中略 -->
    </dependencies>
  </profile>
```

<details>
<summary>keywords</summary>

H2設定例, org.h2.Driver, nablarch.db.jdbcDriver, jdbc:h2

</details>

## Oracleの設定例

```xml
<profiles>
  <!-- 中略 -->
  <profile>
    <!-- 中略 -->
    <dependencies>
      <!-- 中略 -->
      <dependency>
        <groupId>com.oracle.database.jdbc</groupId>
        <artifactId>ojdbc11</artifactId>
        <version>23.2.0.0</version>
        <scope>runtime</scope>
      </dependency>
      <!-- 中略 -->
    </dependencies>
  </profile>
```

<details>
<summary>keywords</summary>

Oracle設定例, oracle.jdbc.driver.OracleDriver, jdbc:oracle:thin, nablarch.db.url

</details>

## PostgreSQLの設定例

```xml
<profiles>
  <!-- 中略 -->
  <profile>
    <!-- 中略 -->
    <dependencies>
      <!-- 中略 -->
      <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <version>42.7.2</version>
        <scope>runtime</scope>
      </dependency>
      <!-- 中略 -->
    </dependencies>
  </profile>
```

<details>
<summary>keywords</summary>

PostgreSQL設定例, org.postgresql.Driver, jdbc:postgresql, nablarch.db.url

</details>

## DB2の設定例

```xml
<profiles>
  <!-- 中略 -->
  <profile>
    <!-- 中略 -->
    <dependencies>
      <!-- 中略 -->
      <dependency>
        <groupId>com.ibm.db2</groupId>
        <artifactId>jcc</artifactId>
        <version>11.5.9.0</version>
        <scope>runtime</scope>
      </dependency>
      <!-- 中略 -->
    </dependencies>
  </profile>
```

<details>
<summary>keywords</summary>

DB2設定例, com.ibm.db2.jcc.DB2Driver, jdbc:db2, nablarch.db.url

</details>

## SQLServerの設定例

```xml
<profiles>
  <!-- 中略 -->
  <profile>
    <!-- 中略 -->
    <dependencies>
      <!-- 中略 -->
      <dependency>
        <groupId>com.microsoft.sqlserver</groupId>
        <artifactId>mssql-jdbc</artifactId>
        <version>12.6.1.jre11</version>
        <scope>runtime</scope>
      </dependency>
      <!-- 中略 -->
    </dependencies>
  </profile>
```

## (本番環境でローカルにコネクションプールを作成するプロジェクトの場合)dependencies要素内

dependencies要素内で、JDBCドライバの依存関係が記述されている箇所を修正する。

デフォルトで記述されているdependency要素の例を示す。


```xml
<dependencies>
  <!-- TODO: プロジェクトで使用するDB製品にあわせたJDBCドライバに修正してください。 -->
  <!-- 中略 -->
  <dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <version>2.2.220</version>
    <scope>runtime</scope>
  </dependency>
  <!-- 中略 -->
</dependencies>
```
dependency要素内の各要素については、(本番環境でJNDIからコネクションを取得するプロジェクトの場合)profiles要素内 と同じように記述する。

<details>
<summary>keywords</summary>

JDBCドライバ設定, ローカルコネクションプール, dependencies要素, Maven依存関係, com.h2database

</details>

## (本番環境でJNDIからコネクションを取得するプロジェクトの場合)コンポーネント設定ファイル (src/main/resources/)

本番環境でJNDIからコネクションを取得するプロジェクトの場合、src/main/resourcesに配置しているコンポーネント設定ファイルにプロジェクトが使用するデータベースのDialectクラスが定義されている。
各プロジェクトのコンポーネント設定ファイル名は以下となる。

| プロジェクト種別 | コンポーネント設定ファイル名 |
|---|---|
| ウェブ | web-component-configuration.xml |
| RESTfulウェブサービス | rest-component-configuration.xml |
上記ファイルの以下の設定を変更する。

```xml
<!-- ダイアレクト設定 -->
<!-- 使用するDBに合わせてダイアレクトを設定すること -->
<component name="dialect" class="nablarch.core.db.dialect.H2Dialect" />
```
Nablarchには以下のDialectクラスが用意されている。使用するデータベースに対応したDialectクラスに修正すること。

| データベース | Dialectクラス |
|---|---|
| Oracle | nablarch.core.db.dialect.OracleDialect |
| PostgreSQL | nablarch.core.db.dialect.PostgreSQLDialect |
| DB2 | nablarch.core.db.dialect.DB2Dialect |
| SQL Server | nablarch.core.db.dialect.SqlServerDialect |

<details>
<summary>keywords</summary>

Dialectクラス設定, コンポーネント設定ファイル, JNDI接続, データベース方言, nablarch.core.db.dialect.OracleDialect, nablarch.core.db.dialect.PostgreSQLDialect, nablarch.core.db.dialect.DB2Dialect, nablarch.core.db.dialect.SqlServerDialect, nablarch.core.db.dialect.H2Dialect, web-component-configuration.xml, rest-component-configuration.xml

</details>

## (本番環境でローカルにコネクションプールを作成するプロジェクトの場合)data-source.xml  (src/main/resources/)

本番環境でローカルにコネクションプールを作成するプロジェクトの場合、data-source.xmlにプロジェクトが使用するデータベースのDialectクラスが記述されている。

このDialectクラスを、使用するデータベースに対応したDialectクラスに修正する。

使用するDialectクラスは、(本番環境でJNDIからコネクションを取得するプロジェクトの場合)コンポーネント設定ファイル (src/main/resources/) と同一である。

<details>
<summary>keywords</summary>

Dialectクラス設定, data-source.xml, ローカルコネクションプール, データベース方言, テスト設定, ユニットテスト, データベース設定, Oracle設定, nablarch.test.core.db.GenericJdbcDbInfo, test-db-info-oracle.xml

</details>

## unit-test.xml  (src/test/resources)

テスティングフレームワークが使用するデータベースの設定が記述されている。

デフォルトは以下のように汎用のDB設定になっている。

Oracleを使用する場合は、記述を修正する。

```xml
<!-- TODO: 使用するDBに合せて設定してください。 -->
<!-- Oracle用の設定 -->
<!--
  <import file="nablarch/test/test-db-info-oracle.xml"/>
-->
<!-- 汎用のDB設定 -->
<component name="dbInfo" class="nablarch.test.core.db.GenericJdbcDbInfo">
  <property name="dataSource" ref="dataSource"/>
  <property name="schema" value="${nablarch.db.schema}"/>
</component>
```
# Nablarchが使用するテーブル作成とデータの投入

## テーブル作成

各プロジェクトの以下のディレクトリに、RDBMS別にDDLを用意している。
このDDLを実行することで、Nablarchが使用するテーブルの作成ができる。

* db/ddl/


> **Tip:** DB2の場合、create.sqlの先頭に接続先データベースと、使用スキーマが記述されているので書きかえてからDDLを実行する。 DDLの実行は、「DB2 コマンド・ウィンドウ」上で以下を実行する。 .. code-block:: text db2 -tvf "C:\develop\myapp-web\db\ddl\db2\create.sql"
> **Tip:** gsp-dba-maven-plugin\ [#gsp]_\ 使用時は、以下のコマンドでgsp-dba-maven-pluginを実行すればテーブルが作成される。 .. code-block:: bash mvn -P gsp clean generate-resources
.. [#gsp]

gsp-dba-maven-pluginを使用するためには、別途設定が必要である。

設定については addin_gsp を参照。

<details>
<summary>keywords</summary>

テーブル作成, DDL実行, DB2設定, gsp-dba-maven-plugin, db/ddl/

</details>

## データの投入

各プロジェクトの以下のディレクトリに、データのInsert文を用意している。
このInsert文を実行することで、Nablarchが使用するデータのInsertができる。

* db/data/

> **Tip:** DB2の場合、data.sqlの先頭に接続先データベースと使用スキーマを記述してから、SQLを実行する。 以下に接続先データベースと使用スキーマの記述例を示す。 .. code-block:: text CONNECT TO SAMPLE2; SET SCHEMA sample; DDLの実行は、「DB2 コマンド・ウィンドウ」上で以下を実行する。 .. code-block:: text db2 -tvf "C:\develop\myapp-web\db\data\data.sql"
# 動作確認

以下の手順を参照し、動作確認を行う。

* ウェブの疎通確認
* RESTfulウェブサービスの疎通確認
* Jakarta Batchに準拠したバッチの疎通確認
* Nablarchバッチの疎通確認
* コンテナ用ウェブの疎通確認
* コンテナ用RESTfulウェブサービスの疎通確認
* コンテナ用Nablarchバッチの疎通確認


.. |br| raw:: html

<br />

<details>
<summary>keywords</summary>

データ投入, Insert文, DB2設定, 初期データ, db/data/

</details>
