**結論**: Nablarch には楽観的ロック・悲観的ロックの仕組みがある。推奨は **UniversalDao** の `@Version` アノテーションを使った楽観的ロックで、テーブルにバージョン番号カラムを持たせることで「後勝ち上書き」を防止できる。

**根拠**:

1. **UniversalDao による楽観的ロック（推奨）**  
   `@Version` が付いた Entity を `UniversalDao.update()` で更新すると、自動的に楽観的ロックが適用される。別ユーザーが先に更新していた場合（バージョン番号が一致しない場合）は `jakarta.persistence.OptimisticLockException` がスローされ、上書きを防止できる。  
   （`component/libraries/libraries-universal_dao.json:s12`）

   画面遷移は `@OnError` で制御できる:
   ```java
   @OnError(type = OptimisticLockException.class,
            path = "/WEB-INF/view/common/errorPages/userError.jsp")
   public HttpResponse update(...) {
       UniversalDao.update(user);
   }
   ```
   （`component/libraries/libraries-universal_dao.json:s12`）

2. **旧 exclusive_control ライブラリ（非推奨）**  
   `BasicExclusiveControlManager` を使う旧方式も楽観的ロック・悲観的ロックの両方を実現できるが、現在は **非推奨**。PostgreSQL など暗黙型変換を行わない DB では主キーの型不一致で実行時例外が発生する問題があるため、UniversalDao 方式に移行することが推奨されている。  
   （`component/libraries/libraries-exclusive_control.json:s1`）

3. **ロック単位の設計**  
   バージョンカラムをどのテーブルに定義するかは業務的観点で決定する。単位を大きくするほど競合確率が上がり、楽観的ロックでは更新失敗、悲観的ロックでは処理遅延を招く。  
   （`component/libraries/libraries-universal_dao.json:s14`）

**注意点**:
- `@Version` は **数値型プロパティのみ** に指定可能。文字列型では正しく動作しない（`component/libraries/libraries-universal_dao.json:s12`）。
- `batchUpdate`（一括更新）では楽観的ロックは **使用できない**（`component/libraries/libraries-universal_dao.json:s12`）。一括更新の楽観的ロックには旧 `HttpExclusiveControlUtil#checkVersions` / `updateVersionsWithCheck` を使う方法があるが、旧ライブラリは非推奨である点に注意（`component/libraries/libraries-exclusive_control.json:s3`）。

参照: component/libraries/libraries-universal_dao.json:s12, component/libraries/libraries-universal_dao.json:s14, component/libraries/libraries-exclusive_control.json:s1, component/libraries/libraries-exclusive_control.json:s3