# Section Granularity Analysis

全334 RST ファイルのセクション分割方式を比較し、RBKC に最適な分割ルールを導出した調査。

## Evaluation Date

2026-04-09

## How to Reproduce

```bash
# Prerequisites: .lw/nab-official/v6/ must exist
./setup.sh

# Analysis scripts are inline in this document (Python one-liners)
# The data source is all RST files under .lw/nab-official/v6/nablarch-document/ja/
```

## Source Data

| 項目 | 値 |
|------|-----|
| 対象 | `.lw/nab-official/v6/nablarch-document/ja/` 配下の全RSTファイル |
| ファイル数 | 334 |
| h2 ありファイル | 243 |
| h2 なしファイル（h1のみ、10行超） | 91 |
| h3 ありファイル | 89 |

## Section Splitting Comparison

3方式で全ファイルのセクション分割結果を比較:

| 方式 | セクション数 | 最大 | 中央値 | > 100行 | > 200行 | > 500行 |
|------|------------|------|--------|---------|---------|---------|
| **KC（AI）** | 1,411 | 561 | 10 | 49 (3%) | 8 (0%) | 1 (0%) |
| **h2のみ** | 1,239 | 2,630 | 21 | 123 (9%) | 50 (4%) | 12 (1%) |
| **h2+h3** | 1,802 | 662 | 19 | 111 (6%) | 16 (0%) | 1 (0%) |

### h2のみの問題ファイル Top 15

h2のみ分割で200行超のセクションが発生するファイル（h3で解決可能かどうか）:

| Max Section | h3数 | 解決可能 | File |
|------------|------|---------|------|
| 2,630 | 41 | Yes | libraries/tag.rst |
| 1,181 | 32 | Yes | libraries/database/database.rst |
| 975 | 19 | Yes | libraries/repository.rst |
| 757 | 20 | Yes | libraries/validation/bean_validation.rst |
| 679 | 7 | Yes | libraries/system_messaging/mom_system_messaging.rst |
| 662 | 4 | Yes | toolbox/NablarchOpenApiGenerator.rst |
| 616 | 21 | Yes | libraries/validation/nablarch_validation.rst |
| 604 | 12 | Yes | libraries/data_io/data_format/format_definition.rst |
| 595 | 16 | Yes | libraries/data_io/data_bind.rst |
| 593 | 7 | Yes | libraries/log/failure_log.rst |
| 569 | 15 | Yes | libraries/data_io/data_format.rst |
| 521 | 11 | Yes | libraries/mail.rst |
| 426 | 19 | Yes | libraries/database/universal_dao.rst |
| 404 | 15 | Yes | libraries/log.rst |
| 378 | 8 | Yes | libraries/code.rst |

**全件 h3 で解決可能。**

### h2+h3 でも残る大セクション（> 200行）

h2+h3 分割後も200行を超える16セクション。h4 はほぼゼロのため、見出しによるさらなる分割は不可能:

| Lines | h4数 | 見出し | File |
|-------|------|-------|------|
| 662 | 0 | OpenAPIドキュメントと生成されるソースコードの例 | NablarchOpenApiGenerator.rst |
| 351 | 0 | Excelシート名に関する規約 | testing_framework 01_Abstract.rst |
| 318 | 0 | フィールドタイプ一覧 | data_format/format_definition.rst |
| 314 | 0 | 一括更新機能の作成 | web/getting_started/project_bulk_update |
| 307 | 0 | メール送信を使うための設定 | libraries/mail.rst |
| 299 | 0 | 使用方法 | toolbox/JspStaticAnalysis.rst |
| 287 | 0 | 検索結果 | biz_samples/03/index.rst |
| 269 | 0 | 検索する | web/getting_started/project_search |
| 262 | 0 | GETリクエストを使用する | libraries/tag.rst |
| 243 | 1 | HikariCPのコネクションプールの状態を取得する | micrometer_adaptor.rst |
| 216 | 0 | 更新内容の入力と確認 | web/getting_started/project_update |
| 215 | 0 | テストデータの書き方 | send_sync.rst |
| 213 | 0 | フォーマットして値を出力する | libraries/tag.rst |
| 205 | 5 | DB設定変更 | toolbox/SqlExecutor.rst |
| 205 | 0 | テストデータの書き方 | RequestUnitTest/index.rst |
| 203 | 0 | タグライブラリのネームスペースをJakarta EE 10に変更 | migration/index.rst |

特徴: チュートリアル手順、コード例一覧、テーブル定義など、見出しなしで長く続く内容。

## Preamble Analysis

h1 と最初の h2 の間にあるコンテンツ（プリアンブル）の分布:

| 項目 | 値 |
|------|-----|
| プリアンブルありファイル | 192 (57%) |
| 最大プリアンブル | 268行 (blank_project/maven.rst) |

プリアンブル > 50行の例:

| Preamble Lines | Total Lines | File |
|---------------|------------|------|
| 268 | 304 | blank_project/maven.rst |
| 100 | 2,025 | libraries/tag/tag_reference.rst |
| 84 | 280 | messaging/db/getting_started/table_queue.rst |
| 76 | 215 | testing_framework 04_MasterDataRestore.rst |
| 71 | 3,085 | libraries/tag.rst |

現状のコンバータではプリアンブルが最初の h2 セクションに吸収されるため、そのセクションが肥大化する。

## No-h2 Files

h2 がなく h1 のみのファイル（10行超）: 91件

| Lines | Depth | File |
|-------|-------|------|
| 302 | 1 | libraries/data_io/data_format/multi_format_example.rst |
| 238 | 1 | web/getting_started/client_create/client_create2.rst |
| 147 | 1 | web/getting_started/client_create/client_create4.rst |
| 135 | 1 | web/getting_started/client_create/client_create1.rst |
| 112 | 1 | web_service/functional_comparison.rst |

depth=1 は見出しが h1 のみ。これらは全コンテンツが1セクションになる。

## Conclusion

See [README.md](../../README.md) — Design > Conversion Rules > RST > ファイル構造
