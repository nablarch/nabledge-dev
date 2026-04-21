# Nablarchバッチアプリケーションのエラー処理

## バッチ処理をリランできるようにする

Nablarchバッチアプリケーションでは、ファイル入力を除き、
バッチ処理をリランできるようにする機能を提供していない。

そのため、処理対象レコードにステータスを持たせ、
処理成功や失敗時にステータスを変更するといった、
アプリケーションでの設計と実装が必要となる。
処理成功や失敗時のステータス変更の実装方法については、
トランザクション終了時に任意の処理を実行したい を参照。

ファイル入力については、
`ResumeDataReader (レジューム機能付き読み込み)`
を使用することで、障害発生ポイントからの再実行ができる。

<details>
<summary>keywords</summary>

ResumeDataReader, nablarch.fw.reader.ResumeDataReader, リラン, 再実行, ステータス管理, ファイル入力, 障害復旧

</details>

## バッチ処理でエラー発生時に処理を継続する

エラー発生時の処理継続は、 常駐バッチ のみ対応している。
都度起動バッチ は対応していない。

常駐バッチ では、
`TransactionAbnormalEnd`
を送出すると、 リトライハンドラ により処理が継続される。
ただし、 バッチ処理をリランできるようにする に記載した内容で、
バッチ処理がリランできるようになっている必要がある。

> **Tip:** `都度起動バッチ<nablarch_batch-each_time_batch>` で extdoc:`TransactionAbnormalEnd<nablarch.fw.results.TransactionAbnormalEnd>` が送出されると、バッチ処理が異常終了となる。

<details>
<summary>keywords</summary>

TransactionAbnormalEnd, nablarch.fw.results.TransactionAbnormalEnd, エラー継続, 常駐バッチ, 都度起動バッチ, retry_handler, 処理継続

</details>

## バッチ処理を異常終了にする

アプリケーションでエラーを検知した場合に、
処理を継続せずにバッチ処理を異常終了させたい場合がある。

Nablarchバッチアプリケーションでは、
`ProcessAbnormalEnd`
を送出すると、バッチ処理を異常終了にできる。
`ProcessAbnormalEnd`
が送出された場合、プロセス終了コードはこのクラスに指定された値となる。

<details>
<summary>keywords</summary>

ProcessAbnormalEnd, nablarch.fw.launcher.ProcessAbnormalEnd, 異常終了, プロセス終了コード, バッチ異常終了

</details>
