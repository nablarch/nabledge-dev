**質問**: for 文で 1 万件のレコードを 1 件ずつ更新する処理を書いている。遅いしレビューでも指摘された。Nablarch に一括で扱える仕組みはある？

---

**結論**: `UniversalDao` に一括処理用のバッチ実行メソッド `batchInsert` / `batchUpdate` / `batchDelete` が提供されている。AP サーバと DB サーバ間のラウンドトリップ回数を削減でき、パフォーマンス向上が期待できる。ただし `batchUpdate` は排他制御を行わないため、排他が必要な処理では使えない。 — `component/libraries/libraries-universal_dao.json#s11`

**① 使用するメソッド**
- `batchInsert`: 一括登録
- `batchUpdate`: 一括更新
- `batchDelete`: 一括削除 — `component/libraries/libraries-universal_dao.json#s11`

**② 効果**
大量データの一括登録・更新・削除でバッチ実行を使用すると、AP サーバと DB サーバ間のラウンドトリップ回数を削減しパフォーマンス向上が期待できる。 — `component/libraries/libraries-universal_dao.json#s11`

**注意点**
- `batchUpdate` による一括更新では **排他制御を行わない**。更新対象 Entity と DB のバージョンが不一致でも、そのレコードの更新は行われずに正常終了する。排他制御が必要な更新処理では、一括更新ではなく **1 レコード毎の更新処理** を使用すること。 — `component/libraries/libraries-universal_dao.json#s11`
