# ログ出力

## 機能概要

ログ出力は3つの処理（Logger/LoggerFactory、LogWriter、LogFormatter）から構成されており、それぞれの実装を差し替えることができる。

![ログ出力の構造](../../knowledge/component/libraries/assets/libraries-log/log-structure.png)

差し替えの単位:
- `LogWriter` / `LogFormatter` 単位で差し替え可能
- これらだけでは要件を満たせない場合は `Logger` / `LoggerFactory` を実装してほぼ全ての処理を差し替え可能
- オープンソースのログ出力ライブラリを使用したい場合は `Logger` / `LoggerFactory` を差し替える（詳細は :ref:`log_adaptor` 参照）

**デフォルト提供クラス**:

Logger/LoggerFactory:
- `nablarch.core.log.basic.BasicLogger`
- `nablarch.core.log.basic.BasicLoggerFactory`

LogWriter:
- `nablarch.core.log.basic.FileLogWriter` — ファイルへ出力・ローテーション
- `nablarch.core.log.basic.SynchronousFileLogWriter` — 複数プロセスから1ファイルへの出力
- `nablarch.core.log.basic.StandardOutputLogWriter` — 標準出力へ出力
- `nablarch.core.log.basic.LogPublisher` — 任意のリスナーへ出力

LogFormatter:
- `nablarch.core.log.basic.BasicLogFormatter` — パターン文字列によるフォーマット

RotatePolicy:
- `nablarch.core.log.basic.DateRotatePolicy` — 日時によるローテーション
- `nablarch.core.log.basic.FileSizeRotatePolicy` — ファイルサイズによるローテーション

> **重要**: `SynchronousFileLogWriter` を使う場合は :ref:`log-synchronous_file_log_writer_attention` を参照すること。

**提供されているログの種類**:

各種ログの出力機能はフォーマット処理のみを行っており、ログの出力処理自体は本機能（ログ出力機能）を使用している。Nablarchのアーキタイプから生成したブランクプロジェクトでは各種ログのフォーマットが設定してある。

| ログの種類 | 説明 |
|---|---|
| :ref:`障害通知ログ <failure_log>` | 障害発生時に1次切り分け担当者を特定するのに必要な情報を出力 |
| :ref:`障害解析ログ <failure_log>` | 障害原因の特定に必要な情報を出力 |
| :ref:`SQLログ <sql_log>` | SQL文の実行時間とSQL文を出力（パフォーマンスチューニング用） |
| :ref:`パフォーマンスログ <performance_log>` | 任意の処理の実行時間とメモリ使用量を出力（パフォーマンスチューニング用） |
| :ref:`HTTPアクセスログ <http_access_log>` | ウェブアプリケーションの実行状況・性能・負荷・全リクエスト/レスポンス情報を出力 |
| :ref:`HTTPアクセスログ（RESTfulウェブサービス用） <jaxrs_access_log>` | RESTfulウェブサービスの実行状況・性能・負荷・全リクエスト/レスポンス情報を出力 |
| :ref:`メッセージングログ <messaging_log>` | メッセージング処理におけるメッセージ送受信の状況を出力 |

> **補足**: 本フレームワークでは、障害通知ログと障害解析ログを合わせて「障害ログ」と呼ぶ。

各設定値は :download:`デフォルト設定一覧 <../configuration/デフォルト設定一覧.xlsx>` を参照。

## モジュール一覧

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core</artifactId>
</dependency>
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-applog</artifactId>
</dependency>

<!-- SQLログを使用する場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-jdbc</artifactId>
</dependency>

<!-- HTTPアクセスログを使用する場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>

<!-- HTTPアクセスログ（RESTfulウェブサービス用）を使用する場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-jaxrs</artifactId>
</dependency>

<!-- メッセージングログを使用する場合のみ -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-messaging</artifactId>
</dependency>
```

## ログを出力する

`Logger` は `LoggerManager` から取得する。ロガー名には文字列またはクラスが指定でき、クラスを指定した場合はFQCNがロガー名となる。

```java
// クラスを指定してLoggerを取得する（クラス変数に保持する）
private static final Logger LOGGER = LoggerManager.get(UserManager.class);

// ログの出力有無を事前にチェックしてログ出力を行う
if (LOGGER.isDebugEnabled()) {
    String message = "userId[" + user.getId() + "],name[" + user.getName() + "]";
    LOGGER.logDebug(message);
}
```

> **重要**: 常にログを出力することになっているレベルは事前チェック不要（ソースコードの可読性が落ちるため）。例えば本番運用時の出力レベルがINFOの場合、FATALからINFOまでは事前チェック不要。

> **補足**: SQLログや監視ログなど特定の用途向けのログ出力を行う場合、ロガー名にその用途を表す名前（SQL、MONITORなど）を指定する。それ以外はクラスのFQCNを指定する。

## ログ出力の設定

設定はクラスパス直下の **log.properties** に記述する。場所を変更する場合はシステムプロパティ `nablarch.log.filePath` でファイルパスを指定する（`FileUtil#getResource` 参照）。

```bash
java -Dnablarch.log.filePath=classpath:nablarch/example/log.properties ...
```

**LoggerFactory設定**:

| プロパティ名 | 説明 |
|---|---|
| loggerFactory.className | LoggerFactoryを実装したクラスのFQCN。本機能を使う場合は `nablarch.core.log.basic.BasicLoggerFactory` を指定する |

**LogWriter設定**:

| プロパティ名 | 説明 |
|---|---|
| writerNames | 使用する全てのLogWriterの名前（カンマ区切り） |
| writer.<名前>.className | LogWriterを実装したクラスのFQCN |
| writer.<名前>.<プロパティ名> | LogWriter毎のプロパティ値（使用するLogWriterのJavadocを参照） |

**ロガー設定**:

| プロパティ名 | 説明 |
|---|---|
| availableLoggersNamesOrder | 使用する全てのロガー設定の名前（カンマ区切り） |
| loggers.<名前>.nameRegex | ロガー名とのマッチングに使用する正規表現 |
| loggers.<名前>.level | `LogLevel` の名前。指定レベル以上を全て出力 |
| loggers.<名前>.writerNames | 出力先LogWriterの名前（カンマ区切り） |

> **重要**: `availableLoggersNamesOrder` は記述順に意味がある。Logger取得時に記述順でマッチングを行い最初にマッチしたLoggerを返す。より限定的な正規表現を指定したロガー設定から順に記述すること。例: `availableLoggersNamesOrder=root,sql` と記述した場合、全てのロガー取得が `root` にマッチし、ロガー名 `SQL` のログが `sqlLog` ではなく `appLog` に出力されてしまう。

> **重要**: `availableLoggersNamesOrder` と `loggers.*` で指定するロガー設定の名称は必ず一致させること。`BasicLoggerFactory` の初期処理でチェックを行い、一致しない場合は例外をスローする。`availableLoggersNamesOrder` から名称を取り除く場合は、対応する `loggers.<名前>.*` の設定も明示的に取り除くこと。

> **補足**: 全てのログ出力にマッチするロガー設定（`nameRegex=.*`）を1つ用意し、`availableLoggersNamesOrder` の最後に指定することを推奨する（設定漏れによる重要ログの出力漏れを防ぐ）。

```properties
loggerFactory.className=nablarch.core.log.basic.BasicLoggerFactory

writerNames=appLog,sqlLog,monitorLog,stdout

writer.appLog.className=nablarch.core.log.basic.FileLogWriter
writer.appLog.filePath=/var/log/app/app.log

writer.sqlLog.className=nablarch.core.log.basic.FileLogWriter
writer.sqlLog.filePath=/var/log/app/sql.log

writer.monitorLog.className=nablarch.core.log.basic.FileLogWriter
writer.monitorLog.filePath=/var/log/app/monitoring.log

writer.stdout.className=nablarch.core.log.basic.StandardOutputLogWriter

availableLoggersNamesOrder=sql,monitoring,access,validation,root

loggers.root.nameRegex=.*
loggers.root.level=WARN
loggers.root.writerNames=appLog

loggers.monitoring.nameRegex=MONITOR
loggers.monitoring.level=ERROR
loggers.monitoring.writerNames=appLog,monitorLog

loggers.sql.nameRegex=SQL
loggers.sql.level=DEBUG
loggers.sql.writerNames=sqlLog

loggers.access.nameRegex=app\\.user\\.UserManager
loggers.access.level=INFO
loggers.access.writerNames=appLog,stdout

loggers.validation.nameRegex=nablarch\\.core\\.validation\\.*
loggers.validation.level=DEBUG
loggers.validation.writerNames=stdout
```

## ログ出力の設定を上書く

システムプロパティにプロパティファイルと同じキー名で値を指定することで、ログ設定を上書きできる。これにより共通プロパティファイルを用意しつつ、プロセス毎にログ設定を変更できる。

```bash
java -Dloggers.root.level=INFO ...
```

## ログのフォーマットを指定する

**クラス**: `nablarch.core.log.basic.BasicLogFormatter`（`LogFormatter` の汎用実装）

プレースホルダを使用してフォーマットを指定する。設定はLogWriterのプロパティに行う。

```properties
writer.appLog.formatter.className=nablarch.core.log.basic.BasicLogFormatter
writer.appLog.formatter.format=$date$ -$logLevel$- $loggerName$ $message$
# 日時フォーマット（デフォルト: "yyyy-MM-dd HH:mm:ss.SSS"）
writer.appLog.formatter.datePattern=yyyy/MM/dd HH:mm:ss[SSS]
# ログレベル文言（デフォルト: LogLevel列挙型の名前: FATAL、INFOなど）
writer.appLog.formatter.label.fatal=F
writer.appLog.formatter.label.error=E
writer.appLog.formatter.label.warn=W
writer.appLog.formatter.label.info=I
writer.appLog.formatter.label.debug=D
writer.appLog.formatter.label.trace=T
```

### 起動プロセス

アプリケーションの実行環境を特定するための名前。システムプロパティ `nablarch.bootProcess` で指定する。未指定の場合はブランク。サーバ名＋JOBIDなどの識別文字列を組み合わせることで、同一サーバの複数プロセスから出力されたログの実行環境を特定できる。

### 処理方式

ウェブ・バッチなどの処理方式を識別するための値。プロパティファイルに `nablarch.processingSystem` で指定する。未指定の場合はブランク。

### 実行時ID

リクエストIDに対する個々の実行を識別するID。`ThreadContext` の初期化タイミングで発行される。1リクエストIDに対して複数の実行時IDが発行される（1対多）。複数のログを紐付けるために使用する。

ID体系（起動プロセスは指定された場合のみ付加）:
```
起動プロセス＋システム日時(yyyyMMddHHmmssSSS)＋連番(4桁)
```

> **重要**: リクエストID、実行時ID、ユーザIDを出力する場合、取得元が `ThreadContext` のため、ハンドラ構成に :ref:`thread_context_handler` が含まれている必要がある。ユーザIDは :ref:`thread_context_handler-user_id_attribute_setting` を参照してセッションに値を設定する必要がある。

### 改行コード・タブ文字

フォーマットに `\n`（改行）・`\t`（タブ）を含めることができる（Java記法と同様）。改行コードはシステムプロパティ `line.separator` から取得するため、未変更の場合はOSの改行コードが使用される。

> **補足**: `\n` と `\t` という文字列自体は `BasicLogFormatter` で出力できない。

## 各種ログの設定

各種ログの設定はクラスパス直下の **app-log.properties** に記述する。場所を変更する場合はシステムプロパティ `nablarch.appLog.filePath` でファイルパスを指定する（`FileUtil#getResource` 参照）。

```bash
java -Dnablarch.appLog.filePath=file:/var/log/app/app-log.properties ...
```

各種ログの設定は以下を参照:
- :ref:`failure_log-setting`
- :ref:`sql_log-setting`
- :ref:`performance_log-setting`
- :ref:`http_access_log-setting`
- :ref:`jaxrs_access_log-setting`
- :ref:`messaging_log-setting`

## ログファイルのローテーションを行う

`FileLogWriter` は設定されたRotatePolicyに従ってローテーションを行う。デフォルトは `FileSizeRotatePolicy`（ファイルサイズによるローテーション）。

`RotatePolicy` の実装クラス:
- `FileSizeRotatePolicy`
- `DateRotatePolicy`

RotatePolicyはLogWriterのプロパティに指定する。

```properties
writerNames=sample

# writerのrotatePolicyにRotatePolicyが実装されたクラスのFQCNを指定する
writer.sample.rotatePolicy=nablarch.core.log.basic.DateRotatePolicy
# 更新時刻（オプション）
writer.sample.rotateTime=12:00
```

## 拡張例

### LogWriterを追加する

新規LogWriterは `LogWriter` インタフェースを実装する。`LogFormatter` を使用する場合は、共通処理を提供する `LogWriterSupport` を継承する。

### LogFormatterを追加する

新規LogFormatterは `LogFormatter` インタフェースを実装する。ログレベル文言を設定で変更可能にする場合は `LogLevelLabelProvider` を使用する。

ログ出力時のパラメータを増やしたい場合は `Logger` のoptionsパラメータを使用する:

```java
public void logInfo(String message, Object... options)
public void logInfo(String message, Throwable cause, Object... options)
```

### ログの出力項目（プレースホルダ）を追加する

1. `LogItem` を実装したクラスを作る
2. `BasicLogFormatter` を継承して `getLogItems()` をオーバーライドし、プレースホルダを追加する

カスタムプレースホルダの設定例:

```properties
writer.appLog.formatter.className=nablarch.core.log.basic.CustomLogFormatter
writer.appLog.formatter.format=$date$ -$logLevel$- $loggerName$ [$bootProcess$] $message$
writer.appLog.formatter.bootProcess=CUSTOM_PROCESS
```

```java
// LogItemを実装したクラスの例
public class CustomBootProcessItem implements LogItem<LogContext> {
    private String bootProcess;
    public CustomBootProcessItem(ObjectSettings settings) {
        bootProcess = settings.getProp("bootProcess");
    }
    @Override
    public String get(LogContext context) {
        return bootProcess;
    }
}

// BasicLogFormatterを継承してプレースホルダを追加する
public class CustomLogFormatter extends BasicLogFormatter {
    @Override
    protected Map<String, LogItem<LogContext>> getLogItems(ObjectSettings settings) {
        Map<String, LogItem<LogContext>> logItems = super.getLogItems(settings);
        logItems.put("$bootProcess$", new CustomBootProcessItem(settings));
        return logItems;
    }
}
```

### ログの初期化メッセージを出力しないようにする

:ref:`log_adaptor` を使用した場合、初期化メッセージは出力されないため本対応は不要。

ログ機能のWriterで初期化メッセージを抑制する手順:
1. ベースWriterクラス（例: `FileLogWriter`）をプロジェクト側にコピーし、初期化ログ出力処理を削除する。
2. `needsToWrite` をオーバーライドし、`initialized.` で始まるメッセージを除外する。
3. 作成したクラスをlog.propertiesに設定する。

```java
private boolean suppressionWriting = true;

@Override
public boolean needsToWrite(final LogContext context) {
    final String message = context.getMessage();
    if (suppressionWriting) {
        if (StringUtil.hasValue(message) && message.startsWith("initialized.")) {
            suppressionWriting = false;
            return false;
        }
    }
    return super.needsToWrite(context);
}
```

```properties
writerNames=sample
writer.sample.className = sample.CustomFileLogWriter
```

## LogWriterで使用するフォーマッタをJsonLogFormatterに変更する

**クラス**: `nablarch.core.log.basic.JsonLogFormatter`

LogWriterのフォーマッタを `JsonLogFormatter` に変更することでJSON形式出力が可能。

```properties
writer.appLog.formatter.className=nablarch.core.log.basic.JsonLogFormatter
writer.appLog.formatter.targets=date,logLevel,message,stackTrace
writer.appLog.formatter.datePattern=yyyy-MM-dd'T'HH:mm:ss.SSS'Z'
```

`targets` プロパティにカンマ区切りで出力項目を指定する。デフォルトは全項目出力。

| 出力項目 | 説明 |
|---|---|
| date | ログ出力要求時点の日時 |
| logLevel | ログレベル |
| loggerName | ロガー設定の名称 |
| runtimeLoggerName | `LoggerManager` からロガー取得に指定した名称 |
| bootProcess | 起動プロセスの識別名 |
| processingSystem | 処理方式の識別名 |
| requestId | ログ出力要求時点のリクエストID |
| executionId | ログ出力要求時点の実行時ID |
| userId | ログ出力要求時点のログインユーザID |
| message | ログメッセージ |
| stackTrace | 例外オブジェクトのスタックトレース |
| payload | オプション情報に指定されたオブジェクト |

> **補足**: `datePattern` および `label`（ログレベルの文言指定）は `BasicLogFormatter` と同様に機能する。

出力例:
```none
{"date":"2021-02-04 12:34:56.789","logLevel":"INFO","message":"hello"}
```

`payload` を出力対象に含む場合、オプション情報の `Map<String, Object>` をJSONオブジェクトとして出力する。

| Javaクラス | JSONによる出力 |
|---|---|
| `String` | JSONの文字列 |
| `Number` およびサブクラス（`Integer`, `Long`, `Short`, `Byte`, `Float`, `Double`, `BigDecimal`, `BigInteger`, `AtomicInteger`, `AtomicLong`） | `toString()` の戻り値をJSONの数値として出力。NaN・無限大はJSONの文字列として出力 |
| `Boolean` | JSONの真理値（`true`/`false`） |
| `Date`, `Calendar` およびサブクラス, `LocalDateTime` | JSONの文字列。デフォルト書式は `"yyyy-MM-dd HH:mm:ss.SSS"`。変更は `datePattern` プロパティで指定 |
| `Map` の実装クラス | JSONのオブジェクト。キーが `String` でない場合や値が `null` の場合はキーも含め出力されない。`null` を出力する場合は `ignoreNullValueMember` に `false` をセット |
| `List` の実装クラス、および配列 | JSONの配列 |
| `null` | JSONの `null`。`Map` の値が `null` のとき、デフォルトでは出力対象外 |
| その他のオブジェクト | `toString()` の戻り値をJSONの文字列 |

出力例（payloadあり）:
```none
{"date":"2021-02-04 12:34:56.789","logLevel":"INFO","message":"addition fields","key1":"value1","key2":123,"key3":true,"key5":"2021-02-04 12:34:56.789"}
```

> **補足**: `JsonLogFormatter` 使用時、オプション情報には `Map<String, Object>` のみセットすること。`Map` オブジェクトは複数指定可能だが、キーが重複した場合はいずれかの値は無視されて出力されない。

## 各種ログで使用するフォーマッタをJSONログ用に差し替える

各種ログのフォーマッタをJSON用クラスに差し替えることで、各種ログが出力する内容もJSON形式で出力できる。

| ログの種類 | JSON版フォーマッタ |
|---|---|
| :ref:`障害ログ <failure_log-json_setting>` | `FailureJsonLogFormatter` |
| :ref:`SQLログ <sql_log-json_setting>` | `SqlJsonLogFormatter` |
| :ref:`パフォーマンスログ <performance_log-json_setting>` | `PerformanceJsonLogFormatter` |
| :ref:`HTTPアクセスログ <http_access_log-json_setting>` | `HttpAccessJsonLogFormatter` |
| :ref:`HTTPアクセスログ（RESTfulウェブサービス用） <jaxrs_access_log-json_setting>` | `JaxRsAccessJsonLogFormatter` |
| :ref:`メッセージングログ <messaging_log-json_setting>` | `MessagingJsonLogFormatter` |

## NablarchバッチのログをJSON形式にする

NablarchバッチのJSON形式ログ出力には、フォーマッタ設定に加えて以下の3つの設定が必要:
1. ApplicationSettingLogFormatterをJSON用に切り替える
2. LauncherLogFormatterをJSON用に切り替える
3. CommitLoggerをJSON用に切り替える

### ApplicationSettingLogFormatterの切り替え

**クラス**: `nablarch.core.log.app.ApplicationSettingJsonLogFormatter`（`ApplicationSettingLogFormatter` の代替）

設定は :ref:`log-app_log_setting` で説明したプロパティファイルに行う。

| プロパティ名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| applicationSettingLogFormatter.className | ○ | | `nablarch.core.log.app.ApplicationSettingJsonLogFormatter` を指定 |
| applicationSettingLogFormatter.appSettingTargets | | `systemSettings` | アプリケーション設定ログの出力項目（業務日付なし）。カンマ区切り。指定可能値: `systemSettings`, `businessDate` |
| applicationSettingLogFormatter.appSettingWithDateTargets | | 全項目 | アプリケーション設定ログの出力項目（業務日付あり）。カンマ区切り。指定可能値: `systemSettings`, `businessDate` |
| applicationSettingLogFormatter.systemSettingItems | | 空（何も出力しない） | 出力するシステム設定値の名前一覧。カンマ区切り |
| applicationSettingLogFormatter.structuredMessagePrefix | | `$JSON$` | フォーマット後メッセージをJSONとして識別するためのマーカー文字列。メッセージ先頭にこのマーカーがある場合、`JsonLogFormatter` はメッセージをJSONデータとして処理する |

```properties
applicationSettingLogFormatter.className=nablarch.core.log.app.ApplicationSettingJsonLogFormatter
applicationSettingLogFormatter.structuredMessagePrefix=$JSON$
applicationSettingLogFormatter.appSettingTargets=systemSettings
applicationSettingLogFormatter.appSettingWithDateTargets=systemSettings,businessDate
applicationSettingLogFormatter.systemSettingItems=dbUser,dbUrl,threadCount
```

### LauncherLogFormatterの切り替え

**クラス**: `nablarch.fw.launcher.logging.LauncherJsonLogFormatter`（`LauncherLogFormatter` の代替）

設定は :ref:`log-app_log_setting` で説明したプロパティファイルに行う。

| プロパティ名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| launcherLogFormatter.className | ○ | | `nablarch.fw.launcher.logging.LauncherJsonLogFormatter` を指定 |
| launcherLogFormatter.startTargets | | 全項目 | 開始ログの出力項目。カンマ区切り。指定可能値: `label`, `commandLineOptions`, `commandLineArguments` |
| launcherLogFormatter.endTargets | | 全項目 | 終了ログの出力項目。カンマ区切り。指定可能値: `label`, `exitCode`, `executeTime` |
| launcherLogFormatter.startLogMsgLabel | | `BATCH BEGIN` | 開始ログのlabelに出力する値 |
| launcherLogFormatter.endLogMsgLabel | | `BATCH END` | 終了ログのlabelに出力する値 |
| launcherLogFormatter.structuredMessagePrefix | | `$JSON$` | フォーマット後メッセージをJSONとして識別するためのマーカー文字列 |

```properties
launcherLogFormatter.className=nablarch.fw.launcher.logging.LauncherJsonLogFormatter
launcherLogFormatter.structuredMessagePrefix=$JSON$
launcherLogFormatter.startTargets=label,commandLineOptions,commandLineArguments
launcherLogFormatter.endTargets=label,exitCode,executionTime
launcherLogFormatter.startLogMsgLabel=BATCH BEGIN
launcherLogFormatter.endLogMsgLabel=BATCH END
```

### CommitLoggerの切り替え

**クラス**: `nablarch.core.log.app.JsonCommitLogger`（`BasicCommitLogger` の代替。`CommitLogger` インターフェース実装）

`JsonCommitLogger` をコンポーネントとして定義する。コンポーネント名は `commitLogger` で定義すること。

```xml
<component name="commitLogger" class="nablarch.core.log.app.JsonCommitLogger">
  <property name="interval" value="${nablarch.commitLogger.interval}" />
</component>
```

## SynchronousFileLogWriterを使用するにあたっての注意事項

> **重要**: `SynchronousFileLogWriter` は複数プロセスからの書き込み用に作成したものであるが、:ref:`障害通知ログ <failure_log>` のように出力頻度が低いログ出力にのみ使用すること。アプリケーションログやアクセスログのように出力頻度の高いログには使用禁止。理由: ロック取得待ちによる性能劣化や競合によるログ消失が発生する可能性がある。また以下の制約がある: (1) ログのローテーションができない (2) 出力されるログの内容が正常でない場合がある。

**クラス**: `nablarch.core.log.basic.SynchronousFileLogWriter`

ロックファイルで排他制御しながらファイルにログを書き込む。ロック取得の待機時間を超えてもロックを取得できない場合、強制的にロックファイルを削除して自身のスレッド用のロックファイルを生成してからログを出力する。強制削除できない場合・ロックファイル生成失敗時・割り込み発生時は、ロックを取得していない状態で強制的にログを出力する。

> **重要**: ロックを取得しない状態で強制的にログを出力する際に複数プロセスからのログ出力が競合すると、ログが正常に出力されない場合がある。

このような障害が発生した場合、強制出力したログに加えて同一のログファイルに障害のログを出力する。`failureCode`プロパティに障害コードを設定することで障害通知ログのフォーマット（障害コードを含む）で出力でき、通常の障害通知ログと同様の方法でログ監視が可能となるため、障害コードの設定を推奨する。

| プロパティ名 | 障害の内容 | ログレベル | メッセージの設定例 | デフォルトで出力するログ |
|---|---|---|---|---|
| failureCodeCreateLockFile | ロックファイルが生成できない | FATAL | ロックファイルの生成に失敗しました。おそらくロックファイルのパスが間違っています。ロックファイルパス=[{0}]。({0}=ロックファイルのパス) | failed to create lock file. perhaps lock file path was invalid. lock file path=[{0}]. |
| failureCodeReleaseLockFile | 生成したロックファイルを解放(削除)できない | FATAL | ロックファイルの削除に失敗しました。ロックファイルパス=[{0}]。({0}=ロックファイルのパス) | failed to delete lock file. lock file path=[{0}]. |
| failureCodeForceDeleteLockFile | 解放されないロックファイルを強制削除できない | FATAL | ロックファイルの強制削除に失敗しました。ロックファイルが不正に開かれています。ロックファイルパス=[{0}]。({0}=ロックファイルのパス) | failed to delete lock file forcedly. lock file was opened illegally. lock file path=[{0}]. |
| failureCodeInterruptLockWait | ロック取得待ちでスレッドをスリープしている際に割り込みが発生 | FATAL | ロック取得中に割り込みが発生しました。 | interrupted while waiting for lock retry. |

```properties
writerNames=monitorLog

writer.monitorLog.className=nablarch.core.log.basic.SynchronousFileLogWriter
writer.monitorLog.filePath=/var/log/app/monitor.log
writer.monitorLog.encoding=UTF-8
writer.monitorLog.outputBufferSize=8
writer.monitorLog.formatter.className=nablarch.core.log.basic.BasicLogFormatter
writer.monitorLog.level=ERROR
writer.monitorLog.lockFilePath=/var/log/lock/monitor.lock
writer.monitorLog.lockRetryInterval=10
writer.monitorLog.lockWaitTime=3000
writer.monitorLog.failureCodeCreateLockFile=MSG00101
writer.monitorLog.failureCodeReleaseLockFile=MSG00102
writer.monitorLog.failureCodeForceDeleteLockFile=MSG00103
writer.monitorLog.failureCodeInterruptLockWait=MSG00104
```

> **重要**: `maxFileSize`プロパティを指定するとログのローテーションが発生しログ出力ができなくなる場合があるため指定しないこと。

> **重要**: 障害コードを設定した場合、障害通知ログのフォーマットで同一のログファイルにログが出力されるが、障害解析ログは出力されない点に注意すること。

## LogPublisherの使い方

**クラス**: `nablarch.core.log.basic.LogPublisher`, `nablarch.core.log.basic.LogContext`, `nablarch.core.log.basic.LogListener`

`LogPublisher` は、出力されたログ情報(`LogContext`)を登録された `LogListener` に連携する機能を提供する。出力されたログ情報に対してプログラム的に処理を行いたい場合に使用する。

1. `LogPublisher`を`LogWriter`として設定する:

```properties
writerNames=monitorFile,appFile,stdout,logPublisher

writer.logPublisher.className=nablarch.core.log.basic.LogPublisher
writer.logPublisher.formatter.className=nablarch.core.log.basic.BasicLogFormatter

loggers.ROO.nameRegex=.*
loggers.ROO.level=INFO
loggers.ROO.writerNames=appFile,stdout,logPublisher

loggers.MON.nameRegex=MONITOR
loggers.MON.level=ERROR
loggers.MON.writerNames=monitorFile,logPublisher
```

2. `LogListener`の実装クラスを作成する:

```java
package example.micrometer.log;

import nablarch.core.log.basic.LogContext;
import nablarch.core.log.basic.LogListener;

public class CustomLogListener implements LogListener {

    @Override
    public void onWritten(LogContext context) {
        // LogContext を使った処理を実装する
    }
}
```

3. 作成した`LogListener`を`LogPublisher`の`static`メソッドを介して登録する:

```java
LogListener listener = new CustomLogListener();
LogPublisher.addListener(listener);
```

登録した`LogListener`は、`removeListener(LogListener)` または `removeAllListeners()` で削除できる。

## ログレベルの定義

| ログレベル | 説明 |
|---|---|
| FATAL | アプリケーションの継続が不可能になる深刻な問題。監視必須、即通報・即対応が必要。 |
| ERROR | アプリケーションの継続に支障をきたす問題。監視必須、FATALほどの緊急性はない。 |
| WARN | 放置するとアプリケーション継続に支障をきたす恐れがある事象。できれば監視。 |
| INFO | 本番運用時にアプリケーション情報を出力するレベル。アクセスログ・統計ログが該当。 |
| DEBUG | 開発時のデバッグ情報。SQLログ・性能ログが該当。 |
| TRACE | 開発時にデバッグ情報より細かい情報を出力したい場合に使用。 |

ログレベルはFATALからTRACEに向かって順にレベルが低くなる。設定で指定されたレベル以上のログをすべて出力する（例: WARN指定 → FATAL/ERROR/WARNのみ出力）。

> **補足**: 本番運用時はINFOレベルでのログ出力を想定。ログファイルのサイズが肥大化しないよう、プロジェクト毎にログの出力内容を規定すること。

> **補足**: フレームワークが出力するログについては、:ref:`log-fw_log_policy` を参照すること。

## フレームワークのログ出力方針

| ログレベル | 出力方針 |
|---|---|
| FATAL/ERROR | 障害ログ出力時に使用。原則1件の障害に対して1件の障害ログを出力。実行制御基盤では単一のハンドラ（例外を処理するハンドラ）により障害通知ログを出力する。 |
| WARN | 障害発生時に連鎖して例外が発生した場合など、障害ログとして出力できない例外をWARNレベルで出力（例: 業務処理とトランザクション終了処理の両方で例外発生時、業務処理の例外を障害ログに、トランザクション終了処理の例外をWARNで出力）。 |
| INFO | アプリケーションの実行状況に関連するエラーを検知した場合に出力（例: URLパラメータの改竄エラー、認可チェックエラー）。 |
| DEBUG | アプリケーション開発時のデバッグ情報を出力。DEBUGレベル設定で開発に必要な情報が出力される。 |
| TRACE | フレームワーク開発時のデバッグ情報を出力。アプリケーション開発での使用は想定していない。 |

## log4jとの機能比較

| 機能 | Nablarch | log4j |
|---|---|---|
| ログの出力有無をログレベルで制御できる | ○ (:ref:`log-basic_setting`) | ○ |
| ログの出力有無をカテゴリ(パッケージ単位や名前など)で制御できる | ○ (:ref:`log-basic_setting`) | ○ |
| 1つのログを複数の出力先に出力できる | ○ (:ref:`log-basic_setting`) | ○ |
| ログを標準出力に出力できる | ○ (:ref:`log-log_writers`) | ○ |
| ログをファイルに出力できる | ○ (:ref:`log-log_writers`) | ○ |
| ファイルサイズによるログファイルのローテーションができる | △ [1] (:ref:`log-rotation`) | ○ |
| 日時によるログファイルのローテーションができる | △ [1] (:ref:`log-rotation`) | ○ |
| ログをメールで送信できる | × [2] | ○ |
| ログをTelnetで送信できる | × [2] | ○ |
| ログをSyslogで送信できる | × [2] | ○ |
| ログをWindows NTのイベントログに追加できる | × [2] | ○ |
| データベースにログを出力できる | × [2] | ○ |
| ログを非同期で出力できる | × [2] | ○ |
| ログのフォーマットをパターン文字列で指定できる | ○ (:ref:`log-log_format`) | ○ |
| 障害ログを出力できる | ○ (:ref:`failure_log`) | — |
| HTTPアクセスログを出力できる | ○ (:ref:`http_access_log`) | — |
| SQLログを出力できる | ○ (:ref:`sql_log`) | — |
| パフォーマンスログを出力できる | ○ (:ref:`performance_log`) | — |
| メッセージングログを出力できる | ○ (:ref:`messaging_log`) | — |

[1] Nablarchのログ出力はファイルの世代管理を提供していないため、一部提供ありとしている。
[2] :ref:`log_adaptor` を使用するか、プロジェクトで作成する（作成方法は :ref:`log-add_log_writer` を参照）。
