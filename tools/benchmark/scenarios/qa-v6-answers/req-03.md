**質問**: 同じデータを複数人が同時に編集して後勝ちで消える問題を防ぎたい。Nablarch にそういう仕組みはある？

---

**結論**: Nablarch は排他制御をビルトインで提供している。推奨は `UniversalDao` による排他制御で、**楽観排他** と **悲観排他** の両方をサポートする。楽観排他は `@Version` アノテーションを数値型プロパティに付与するだけで自動的に有効になり、排他エラー時は `jakarta.persistence.OptimisticLockException` が送出される。 — `processing-pattern/web-application/web-application-feature_details.json#s4`、`component/libraries/libraries-universal_dao.json#s12`

**① 推奨方式**
排他制御は2種類提供されるが、`UniversalDao` の使用を推奨する（`UniversalDao` を推奨する理由は `component/libraries/libraries-exclusive_control.json#s1` を参照）:
- `universal_dao`（推奨） — 楽観排他 / 悲観排他をサポート
- `exclusive_control` — `processing-pattern/web-application/web-application-feature_details.json#s4`

**② 楽観的ロックの書き方**
`@Version` が付いている Entity を更新すると自動で楽観的ロックを行う。排他エラー発生時は `jakarta.persistence.OptimisticLockException` を送出する。

排他エラー時の画面遷移は `@OnError` を使用:

```java
@OnError(type = OptimisticLockException.class,
         path = "/WEB-INF/view/common/errorPages/userError.jsp")
public HttpResponse update(HttpRequest request, ExecutionContext context) {
    UniversalDao.update(user);
}
```

- `@Version` は **数値型プロパティのみ** に指定可能。文字列型では正しく動作しない。
- 一括更新処理（`batchUpdate`）では楽観的ロックは使用できない。 — `component/libraries/libraries-universal_dao.json#s12`

**③ バージョンカラム設計の考え方**
バージョンカラムをどのテーブルに定義するかは業務観点で決める。バージョン番号を持つテーブルは **排他制御の単位ごと** に定義し、**競合が許容される最大の単位** で定義する。例えば「ユーザ」単位のロックが業務上許容されるならユーザテーブルにバージョン番号を定義する。単位を大きくすると競合の可能性が高まり、更新失敗（楽観）や処理遅延（悲観）を招く点に注意。 — `component/libraries/libraries-universal_dao.json#s14`
