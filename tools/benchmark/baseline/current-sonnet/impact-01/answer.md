**結論**: Nablarchバッチのトランザクション境界は、使用するバッチ方式によって決まる主体が異なる。**Nablarchバッチ（スタンドアロン）**では `LoopHandler` が `commitInterval` 件数ごとにコミットし、**Jakarta EEバッチ（JSR352）** ではリスナー（`ItemWriteTransactionManagementListener`）が `ItemWriter#writeItems` 実行後にコミットする。

---

**根拠**:

### Nablarchバッチ（スタンドアロン）の場合

トランザクション制御の主体は `LoopHandler`（`nablarch.fw.handler.LoopHandler`）。

> 「データリーダ上に処理対象のデータが存在する間、後続ハンドラの処理を繰り返し実行する。実行中はトランザクションを制御し、一定の繰り返し回数ごとにトランザクションをコミットする」
> — `component/handlers/handlers-loop_handler.json:s1`

コミット間隔は `commitInterval` プロパティで件数指定する：

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <property name="commitInterval" value="1000" />
</component>
```

（`component/handlers/handlers-loop_handler.json:s6`）

ハンドラ構成表では「サブスレッドの `LoopHandler` が業務トランザクション開始→コミット間隔毎にコミット→例外時ロールバック」という役割が割り当てられている（`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`）。

トランザクション対象DBの指定は `transactionFactory` / `transactionName` プロパティで行い、`DbConnectionManagementHandler#connectionName` と一致させる必要がある（`component/handlers/handlers-loop_handler.json:s5`）。

---

### Jakarta EEバッチ（JSR352 / Chunkタイプ）の場合

トランザクション制御はリスナーが担当し、2層構造になっている（`processing-pattern/jakarta-batch/jakarta-batch-architecture.json:s7`）：

| リスナー | 動作タイミング | 処理 |
|---|---|---|
| `StepTransactionManagementListener` | ステップ開始前 / 終了後 | トランザクション開始 / 終了（commit or rollback） |
| `ItemWriteTransactionManagementListener` | `ItemWriter` 実行後 | トランザクション終了（commit or rollback） |

コミットのタイミングは `ItemWriter#writeItems` の実行後：

> 「`writeItems`実行後にトランザクションがコミットされ、新たなトランザクションが開始される」
> — `processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json:s5`

Chunkサイズ（＝何件ごとに `writeItems` を呼ぶか）はジョブ定義XMLの `item-count` で指定する（`processing-pattern/jakarta-batch/jakarta-batch-architecture.json:s8`）：

```xml
<chunk item-count="10">
  <reader ref="stringReader" />
  <processor ref="createEntityProcessor" />
  <writer ref="batchOutputWriter" />
</chunk>
```

---

**注意点**:
- Nablarchバッチの `commitInterval` は「レコード読み込み繰り返し回数」であり、レコード件数そのものではなくループ回数で数える。
- Jakarta EEバッチの `ItemWriteTransactionManagementListener` が行うコミット/ロールバックは、ステップレベルで開始されたトランザクションに対して行われる（`processing-pattern/jakarta-batch/jakarta-batch-architecture.json:s7`）。
- リスナーの実行順はJSR352では保証されないため、NablarchはExecutorパターンでリスナーリスト定義順に実行する仕組みを提供している（`processing-pattern/jakarta-batch/jakarta-batch-architecture.json:s6`）。

参照: component/handlers/handlers-loop_handler.json:s1, component/handlers/handlers-loop_handler.json:s5, component/handlers/handlers-loop_handler.json:s6, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1, processing-pattern/jakarta-batch/jakarta-batch-architecture.json:s6, processing-pattern/jakarta-batch/jakarta-batch-architecture.json:s7, processing-pattern/jakarta-batch/jakarta-batch-architecture.json:s8, processing-pattern/jakarta-batch/jakarta-batch-getting-started-chunk.json:s5