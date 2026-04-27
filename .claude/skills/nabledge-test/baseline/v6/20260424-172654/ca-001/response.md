# Code Analysis: ProjectAction

**Generated**: 2026-04-24 17:27:59
**Target**: プロジェクトの検索・登録・更新・削除・CSVダウンロード機能を提供する業務Action
**Modules**: nablarch-example-web
**Analysis Duration**: unknown

---

## Overview

`ProjectAction` は Nablarch Web アプリケーションの業務Actionで、プロジェクトに対する CRUD (一覧検索・登録・更新・削除) と CSV ダウンロードを提供する。入力はフォームクラス (`ProjectForm`/`ProjectSearchForm`/`ProjectTargetForm`/`ProjectUpdateForm`) で受け取り、`@InjectForm` によりバリデーション済みのオブジェクトがリクエストスコープへ格納される。データアクセスは `UniversalDao` を利用し、ページングや遅延ロードを活用する。登録・更新・削除メソッドには `@OnDoubleSubmission` を付与し二重サブミットを防止している。

## Architecture

Dependency Graph (classDiagram): `ProjectAction` → `ProjectForm`/`ProjectSearchForm`/`ProjectTargetForm`/`ProjectUpdateForm` (validates via @InjectForm), `ProjectProfit` (creates), `UniversalDao` <<Nablarch>> (persists/queries), `SessionUtil` <<Nablarch>> (stores state), `BeanUtil` <<Nablarch>> (copies properties), `ObjectMapperFactory`/`ObjectMapper` <<Nablarch>> (writes CSV), `FileResponse` <<Nablarch>> (downloads file), `DeferredEntityList` <<Nablarch>> (lazy loads), `ExecutionContext` <<Nablarch>>, `ApplicationException` <<Nablarch>>, `MessageUtil` <<Nablarch>>.

Component Summary:
- ProjectAction — プロジェクトCRUDとCSVダウンロードの業務Action (Action)
- ProjectProfit — 売上・原価から利益指標を算出する値オブジェクト (Domain Value)
- ProjectForm / ProjectSearchForm / ProjectTargetForm / ProjectUpdateForm — 入力Form (Form)
- UniversalDao — O/Rマッパー (Nablarch)
- SessionUtil — セッションスコープ操作 (Nablarch)
- BeanUtil — JavaBeanプロパティコピー (Nablarch)
- ObjectMapperFactory / ObjectMapper — CSVバインディング (Nablarch)
- FileResponse — ファイル応答 (Nablarch)
- DeferredEntityList — 遅延ロード対応Entityリスト (Nablarch)

## Flow

- 登録系: `newEntity()` → `confirmOfCreate()` (@InjectForm(ProjectForm) + @OnError, Client存在チェック, SessionUtil.put) → `create()` (@OnDoubleSubmission, UniversalDao.insert, 303 redirect) → `completeOfCreate()`。`backToNew()` で入力画面に戻る。
- 検索系: `index()` (初期ソートキー=ID, ページ=1) / `list()` (@InjectForm(ProjectSearchForm) + @OnError) → private `searchProject(cond, context)` で `UniversalDao.page(n).per(20L).findAllBySqlFile(Project.class, "SEARCH_PROJECT", cond)`。
- 参照/更新系: `show()` / `edit()` (@InjectForm(ProjectTargetForm)) で `UniversalDao.findBySqlFile(ProjectDto.class, "FIND_BY_PROJECT", ...)`。`confirmOfUpdate()` (@InjectForm(ProjectUpdateForm) + @OnError, Client存在チェック, BeanUtil.copy) → `update()` (@OnDoubleSubmission, UniversalDao.update, 303 redirect) → `completeOfUpdate()`。`backToEdit()` で戻る。
- 削除/ダウンロード系: `delete()` (@OnDoubleSubmission, UniversalDao.delete, 303 redirect)。`download()` (@InjectForm(ProjectSearchForm) + @OnError) で `UniversalDao.defer().findAllBySqlFile(ProjectDownloadDto.class, "SEARCH_PROJECT", ...)` + `ObjectMapperFactory.create()` の try-with-resources、ループで `mapper.write(dto)`、`FileResponse` を `text/csv; charset=Shift_JIS` / ファイル名 `プロジェクト一覧.csv` で返却。

Sequence Diagram: Client → ProjectAction → SessionUtil/BeanUtil/UniversalDao/ObjectMapper/DB、登録フローと検索/ダウンロードフローを alt/loop 含めて記載。

## Components

- **ProjectAction**: 主要メソッド `confirmOfCreate` (:61-88), `create` (:97-103), `index` (:138-150), `list` (:159-169), `searchProject` (:181-190, private helper), `download` (:200-222), `show` (:231-246), `edit` (:255-271), `confirmOfUpdate` (:280-305), `update` (:322-328), `delete` (:348-353)。
- **ProjectProfit**: `getGrossProfit`, `getProfitBeforeAllocation`, `getProfitRateBeforeAllocation` (BigDecimal, RoundingMode.HALF_UP)。
- **ProjectForm / ProjectSearchForm / ProjectTargetForm / ProjectUpdateForm**: Bean Validation 適用の入力Form群。

## Nablarch Framework Usage

- **UniversalDao** (`nablarch.common.dao.UniversalDao`): `page().per()` によるページング、`defer()` による遅延ロード、`insert/update/delete/findBySqlFile/findAllBySqlFile/exists`。本コードでは `confirmOfCreate`/`confirmOfUpdate` の `exists(Client, "FIND_BY_CLIENT_ID", ...)`、`searchProject` の `page(n).per(20L).findAllBySqlFile(Project, "SEARCH_PROJECT", ...)`、`show`/`edit` の `findBySqlFile(ProjectDto, "FIND_BY_PROJECT", ...)`、`download` の `defer().findAllBySqlFile(ProjectDownloadDto, ...)`、`create/update/delete` の副作用メソッドで使用。
- **@InjectForm / @OnError** (`nablarch.common.web.interceptor.InjectForm` / `nablarch.fw.web.interceptor.OnError`): バインド+バリデーション+例外時のフォワード。`confirmOfCreate`/`confirmOfUpdate`/`list`/`download` で `ApplicationException → JSP` のペアが使われ、`show`/`edit` は path なしで利用。
- **@OnDoubleSubmission** (`nablarch.common.web.token.OnDoubleSubmission`): `create`/`update`/`delete` に付与し、副作用後に 303 リダイレクトで PRG 実装。
- **SessionUtil** (`nablarch.common.web.session.SessionUtil`): `put`/`get`/`delete` でセッションスコープを型安全に扱う。`"project"` キーで入力→確認→登録/更新の中継、`"userContext"` キーで `LoginUserPrincipal` を取得し検索条件の `userId` 付与。
- **ObjectMapper / ObjectMapperFactory / FileResponse** (`nablarch.common.databind.*` / `nablarch.common.web.download.FileResponse`): データバインドによる CSV 出力、`text/csv; charset=Shift_JIS` / `プロジェクト一覧.csv` のダウンロード応答。`DeferredEntityList` と `ObjectMapper` を try-with-resources で扱い大量データを安全に処理。
- **BeanUtil** (`nablarch.core.beans.BeanUtil`): `createAndCopy` / `copy` で Form↔Entity↔DTO のプロパティコピー。
- **MessageUtil / ApplicationException** (`nablarch.core.message.*`): `errors.nothing.client` などのメッセージIDから国際化メッセージ生成 → 業務例外 throw → `@OnError` でフォワード。

## References

- Source: `.lw/nab-official/v6/nablarch-example-web/src/main/java/com/nablarch/example/app/web/action/ProjectAction.java` ほか ProjectProfit, ProjectForm/SearchForm/TargetForm/UpdateForm
- Knowledge Base (Nabledge-6): Libraries Universal Dao, Libraries Data Bind, Handlers InjectForm, Handlers On Error, Web Application Feature Details, Web Application Getting Started Project Search/Update/Delete/Download

**Output file**: `/home/tie303177/work/nabledge/work2/.nabledge/20260424/code-analysis-ProjectAction.md`
