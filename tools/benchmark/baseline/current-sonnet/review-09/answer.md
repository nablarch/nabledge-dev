**結論**: `UniversalDao.batchUpdate(List<Entity>)` を使うことで、1件ずつの for ループをなくし、アプリ〜DBサーバ間のラウンドトリップ回数を削減できる。ただし **排他制御（楽観的ロック）は行われない** ため、バージョン管理が必要な場合は使えない。

**根拠**:

`UniversalDao` には大量データの一括更新を行うための `batchUpdate` メソッドが用意されている。`component/libraries/libraries-universal_dao.json:s11` によると、`batchInsert` / `batchUpdate` / `batchDelete` の3メソッドが提供されており、いずれも「アプリケーションサーバとDBサーバ間のラウンドトリップ回数を削減しパフォーマンス向上が期待できる」と明記されている。

```java
// 変更前（遅い）
for (MyEntity entity : list) {
    UniversalDao.update(entity);
}

// 変更後（一括更新）
UniversalDao.batchUpdate(list);
```

`processing-pattern/web-application/web-application-getting-started-project-bulk-update.json:s1` の一括更新実行アクション例でも同様に、`projectListDto.getProjectList()` の `List` を `batchUpdate` へ渡すパターンが示されている（ただし同サンプルは排他制御が必要なため `update` を採用している点にも言及がある）。

**注意点**:

- **排他制御なし**: `batchUpdate` は `@Version` による楽観的ロックを行わない（`component/libraries/libraries-universal_dao.json:s11`、`component/libraries/libraries-universal_dao.json:s12`）。更新対象EntityとDB上のバージョンが不一致でも、そのレコードは更新されずに**正常終了**してしまう。更新漏れがサイレントに発生する点に注意。
- 排他制御が必要な場合は、`batchUpdate` ではなく `UniversalDao.update(entity)` を1件ずつ呼び出す実装を維持すること（`processing-pattern/web-application/web-application-getting-started-project-bulk-update.json:s1` でも「排他制御が必要な場合は `UniversalDao#update` を使用すること」と明記）。
- 楽観的ロックエラー（`OptimisticLockException`）のハンドリングが必要な場合は `@OnError` アノテーションで遷移先を設定する（`component/libraries/libraries-universal_dao.json:s12`）。

参照: component/libraries/libraries-universal_dao.json:s11, component/libraries/libraries-universal_dao.json:s12, processing-pattern/web-application/web-application-getting-started-project-bulk-update.json:s1