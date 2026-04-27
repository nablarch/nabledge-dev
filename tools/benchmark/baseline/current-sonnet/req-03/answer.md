**結論**: Nablarch には標準の楽観的ロック機能があり、**Universal DAO の `@Version` アノテーション**を使うのが推奨方法です。テーブルにバージョン番号カラムを追加し、Entity の getter に `@Version` を付与するだけで、同時更新（後勝ちによるデータ消失）を防止できます。

**根拠**:

1. **`@Version` アノテーションで楽観的ロックを有効化** (`component/libraries/libraries-universal_dao.json:s6`)
   Entityのバージョンカラム用プロパティ（数値型）の getter に `@Version`（`jakarta.persistence.Version`）を付与します。更新処理時にバージョンカラムが WHERE 条件に自動追加され、楽観的ロックが実行されます。Entityに1つのみ指定可能です。

   ```java
   private Long version;

   @Version
   @Column(name = "VERSION", precision = 19, nullable = false, unique = false)
   public Long getVersion() {
       return version;
   }
   ```

2. **更新時の動作と排他エラー処理** (`component/libraries/libraries-universal_dao.json:s12`)
   `@Version` 付きEntityを `UniversalDao.update()` で更新すると楽観的ロックが自動実行されます。バージョン不一致（別のユーザーが先に更新済み）の場合は `jakarta.persistence.OptimisticLockException` がスローされます。エラー時の画面遷移は `@OnError` で設定します。

   ```java
   @OnError(type = OptimisticLockException.class,
            path = "/WEB-INF/view/common/errorPages/userError.jsp")
   public HttpResponse update(HttpRequest request, ExecutionContext context) {
       UniversalDao.update(user);
   }
   ```

3. **実際のWebアプリでの使い方** (`processing-pattern/web-application/web-application-getting-started-project-update.json:s2`)
   `UniversalDao.update()` を呼ぶだけで楽観的ロックが実行されます。二重サブミット防止には `@OnDoubleSubmission` を併用します。

4. **ロック単位の設計指針** (`component/libraries/libraries-universal_dao.json:s14`)
   バージョンカラムをどのテーブルに定義するかは業務的観点で決めます。競合が許容される最大の単位で定義し、単位を大きくすると競合の可能性が高まる点に注意が必要です。

**注意点**:
- `@Version` は**数値型のプロパティのみ**に指定可能。文字列型では正しく動作しません (`component/libraries/libraries-universal_dao.json:s12`)
- `batchUpdate`（一括更新）では楽観的ロックは**使用できません** (`component/libraries/libraries-universal_dao.json:s12`)
- 旧来の排他制御ライブラリ（`BasicExclusiveControlManager` / `ExclusiveControlUtil`）は**非推奨**。Universal DAO を使用してください (`component/libraries/libraries-exclusive_control.json:s1`)

参照: component/libraries/libraries-universal_dao.json:s6, component/libraries/libraries-universal_dao.json:s12, component/libraries/libraries-universal_dao.json:s14, processing-pattern/web-application/web-application-getting-started-project-update.json:s2, component/libraries/libraries-exclusive_control.json:s1