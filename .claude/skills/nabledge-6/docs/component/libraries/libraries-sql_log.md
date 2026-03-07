# SQLログの出力

## SQLログの出力方針

SQLログはディスクフルやパフォーマンスへの影響の可能性があるため、開発時の使用を想定し、DEBUGレベル以下で出力する。

| ログレベル | ロガー名 | 出力内容 |
|---|---|---|
| DEBUG | SQL | SQL文、実行時間、件数（検索件数や更新件数など）、トランザクションの処理結果（コミット又はロールバック） |
| TRACE | SQL | SQLパラメータ（バインド変数の値） |

**log.propertiesの設定例**:
```properties
writerNames=appLog

# アプリケーションログの出力先
writer.appLog.className=nablarch.core.log.basic.FileLogWriter
writer.appLog.filePath=/var/log/app/app.log
writer.appLog.encoding=UTF-8
writer.appLog.maxFileSize=10000
writer.appLog.formatter.className=nablarch.core.log.basic.BasicLogFormatter
writer.appLog.formatter.format=$date$ -$logLevel$- $runtimeLoggerName$ [$executionId$] boot_proc = [$bootProcess$] proc_sys = [$processingSystem$] req_id = [$requestId$] usr_id = [$userId$] $message$$information$$stackTrace$

availableLoggersNamesOrder=SQL,ROO

# アプリケーションログの設定
loggers.ROO.nameRegex=.*
loggers.ROO.level=INFO
loggers.ROO.writerNames=appLog

# SQLログの設定
loggers.SQL.nameRegex=SQL
loggers.SQL.level=TRACE
loggers.SQL.writerNames=appLog
```

**app-log.propertiesの設定例**（SqlLogFormatterフォーマット設定）:
```properties
sqlLogFormatter.startRetrieveFormat=$methodName$\n\tSQL = [$sql$]\n\tstart_position = [$startPosition$] size = [$size$]\n\tquery_timeout = [$queryTimeout$] fetch_size = [$fetchSize$]\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endRetrieveFormat=$methodName$\n\texecute_time(ms) = [$executeTime$] retrieve_time(ms) = [$retrieveTime$] count = [$count$]
sqlLogFormatter.startExecuteFormat=$methodName$\n\tSQL = [$sql$]\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endExecuteFormat=$methodName$\n\texecute_time(ms) = [$executeTime$]
sqlLogFormatter.startExecuteQueryFormat=$methodName$\n\tSQL = [$sql$]\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endExecuteQueryFormat=$methodName$\n\texecute_time(ms) = [$executeTime$]
sqlLogFormatter.startExecuteUpdateFormat=$methodName$\n\tSQL = [$sql$]\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endExecuteUpdateFormat=$methodName$\n\texecute_time(ms) = [$executeTime$] update_count = [$updateCount$]
sqlLogFormatter.startExecuteBatchFormat=$methodName$\n\tSQL = [$sql$]\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endExecuteBatchFormat=$methodName$\n\texecute_time(ms) = [$executeTime$] batch_count = [$updateCount$]
```

## SQLログの設定

SQLログの設定は :ref:`log-app_log_setting` で説明したプロパティファイルに行う。

| プロパティ名 | 説明 | 利用可能なプレースホルダ |
|---|---|---|
| `sqlLogFormatter.className` | `SqlLogFormatter` 実装クラス。差し替える場合に指定 | — |
| `sqlLogFormatter.startRetrieveFormat` | `SqlPStatement#retrieve` 開始時フォーマット | $methodName$, $sql$, $startPosition$, $size$, $queryTimeout$, $fetchSize$, $additionalInfo$ |
| `sqlLogFormatter.endRetrieveFormat` | SqlPStatement#retrieve 終了時フォーマット | $methodName$, $executeTime$, $retrieveTime$, $count$ |
| `sqlLogFormatter.startExecuteFormat` | `SqlPStatement#execute` 開始時フォーマット | $methodName$, $sql$, $additionalInfo$ |
| `sqlLogFormatter.endExecuteFormat` | SqlPStatement#execute 終了時フォーマット | $methodName$, $executeTime$ |
| `sqlLogFormatter.startExecuteQueryFormat` | `SqlPStatement#executeQuery` 開始時フォーマット | $methodName$, $sql$, $additionalInfo$ |
| `sqlLogFormatter.endExecuteQueryFormat` | SqlPStatement#executeQuery 終了時フォーマット | $methodName$, $executeTime$ |
| `sqlLogFormatter.startExecuteUpdateFormat` | `SqlPStatement#executeUpdate` 開始時フォーマット | $methodName$, $sql$, $additionalInfo$ |
| `sqlLogFormatter.endExecuteUpdateFormat` | SqlPStatement#executeUpdate 終了時フォーマット | $methodName$, $executeTime$, $updateCount$ |
| `sqlLogFormatter.startExecuteBatchFormat` | `SqlStatement#executeBatch` 開始時フォーマット | $methodName$, $sql$, $additionalInfo$ |
| `sqlLogFormatter.endExecuteBatchFormat` | SqlStatement#executeBatch 終了時フォーマット | $methodName$, $executeTime$, $batchCount$ |

**デフォルトフォーマット一覧:**

| プロパティ名 | デフォルトフォーマット |
|---|---|
| `startRetrieveFormat` | `$methodName$\n\tSQL = [$sql$]\n\tstart_position = [$startPosition$] size = [$size$]\n\tquery_timeout = [$queryTimeout$] fetch_size = [$fetchSize$]\n\tadditional_info:\n\t$additionalInfo$` |
| `endRetrieveFormat` | `$methodName$\n\texecute_time(ms) = [$executeTime$] retrieve_time(ms) = [$retrieveTime$] count = [$count$]` |
| `startExecuteFormat` | `$methodName$\n\tSQL = [$sql$]\n\tadditional_info:\n\t$additionalInfo$` |
| `endExecuteFormat` | `$methodName$\n\texecute_time(ms) = [$executeTime$]` |
| `startExecuteQueryFormat` | `$methodName$\n\tSQL = [$sql$]\n\tadditional_info:\n\t$additionalInfo$` |
| `endExecuteQueryFormat` | `$methodName$\n\texecute_time(ms) = [$executeTime$]` |
| `startExecuteUpdateFormat` | `$methodName$\n\tSQL = [$sql$]\n\tadditional_info:\n\t$additionalInfo$` |
| `endExecuteUpdateFormat` | `$methodName$\n\texecute_time(ms) = [$executeTime$] update_count = [$updateCount$]` |
| `startExecuteBatchFormat` | `$methodName$\n\tSQL = [$sql$]\n\tadditional_info:\n\t$additionalInfo$` |
| `endExecuteBatchFormat` | `$methodName$\n\texecute_time(ms) = [$executeTime$] batch_count = [$updateCount$]` |

> **注意**: `endExecuteBatchFormat` のデフォルトフォーマットではプレースホルダとして `$updateCount$` が使用されている（`$batchCount$` ではない）。これはソースドキュメント内の不整合であり、プロパティの説明では `$batchCount$` が利用可能なプレースホルダとして列挙されているにもかかわらず、デフォルト値では `$updateCount$` が用いられている。

設定例:
```properties
sqlLogFormatter.className=nablarch.core.db.statement.SqlLogFormatter
sqlLogFormatter.startRetrieveFormat=$methodName$\n\tSQL:$sql$\n\tstart:$startPosition$ size:$size$\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endRetrieveFormat=$methodName$\n\texe:$executeTime$ms ret:$retrieveTime$ms count:$count$
sqlLogFormatter.startExecuteFormat=$methodName$\n\tSQL:$sql$\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endExecuteFormat=$methodName$\n\texe:$executeTime$ms
sqlLogFormatter.startExecuteQueryFormat=$methodName$\n\tSQL:$sql$\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endExecuteQueryFormat=$methodName$\n\texe:$executeTime$ms
sqlLogFormatter.startExecuteUpdateFormat=$methodName$\n\tSQL:$sql$\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endExecuteUpdateFormat=$methodName$\n\texe:$executeTime$ms count:$updateCount$
sqlLogFormatter.startExecuteBatchFormat=$methodName$\n\tSQL:$sql$\n\tadditional_info:\n\t$additionalInfo$
sqlLogFormatter.endExecuteBatchFormat=$methodName$\n\texe:$executeTime$ms count:$updateCount$
```

## JSON形式の構造化ログとして出力する

:ref:`log-json_log_setting` 設定でログをJSON形式で出力できるが、`SqlLogFormatter` ではSQLログの各項目はmessageの値に文字列として出力される。各項目もJSONの値として出力するには `SqlJsonLogFormatter` を使用する。設定は :ref:`log-app_log_setting` で説明したプロパティファイルに行う。

| プロパティ名 | 必須 | 説明 |
|---|---|---|
| `sqlLogFormatter.className` | ○ | `nablarch.core.db.statement.SqlJsonLogFormatter` を指定 |
| `sqlLogFormatter.startRetrieveTargets` | | SqlPStatement#retrieve 開始時の出力項目（カンマ区切り）。指定可能: methodName, sql, startPosition, size, queryTimeout, fetchSize, additionalInfo。デフォルトは全項目 |
| `sqlLogFormatter.endRetrieveTargets` | | SqlPStatement#retrieve 終了時の出力項目。指定可能: methodName, executeTime, retrieveTime, count。デフォルトは全項目 |
| `sqlLogFormatter.startExecuteTargets` | | SqlPStatement#execute 開始時の出力項目。指定可能: methodName, sql, additionalInfo。デフォルトは全項目 |
| `sqlLogFormatter.endExecuteTargets` | | SqlPStatement#execute 終了時の出力項目。指定可能: methodName, executeTime。デフォルトは全項目 |
| `sqlLogFormatter.startExecuteQueryTargets` | | SqlPStatement#executeQuery 開始時の出力項目。指定可能: methodName, sql, additionalInfo。デフォルトは全項目 |
| `sqlLogFormatter.endExecuteQueryTargets` | | SqlPStatement#executeQuery 終了時の出力項目。指定可能: methodName, executeTime。デフォルトは全項目 |
| `sqlLogFormatter.startExecuteUpdateTargets` | | SqlPStatement#executeUpdate 開始時の出力項目。指定可能: methodName, sql, additionalInfo。デフォルトは全項目 |
| `sqlLogFormatter.endExecuteUpdateTargets` | | SqlPStatement#executeUpdate 終了時の出力項目。指定可能: methodName, executeTime, updateCount。デフォルトは全項目 |
| `sqlLogFormatter.startExecuteBatchTargets` | | SqlStatement#executeBatch 開始時の出力項目。指定可能: methodName, sql, additionalInfo。デフォルトは全項目 |
| `sqlLogFormatter.endExecuteBatchTargets` | | SqlStatement#executeBatch 終了時の出力項目。指定可能: methodName, executeTime, batchCount。デフォルトは全項目 |
| `sqlLogFormatter.structuredMessagePrefix` | | メッセージ先頭に付与するマーカー文字列。`JsonLogFormatter` のマーカー文字列と一致する場合、JSONデータとして処理される。デフォルト: `"$JSON$"` |

> **重要**: `structuredMessagePrefix` を変更する場合は、LogWriterの `structuredMessagePrefix` プロパティで `JsonLogFormatter` にも同じ値を設定すること（:ref:`log-basic_setting` 参照）。

設定例:
```properties
sqlLogFormatter.className=nablarch.core.db.statement.SqlJsonLogFormatter
sqlLogFormatter.structuredMessagePrefix=$JSON$
sqlLogFormatter.startRetrieveTargets=methodName,sql,startPosition,size,additionalInfo
sqlLogFormatter.endRetrieveTargets=methodName,executeTime,retrieveTime,count
sqlLogFormatter.startExecuteTargets=methodName,sql,additionalInfo
sqlLogFormatter.endExecuteTargets=methodName,executeTime
sqlLogFormatter.startExecuteQueryTargets=methodName,sql,additionalInfo
sqlLogFormatter.endExecuteQueryTargets=methodName,executeTime
sqlLogFormatter.startExecuteUpdateTargets=methodName,sql,additionalInfo
sqlLogFormatter.endExecuteUpdateTargets=methodName,executeTime,updateCount
sqlLogFormatter.startExecuteBatchTargets=methodName,sql,additionalInfo
sqlLogFormatter.endExecuteBatchTargets=methodName,executeTime,batchCount
```
