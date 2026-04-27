**質問**: DB 接続が一瞬切れるような一時的な障害で失敗したとき、自動で再実行させたい。Nablarch にそういう仕組みある？ 使う場合の注意は？

---

**結論**: Nablarch には `RetryHandler`（リトライハンドラ）が標準で用意されている。`retryContextFactory` プロパティに `CountingRetryContextFactory`（回数）または経過時間ベースのファクトリを設定して上限を決める。リトライ対象の例外を送出するハンドラは、本ハンドラより **後** に配置する必要がある。 — `component/handlers/handlers-retry_handler.json#s3`、`component/handlers/handlers-retry_handler.json#s4`

**① 配置制約**
リトライ対象例外を送出するハンドラは、`RetryHandler` より **後** に設定する。手前に設定しても単なる例外として処理されてしまう。 — `component/handlers/handlers-retry_handler.json#s3`

**② リトライ上限の設定（必須）**
本ハンドラ使用時はリトライ上限の設定が **必須**。上限に達しても成功しない場合は異常終了させる。上限設定は2種類:
- リトライ回数による上限設定
- 経過時間による上限設定 — `component/handlers/handlers-retry_handler.json#s4`

**③ 設定例（回数ベース）**
```xml
<component name="retryHandler" class="nablarch.fw.handler.RetryHandler">
  <property name="retryContextFactory">
    <component class="nablarch.fw.handler.retry.CountingRetryContextFactory">
      <property name="retryCount" value="3" />         <!-- 最大3回リトライ -->
      <property name="retryIntervals" value="5000" />  <!-- リトライ実行まで5秒待機 -->
    </component>
  </property>
</component>
```
— `component/handlers/handlers-retry_handler.json#s4`

**注意点**
- 上限値は想定する最大復旧時間プラスアルファに設定する（例: DB 切り替えに最大5分かかるなら7分など）。
- 複数の例外に対するリトライを実現する場合は、最も復旧に時間を要するものをベースに上限を設定する。 — `component/handlers/handlers-retry_handler.json#s4`
