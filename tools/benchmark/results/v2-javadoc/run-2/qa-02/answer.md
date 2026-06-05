必要なセクションが揃いました。回答を生成します。

---

**結論**: Nablarchバッチの **DB to DBパターン（都度起動バッチ）** で実装します。`DatabaseRecordReader` でDB読み込み、`BatchAction` で集計・書き込みを行い、フレームワークのトランザクションループ制御ハンドラにコミット間隔を委ねる構成です。

---

**根拠**:

### 1. ハンドラ構成（コンポーネント定義ファイル）

DB接続有り都度起動バッチの最小ハンドラ構成（順序厳守）:

| No. | ハンドラ | スレッド | 役割 |
|-----|---------|---------|------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン | 終了コード変換 |
| 2 | グローバルエラーハンドラ | メイン | 未捕捉例外のログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | メイン | DB接続取得/解放 |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | メイン | 初期化トランザクション |
| 5 | リクエストディスパッチハンドラ | メイン | アクションクラス決定 |
| 6 | マルチスレッド実行制御ハンドラ | メイン | サブスレッド管理 |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ | 業務用DB接続取得/解放 |
| 8 | **トランザクションループ制御ハンドラ** | サブ | コミット間隔制御・ループ継続 |
| 9 | データリードハンドラ | サブ | 1レコード読み込み→アクションへ渡す |

コミット間隔はトランザクションループ制御ハンドラで設定します:

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <!-- コミット間隔に1000を指定 -->
  <property name="commitInterval" value="1000" />
</component>
```

### 2. DataReader（読み込み側）

DBから読み込むには `DatabaseRecordReader` を使います。アクションクラスの `createReader` でインスタンスを生成します。集計に使うSQLは SQLファイルで管理し、`UniversalDao.findAllBySqlFile` で呼び出します。

大量データを扱う場合は `UniversalDao.defer()` で遅延ロードし、メモリ不足を防ぎます:

```java
try (DeferredEntityList<InputEntity> inputs
        = (DeferredEntityList<InputEntity>) UniversalDao.defer()
                .findAllBySqlFile(InputEntity.class, "AGGREGATE_QUERY")) {
    // フレームワークが1件ずつ handle() に渡す
}
```

### 3. アクションクラス（集計・書き込み側）

`BatchAction` を継承して実装します。`handle` メソッドで1レコード分の集計処理と別テーブルへの書き込みを行います:

```java
public Result handle(InputEntity input, ExecutionContext ctx) {
    // 集計結果を計算
    OutputEntity result = aggregate(input);
    // 別テーブルに書き込み
    UniversalDao.insert(result);
    return new Result.Success();
}
```

まとめて書き込める場合は `batchInsert` でラウンドトリップ回数を削減できます:

```java
UniversalDao.batchInsert(resultList);
```

### 4. DB to DBパターンの動作

入力はSELECT文の結果セットの各レコードで、1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

---

**注意点**:

- **自前ループ禁止**: `handle` メソッド内で自前でSELECT文を発行してループするとフレームワークのコミット制御が効かず、更新件数が増えるとトランザクションログを逼迫します。読み込みSQLは必ず `createReader` に移してフレームワーク管理のループを使ってください。
- **遅延ロード時のカーソル注意**: `defer()` 使用中にトランザクション制御（コミット）が行われるとカーソルがクローズされてエラーになる場合があります（RDBMSに依存）。データベースベンダーのマニュアルで挙動を確認してください。
- **batchUpdate と排他制御**: `batchUpdate` は排他制御を行いません。排他制御が必要な更新は1レコードずつの更新処理を使ってください。

参照: `nablarch-batch-architecture.json:s5`, `nablarch-batch-architecture.json:s7`, `nablarch-batch-architecture.json:s8`, `nablarch-patterns-Nablarchバッチ処理パターン.json:s4`, `nablarch-patterns-Nablarchアンチパターン.json:s9`, `nablarch-patterns-Nablarchアンチパターン.json:s11`, `libraries-universal-dao.json:s7`, `libraries-universal-dao.json:s9`, `libraries-universal-dao.json:s14`, `handlers-loop-handler.json:s5`

---