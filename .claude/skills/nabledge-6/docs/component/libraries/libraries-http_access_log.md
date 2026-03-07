# HTTPアクセスログの出力

## HTTPアクセスログの出力方針

HTTPアクセスログ出力に必要なハンドラ:

1. :ref:`http_access_log_handler` - リクエスト処理開始時と終了時のログ出力
2. :ref:`nablarch_tag_handler` - hiddenパラメータ復号後のログ出力（hiddenパラメータについては :ref:`hidden暗号化<tag-hidden_encryption>` 参照）
3. :ref:`http_request_java_package_mapping` - ディスパッチ先クラス決定後のログ出力

リクエストパラメータを含むリクエスト情報を出力することで証跡ログ要件を満たせる場合は、HTTPアクセスログと証跡ログを兼用できる。

**出力方針**: ログレベル `INFO`、ロガー名 `HTTP_ACCESS`（アプリケーションログに出力）

**log.propertiesの設定例**:
```properties
writerNames=appLog

writer.appLog.className=nablarch.core.log.basic.FileLogWriter
writer.appLog.filePath=/var/log/app/app.log
writer.appLog.encoding=UTF-8
writer.appLog.maxFileSize=10000
writer.appLog.formatter.className=nablarch.core.log.basic.BasicLogFormatter
writer.appLog.formatter.format=$date$ -$logLevel$- $runtimeLoggerName$ [$executionId$] boot_proc = [$bootProcess$] proc_sys = [$processingSystem$] req_id = [$requestId$] usr_id = [$userId$] $message$$information$$stackTrace$

availableLoggersNamesOrder=ACC,ROO

loggers.ROO.nameRegex=.*
loggers.ROO.level=INFO
loggers.ROO.writerNames=appLog

loggers.ACC.nameRegex=HTTP_ACCESS
loggers.ACC.level=INFO
loggers.ACC.writerNames=appLog
```

**app-log.propertiesの設定例**（`HttpAccessLogFormatter`設定プロパティ）:
```properties
#httpAccessLogFormatter.className=
#httpAccessLogFormatter.datePattern=
#httpAccessLogFormatter.maskingChar=
#httpAccessLogFormatter.maskingPatterns=
#httpAccessLogFormatter.parametersSeparator=
#httpAccessLogFormatter.sessionScopeSeparator=
#httpAccessLogFormatter.beginOutputEnabled=
#httpAccessLogFormatter.parametersOutputEnabled=
#httpAccessLogFormatter.dispatchingClassOutputEnabled=
#httpAccessLogFormatter.endOutputEnabled=
httpAccessLogFormatter.beginFormat=@@@@ BEGIN @@@@ rid = [$requestId$] uid = [$userId$] sid = [$sessionId$]\
                                      \n\turl          = [$url$$query$]\
                                      \n\tmethod      = [$method$]\
                                      \n\tport        = [$port$]\
                                      \n\tclient_ip   = [$clientIpAddress$]\
                                      \n\tclient_host = [$clientHost$]
httpAccessLogFormatter.parametersFormat=@@@@ PARAMETERS @@@@\n\tparameters  = [$parameters$]
httpAccessLogFormatter.dispatchingClassFormat=@@@@ DISPATCHING CLASS @@@@ class = [$dispatchingClass$]
httpAccessLogFormatter.endFormat=@@@@ END @@@@ rid = [$requestId$] uid = [$userId$] sid = [$sessionId$] url = [$url$$query$] method = [$method$] status_code = [$statusCode$] content_path = [$contentPath$]\
                                    \n\tstart_time     = [$startTime$]\
                                    \n\tend_time       = [$endTime$]\
                                    \n\texecution_time = [$executionTime$]\
                                    \n\tmax_memory     = [$maxMemory$]\
                                    \n\tfree_memory    = [$freeMemory$]
```

## HTTPアクセスログの設定

設定は :ref:`log-app_log_setting` で説明したプロパティファイルに行う。

| プロパティ名 | デフォルト値 | 説明 |
|---|---|---|
| httpAccessLogFormatter.className | | `HttpAccessLogFormatter` を実装したクラス。差し替える場合に指定する。 |
| httpAccessLogFormatter.beginFormat | 下記参照 | リクエスト処理開始時のログ出力フォーマット |
| httpAccessLogFormatter.parametersFormat | 下記参照 | hiddenパラメータ復号後のログ出力フォーマット |
| httpAccessLogFormatter.dispatchingClassFormat | 下記参照 | ディスパッチ先クラス決定後のログ出力フォーマット |
| httpAccessLogFormatter.endFormat | 下記参照 | リクエスト処理終了時のログ出力フォーマット |
| httpAccessLogFormatter.datePattern | `yyyy-MM-dd HH:mm:ss.SSS` | 日時パターン（SimpleDateFormat構文） |
| httpAccessLogFormatter.maskingPatterns | | マスク対象パラメータ名/変数名（正規表現、カンマ区切り、大文字小文字区別なし） |
| httpAccessLogFormatter.maskingChar | `*` | マスク文字 |
| httpAccessLogFormatter.parametersSeparator | `\n\t\t` | リクエストパラメータのセパレータ |
| httpAccessLogFormatter.sessionScopeSeparator | `\n\t\t` | セッションスコープ情報のセパレータ |
| httpAccessLogFormatter.beginOutputEnabled | `true` | リクエスト処理開始時の出力有効/無効 |
| httpAccessLogFormatter.parametersOutputEnabled | `true` | hiddenパラメータ復号後の出力有効/無効 |
| httpAccessLogFormatter.dispatchingClassOutputEnabled | `true` | ディスパッチ先クラス決定後の出力有効/無効 |
| httpAccessLogFormatter.endOutputEnabled | `true` | リクエスト処理終了時の出力有効/無効 |

**beginFormatのプレースホルダ**: `$requestId$`, `$userId$`, `$url$`, `$query$`, `$port$`, `$method$`, `$sessionId$`, `$sessionStoreId$`, `$parameters$`, `$sessionScope$`, `$clientIpAddress$`, `$clientHost$`, `$clientUserAgent$`

デフォルトフォーマット（beginFormat）:
```bash
@@@@ BEGIN @@@@ rid = [$requestId$] uid = [$userId$] sid = [$sessionId$]
    \n\turl         = [$url$]
    \n\tmethod      = [$method$]
    \n\tport        = [$port$]
    \n\tclient_ip   = [$clientIpAddress$]
    \n\tclient_host = [$clientHost$]
```

> **補足**: リクエストパラメータは :ref:`hidden暗号化<tag-hidden_encryption>` の復号前の状態となる。

> **重要**: リクエストID・ユーザIDを出力する場合、取得元が `ThreadContext` のためハンドラ構成に :ref:`thread_context_handler` が必要。ユーザIDは :ref:`thread_context_handler-user_id_attribute_setting` を参照してセッションに値を設定すること。

デフォルトフォーマット（parametersFormat）:
```bash
@@@@ PARAMETERS @@@@
    \n\tparameters  = [$parameters$]
```

**dispatchingClassFormatのプレースホルダ**: `$dispatchingClass$`, `$sessionStoreId$`

デフォルトフォーマット（dispatchingClassFormat）: `@@@@ DISPATCHING CLASS @@@@ class = [$dispatchingClass$]`

**endFormatのプレースホルダ**: `$dispatchingClass$`, `$statusCode$`, `$responseStatusCode$`, `$contentPath$`, `$startTime$`, `$endTime$`, `$executionTime$`, `$maxMemory$`, `$freeMemory$`, `$sessionStoreId$`

デフォルトフォーマット（endFormat）:
```bash
@@@@ END @@@@ rid = [$requestId$] uid = [$userId$] sid = [$sessionId$] url = [$url$] status_code = [$statusCode$] content_path = [$contentPath$]
    \n\tstart_time     = [$startTime$]
    \n\tend_time       = [$endTime$]
    \n\texecution_time = [$executionTime$]
    \n\tmax_memory     = [$maxMemory$]
    \n\tfree_memory    = [$freeMemory$]
```

> **補足**: ステータスコード(内部)は :ref:`http_access_log_handler` の復路時点のコード。ステータスコード(クライアント)は :ref:`http_response_handler` でクライアントに返却するコード（変換ルールは :ref:`http_response_handler-convert_status_code` 参照）。本ログ出力時点では確定していないが同じ機能で導出する。

> **重要**: `ステータスコード(クライアント)` はHTTPアクセスログハンドラ後にシステムエラー（JSPエラー等）が発生した場合、実際の内部コードと異なることがある。障害監視ログが発生した際はこの値が正しくない可能性を考慮すること。

設定例:
```properties
httpAccessLogFormatter.className=nablarch.fw.web.handler.HttpAccessLogFormatter
httpAccessLogFormatter.beginFormat=> sid = [$sessionId$] @@@@ BEGIN @@@@\n\turl = [$url$]\n\tmethod = [$method$]
httpAccessLogFormatter.parametersFormat=> sid = [$sessionId$] @@@@ PARAMETERS @@@@\n\tparameters  = [$parameters$]
httpAccessLogFormatter.dispatchingClassFormat=> sid = [$sessionId$] @@@@ DISPATCHING CLASS @@@@ class = [$dispatchingClass$]
httpAccessLogFormatter.endFormat=< sid = [$sessionId$] @@@@ END @@@@ url = [$url$] status_code = [$statusCode$] content_path = [$contentPath$]
httpAccessLogFormatter.datePattern="yyyy-MM-dd HH:mm:ss.SSS"
httpAccessLogFormatter.maskingChar=#
httpAccessLogFormatter.maskingPatterns=password,mobilePhoneNumber
httpAccessLogFormatter.parametersSeparator=,
httpAccessLogFormatter.sessionScopeSeparator=,
httpAccessLogFormatter.beginOutputEnabled=true
httpAccessLogFormatter.parametersOutputEnabled=true
httpAccessLogFormatter.dispatchingClassOutputEnabled=true
httpAccessLogFormatter.endOutputEnabled=true
```

## JSON形式の構造化ログとして出力する

デフォルトの `HttpAccessLogFormatter` では各項目はmessageの値に文字列として出力される。各項目もJSONの値として出力するには `HttpAccessJsonLogFormatter` を使用する。設定は :ref:`log-app_log_setting` のプロパティファイルに行う。

| プロパティ名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| httpAccessLogFormatter.className | ○ | | `nablarch.fw.web.handler.HttpAccessJsonLogFormatter` を指定 |
| httpAccessLogFormatter.beginTargets | | label,requestId,userId,sessionId,url,port,method,clientIpAddress,clientHost | リクエスト処理開始時のログ出力項目（カンマ区切り） |
| httpAccessLogFormatter.parametersTargets | | label,parameters | hiddenパラメータ復号後のログ出力項目（カンマ区切り） |
| httpAccessLogFormatter.dispatchingClassTargets | | label,dispatchingClass | ディスパッチ先クラス決定後のログ出力項目（カンマ区切り） |
| httpAccessLogFormatter.endTargets | | label,requestId,userId,sessionId,url,statusCode,contentPath,startTime,endTime,executionTime,maxMemory,freeMemory | リクエスト処理終了時のログ出力項目（カンマ区切り） |
| httpAccessLogFormatter.datePattern | | `yyyy-MM-dd HH:mm:ss.SSS` | 日時パターン（SimpleDateFormat構文） |
| httpAccessLogFormatter.maskingPatterns | | | マスク対象パラメータ名/変数名（正規表現、カンマ区切り、大文字小文字区別なし、部分一致） |
| httpAccessLogFormatter.maskingChar | | `*` | マスク文字 |
| httpAccessLogFormatter.beginOutputEnabled | | `true` | 開始時出力有効/無効 |
| httpAccessLogFormatter.parametersOutputEnabled | | `true` | パラメータ出力有効/無効 |
| httpAccessLogFormatter.dispatchingClassOutputEnabled | | `true` | ディスパッチ後出力有効/無効 |
| httpAccessLogFormatter.endOutputEnabled | | `true` | 終了時出力有効/無効 |
| httpAccessLogFormatter.beginLabel | | `"HTTP ACCESS BEGIN"` | 開始時ログのlabel値 |
| httpAccessLogFormatter.parametersLabel | | `"PARAMETERS"` | パラメータログのlabel値 |
| httpAccessLogFormatter.dispatchingClassLabel | | `"DISPATCHING CLASS"` | ディスパッチ後ログのlabel値 |
| httpAccessLogFormatter.endLabel | | `"HTTP ACCESS END"` | 終了時ログのlabel値 |
| httpAccessLogFormatter.structuredMessagePrefix | | `"$JSON$"` | JSONデータ識別マーカー。メッセージ先頭に付与する。 |

> **重要**: `structuredMessagePrefix` を変更する場合は、LogWriterの `structuredMessagePrefix` プロパティで `JsonLogFormatter` にも同じ値を設定すること（ :ref:`log-basic_setting` 参照）。

**beginTargetsの指定可能項目**: label, requestId, userId, sessionId, sessionStoreId, url, port, method, queryString, parameters, sessionScope, clientIpAddress, clientHost, clientUserAgent

**endTargetsの指定可能項目**: label, requestId, userId, sessionId, sessionStoreId, url, dispatchingClass, statusCode, responseStatusCode, contentPath, startTime, endTime, executionTime, maxMemory, freeMemory

**dispatchingClassTargetsの指定可能項目**: label, sessionId, sessionStoreId, dispatchingClass

設定例:
```properties
httpAccessLogFormatter.className=nablarch.fw.web.handler.HttpAccessJsonLogFormatter
httpAccessLogFormatter.structuredMessagePrefix=$JSON$
httpAccessLogFormatter.beginTargets=sessionId,url,method
httpAccessLogFormatter.parametersTargets=sessionId,parameters
httpAccessLogFormatter.dispatchingClassTargets=sessionId,dispatchingClass
httpAccessLogFormatter.endTargets=sessionId,url,statusCode,contentPath
httpAccessLogFormatter.beginLabel=HTTP ACCESS BEGIN
httpAccessLogFormatter.parametersLabel=PARAMETERS
httpAccessLogFormatter.dispatchingClassLabel=DISPATCHING CLASS
httpAccessLogFormatter.endLabel=HTTP ACCESS END
```

## セッションストアIDについて

セッションストアIDを出力に含めた場合、 :ref:`session_store` が発行するセッション識別IDが出力される。

> **重要**: セッションストアIDをログに出力する場合、 :ref:`http_access_log_handler` は :ref:`session_store_handler` より後に配置しなければならない（ :ref:`session_store_handler` の往路で記録された値を使用するため）。

セッションストアIDはリクエスト処理開始時の状態で固定されるため、以下の仕様となる:
- セッションストアIDが発行されていないリクエストでは、途中でIDが発行されたとしても、同一リクエスト内で出力されるセッションストアIDは全て空になる
- 途中で `セッションを破棄` したり `IDを変更` しても、ログに出力される値はリクエスト処理開始時のものから変化しない
