**結論**: Nablarchバッチのエラーハンドリングは、バッチ種別によって方針が異なります。

- **都度起動バッチ**: `TransactionAbnormalEnd` が送出されるとバッチ処理が異常終了します。
- **常駐バッチ**: `TransactionAbnormalEnd` を送出すると `RetryHandler` により処理が継続されます（バッチ処理がリランできる設計であることが前提）。

ProcessAbnormalEnd 異常終了 プロセス終了コード ステータス

リラン: バッチ処理がリランできる設計

ResumeDataReader: 処理再開用リーダ
