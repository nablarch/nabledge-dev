Code analysis for ProjectAction completed. Documentation written to `.nabledge/20260424/code-analysis-ProjectAction.md`.

## Summary

**Target**: `./.lw/nab-official/v6/nablarch-example-web/src/main/java/com/nablarch/example/app/web/action/ProjectAction.java` — プロジェクトの検索・登録・更新・削除・CSVダウンロードを提供するWebアクション

### Architecture

Single Action class (`ProjectAction`) coordinating:
- **Forms**: `ProjectForm`, `ProjectSearchForm`, `ProjectTargetForm`, `ProjectUpdateForm`
- **DTOs**: `ProjectDto`, `ProjectSearchDto`, `ProjectDownloadDto`
- **Entities**: `Project`, `Client`
- **Value/Session**: `LoginUserPrincipal`, `ProjectProfit`
- **Utility**: `TempFileUtil`
- **Nablarch framework**: `UniversalDao`, `DeferredEntityList`, `ObjectMapper`/`ObjectMapperFactory`, `FileResponse`, `SessionUtil`, `BeanUtil`, `ApplicationException`/`MessageUtil`, and interceptors `@InjectForm`, `@OnError`, `@OnDoubleSubmission`.

### Processing Flows

1. **登録 (PRG)**: `newEntity()` → `confirmOfCreate()` (ProjectForm 検証 + `UniversalDao.exists(Client, FIND_BY_CLIENT_ID)`) → `create()` (`@OnDoubleSubmission` + `UniversalDao.insert`) → 303 redirect → `completeOfCreate()`. 入力画面戻りは `backToNew()`。
2. **検索・一覧**: `index()` が初期条件でページング検索、`list()` が `@InjectForm(ProjectSearchForm)` 経由で条件検索。private `searchProject()` が `UniversalDao.page(n).per(20L).findAllBySqlFile(Project, "SEARCH_PROJECT", cond)` を実行。
3. **CSVダウンロード**: `download()` が `TempFileUtil.createTempFile()` → try-with-resources で `UniversalDao.defer().findAllBySqlFile(ProjectDownloadDto, "SEARCH_PROJECT", cond)` の `DeferredEntityList` と `ObjectMapperFactory.create(ProjectDownloadDto, out)` の `ObjectMapper` を束ね、レコードを逐次 `mapper.write()`、`FileResponse(path.toFile(), true)` を Shift_JIS/`プロジェクト一覧.csv` で返却。
4. **詳細・編集**: `show()`/`edit()` が `@InjectForm(ProjectTargetForm)` → `UniversalDao.findBySqlFile(ProjectDto, "FIND_BY_PROJECT")`。`edit()` は `SessionUtil.put("project", Project)` で編集対象を保持。
5. **更新・削除**: `confirmOfUpdate()` (顧客ID確認 + `BeanUtil.copy`) → `backToEdit()`/`update()` (`@OnDoubleSubmission` + `UniversalDao.update`) → `completeOfUpdate()`、`delete()` (`@OnDoubleSubmission` + `UniversalDao.delete`) → `completeOfDelete()`。

### Nablarch Framework Usage (highlights)

- **UniversalDao**: CRUD (`insert`/`update`/`delete`)、主キー検索 (`findById`)、SQLファイル検索 (`findBySqlFile`/`findAllBySqlFile`)、ページング (`page().per().findAllBySqlFile()`)、遅延ロード (`defer()` + `DeferredEntityList` を try-with-resources で close) を全て網羅。
- **@InjectForm / @OnError**: `ProjectForm`/`ProjectSearchForm`/`ProjectTargetForm`/`ProjectUpdateForm` のバインディングと、`ApplicationException` 時の入力画面フォワード。`name` 属性で複数フォーム共存（`searchForm`）。
- **@OnDoubleSubmission**: `create`/`update`/`delete` に付与し二重サブミットを防止。いずれも 303 リダイレクトで PRG パターン。
- **ObjectMapper / FileResponse (data-bind)**: 大量CSVは一時ファイル経由でストリーミング出力し `FileResponse(file, autoDelete=true)` で自動削除。`ObjectMapper.close()` 必須。
- **SessionUtil / BeanUtil / ApplicationException + MessageUtil**: `project` / `userContext` のセッション出し入れ、Form↔Entity↔DTO のコピー、`errors.nothing.client` メッセージによる業務例外送出。

Output: `/home/tie303177/work/nabledge/work2/.nabledge/20260424/code-analysis-ProjectAction.md` (Duration: approx. 2m 25s)
