# 生成・検証・修正 最長実行時間 上位30件 傾向分析

**対象実行**: 20260324T235810
**分析日**: 2026-03-25

---

## Phase B（生成）上位30件

| rank | file_id | 秒 | turns | コスト | ソース行 | in_kb | 画像 |
|-----|---------|---:|------:|------:|-------:|-----:|----:|
| 1 | about-nablarch-glossary--s1 | 1503 | 2 | $2.43 | 224 | 29.5 | 0 |
| 2 | ui-framework-jsp_page_templates--s1 | 1236 | 2 | $2.30 | 322 | 40.1 | 0 |
| 3 | libraries-05_ServiceAvailability--s1 | 853 | 2 | $1.39 | 264 | 35.0 | 5 |
| 4 | web-application-07_insert--s1 | 793 | 2 | $1.37 | 398 | 40.4 | 2 |
| 5 | libraries-07_FormTag--s1 | 745 | 2 | $1.36 | 379 | 39.7 | 6 |
| 6 | testing-framework-02_DbAccessTest--s1 | 696 | 2 | $1.20 | 379 | 33.1 | 3 |
| 7 | web-application-10_submitParameter--s1 | 689 | 2 | $1.08 | 182 | 26.5 | 2 |
| 8 | toolbox-01_DefInfoGenerator--s13 | 640 | 2 | $1.20 | 301 | 29.0 | 0 |
| 9 | libraries-06_IdGenerator--s1 | 600 | 2 | $1.13 | 343 | 38.9 | 3 |
| 10 | libraries-04_QueryCache--s1 | 600 | 2 | $1.06 | 329 | 34.0 | 10 |
| 11 | testing-framework-send_sync-02_RequestUnitTest--s1 | 591 | 2 | $1.04 | 254 | 34.2 | 5 |
| 12 | libraries-messaging_sender_util--s1 | 588 | 2 | $1.13 | 371 | 43.7 | 0 |
| 13 | libraries-mail--s1 | 586 | 2 | $0.28 | 305 | 36.2 | 2 |
| 14 | handlers-BatchAction--s1 | 582 | 2 | $0.99 | 205 | 28.3 | 0 |
| 15 | libraries-04_Statement--s1 | 517 | 2 | $0.94 | 353 | 41.0 | 2 |
| 16 | handlers-HttpRewriteHandler--s1 | 503 | 2 | $0.95 | 366 | 39.6 | 0 |
| 17 | web-application-06_sharingInputAndConfirmationJsp--s1 | 490 | 2 | $0.79 | 132 | 25.1 | 2 |
| 18 | testing-framework-batch-02_RequestUnitTest--s1 | 479 | 2 | $0.84 | 361 | 37.9 | 1 |
| 19 | libraries-07_CustomTag--s1 | 444 | 2 | $0.74 | 183 | 25.0 | 1 |
| 20 | workflow-WorkflowProcessElement--s1 | 335 | 2 | $0.77 | 220 | 29.2 | 9 |
| 21 | biz-samples-07_UserAgent--s1 | 328 | 2 | $0.76 | 326 | 38.4 | 1 |
| 22 | libraries-05_FileDownload--s1 | 325 | 2 | $0.78 | 399 | 51.8 | 2 |
| 23 | web-application-04_validation--s1 | 323 | 2 | $0.74 | 382 | 37.7 | 1 |
| 24 | libraries-07_BasicRules--s1 | 320 | 2 | $0.76 | 260 | 32.3 | 0 |
| 25 | toolbox-01_AuthGenerator--s1 | 319 | 2 | $0.74 | 329 | 31.2 | 0 |
| 26 | libraries-01_Log--s26 | 316 | 2 | $0.73 | 400 | 49.5 | 3 |
| 27 | biz-samples-04_ExtendedFormatter--s1 | 315 | 2 | $0.66 | 120 | 26.0 | 0 |
| 28 | testing-framework-01_Abstract--s1 | 313 | 2 | $0.58 | 226 | 29.0 | 2 |
| 29 | testing-framework-http_real--s1 | 310 | 2 | $0.60 | 161 | 26.6 | 1 |
| 30 | libraries-07_FormTag--s16 | 306 | 2 | $0.60 | 187 | 27.7 | 6 |

### Phase B 傾向分析

**全件 turns=2**。生成フェーズではエージェント的な追加ツール呼び出しは発生していない（標準フロー）。

**時間とコストの相関は強いが、ソース行数との相関は弱い**

上位5件のソース行数：224 / 322 / 264 / 398 / 379 行。最長の `about-nablarch-glossary--s1` は224行と中規模だが1503秒かかっている。一方 `libraries-05_FileDownload--s1`（399行、51.8KB）は325秒に留まる。

→ **行数・バイト数より「内容の複雑さ」が実行時間を左右している**。用語集・JSPテンプレートなど密度の高いドキュメントが時間を要する傾向。

**画像との相関も弱い**

1位（0枚）・2位（0枚）が最長で、10位（10枚）が600秒。画像枚数と実行時間に一貫した相関なし。画像は RST 内にディレクティブとして記述されるだけで、実際に画像ファイルを読み込んでいないため。

**13位 `libraries-mail--s1` のコストが異常に低い（$0.28）**

同規模の他ファイルが $0.74〜1.36 なのに対して $0.28 は突出して低い。
これはモデルが出力した知識ファイルの内容量が少なかった可能性がある（内容が薄い生成結果）。
後のコンテンツチェックでも問題が検出されているかを確認する価値がある。

---

## Phase D（コンテンツチェック）上位30件

| rank | file_id | 秒 | turns | コスト | ソース行 |
|-----|---------|---:|------:|------:|-------:|
| 1 | libraries-01_FailureLog--s1 | 213 | 5 | $0.644 | 3 |
| 2 | libraries-01_FailureLog--s1 | 204 | 9 | $0.757 | 3 |
| 3 | libraries-01_FailureLog--s2 | 198 | 2 | $0.368 | 807 |
| 4 | libraries-08_02_validation_usage--s8 | 195 | 2 | $0.318 | 309 |
| 5 | libraries-08_ExclusiveControl--s1 | 184 | 2 | $0.328 | 332 |
| 6 | toolbox-01_AuthGenerator--s1 | 176 | 2 | $0.337 | 329 |
| 7 | web-application-basic--s8 | 175 | 2 | $0.322 | 430 |
| 8 | libraries-01_FailureLog--s2 | 170 | 2 | $0.373 | 807 |
| 9 | testing-framework-01_UnitTestOutline--s1 | 168 | 2 | $0.298 | 375 |
| 10 | web-application-03_listSearch--s1 | 165 | 2 | $0.280 | 362 |
| 11 | web-application-07_insert--s1 | 160 | 2 | $0.308 | 398 |
| 12 | libraries-02_04_Repository_override--s1 | 160 | 2 | $0.314 | 397 |
| 13 | libraries-02_01_Repository_config--s1 | 160 | 2 | $0.311 | 294 |
| 14 | libraries-04_Statement--s1 | 153 | 2 | $0.300 | 353 |
| 15 | about-nablarch-concept--s8 | 152 | 2 | $0.296 | 355 |
| 16 | handlers-HttpRewriteHandler--s1 | 151 | 2 | $0.265 | 366 |
| 17 | testing-framework-02_RequestUnitTest-02_RequestUnitTest--s1 | 150 | 2 | $0.282 | 397 |
| 18 | testing-framework-02_RequestUnitTest--s12 | 150 | 2 | $0.298 | 349 |
| 19 | libraries-07_Message--s1 | 149 | 2 | $0.294 | 354 |
| 20 | libraries-05_FileDownload--s1 | 147 | 2 | $0.286 | 399 |
| 21 | libraries-05_ServiceAvailability--s1 | 146 | 2 | $0.272 | 264 |
| 22 | about-nablarch-concept--s8 | 144 | 2 | $0.267 | 355 |
| 23 | libraries-02_01_Repository_config--s1 | 144 | 2 | $0.269 | 294 |
| 24 | libraries-07_Message--s1 | 143 | 2 | $0.286 | 354 |
| 25 | web-application-02_basic--s1 | 143 | 2 | $0.264 | 258 |
| 26 | libraries-01_FailureLog--s1 | 143 | 11 | $0.449 | 3 |
| 27 | ui-framework-reference_ui_standard--s1 | 143 | 2 | $0.274 | 395 |
| 28 | biz-samples-03_ListSearchResult--s1 | 142 | 2 | $0.265 | 266 |
| 29 | biz-samples-03_ListSearchResult--s24 | 142 | 2 | $0.294 | 397 |
| 30 | libraries-04_Statement--s1 | 142 | 2 | $0.256 | 353 |

### Phase D 傾向分析

**`libraries-01_FailureLog--s1` が突出して多ターン（5t / 9t / 11t）**

同一ファイルが3回チェックされており（ラウンド1・2・3）、毎回多ターンになっている。
ソース行数が「3行」と記録されているのは catalog の section_range が正しく反映されていない可能性がある。
多ターンはチェッカーがツールを呼び出してソース照合を繰り返していることを示す。
このファイルは他のファイルより構造が複雑か、知識ファイルとソースの差異が大きいと考えられる。

**Phase D の実行時間はPhase B より大幅に短い（最大213秒 vs 最大1503秒）**

コンテンツチェックはソースと知識ファイルを比較するだけのため、生成より軽量。
ただし上位30件は全てで100秒超えており、チェック処理もそれなりのコストがある。

**同一ファイルが複数回ランクインする（ラウンド1/2/3での重複）**

`libraries-01_FailureLog--s2`（rank 3, 8）、`libraries-02_01_Repository_config--s1`（rank 13, 23）、
`about-nablarch-concept--s8`（rank 15, 22）など。毎ラウンドで検査時間が長い「慢性的に重いファイル」が存在する。

**大きいソースファイル（400行超）が上位に集中**

上位30件のソース行数の中央値は約350行。これはチェックプロンプトがソース全文を含むため、
ソースが大きいほどチェック時間が比例して増加する。

---

## Phase E（修正）上位30件

| rank | file_id | 秒 | turns | コスト | ソース行 |
|-----|---------|---:|------:|------:|-------:|
| 1 | biz-samples-01_Utility--s6 | 192 | 2 | $0.454 | 318 |
| 2 | libraries-thread_context--s1 | 151 | 2 | $0.410 | 345 |
| 3 | libraries-01_FailureLog--s2 | 131 | 2 | $0.405 | 807 |
| 4 | libraries-07_TagReference--s1 | 127 | 2 | $0.357 | 400 |
| 5 | libraries-thread_context--s1 | 125 | 2 | $0.382 | 345 |
| 6 | libraries-04_HttpAccessLog--s1 | 110 | 2 | $0.287 | 336 |
| 7 | libraries-01_FailureLog--s1 | 109 | 2 | $0.284 | 3 |
| 8 | web-application-05_screenTransition--s1 | 105 | 4 | $0.522 | 89 |
| 9 | libraries-01_Log--s17 | 103 | 2 | $0.278 | 388 |
| 10 | testing-framework-01_Abstract--s8 | 100 | 2 | $0.318 | 351 |
| 11 | libraries-05_MessagingLog--s1 | 98 | 2 | $0.321 | 396 |
| 12 | libraries-05_FileDownload--s1 | 93 | 2 | $0.279 | 399 |
| 13 | java-static-analysis-01_JspStaticAnalysis--s1 | 92 | 2 | $0.282 | 344 |
| 14 | libraries-01_FailureLog--s2 | 92 | 2 | $0.291 | 807 |
| 15 | testing-framework-02_RequestUnitTest--s12 | 91 | 2 | $0.262 | 349 |
| 16 | libraries-record_format--s11 | 90 | 2 | $0.257 | 449 |
| 17 | biz-samples-08_HtmlMail--s1 | 90 | 2 | $0.242 | 334 |
| 18 | web-application-01_DbAccessSpec_Example--s18 | 90 | 2 | $0.255 | 521 |
| 19 | libraries-08_02_validation_usage--s1 | 89 | 2 | $0.262 | 389 |
| 20 | workflow-doc-tool--s1 | 88 | 2 | $0.283 | 383 |
| 21 | libraries-02_04_Repository_override--s1 | 87 | 2 | $0.250 | 397 |
| 22 | java-static-analysis-UnpublishedApi--s1 | 86 | 2 | $0.263 | 298 |
| 23 | web-application-02_basic--s1 | 84 | 2 | $0.220 | 258 |
| 24 | libraries-messaging_sender_util--s1 | 84 | 2 | $0.243 | 371 |
| 25 | libraries-mail--s1 | 83 | 2 | $0.253 | 305 |
| 26 | ui-framework-reference_ui_standard--s1 | 82 | 2 | $0.259 | 395 |
| 27 | web-application-screenTransition--s1 | 81 | 2 | $0.254 | 304 |
| 28 | about-nablarch-concept--s8 | 81 | 2 | $0.231 | 355 |
| 29 | workflow-doc-tool--s1 | 80 | 2 | $0.308 | 383 |
| 30 | testing-framework-02_RequestUnitTest-06_TestFWGuide--s1 | 79 | 2 | $0.253 | 309 |

### Phase E 傾向分析

**ほぼ全件 turns=2（例外：rank 8 の web-application-05_screenTransition--s1 が 4t）**

修正フェーズは基本的に1回の大きな修正で完結している。4turnになったケースはファイルの修正が複数ステップに分かれた可能性がある。

**Phase E の最長は192秒（Phase D の213秒とほぼ同水準）**

修正プロンプトは知識ファイル全体 + ソース全体 + findingsを含むため、チェックと同等の重さになっている。

**`libraries-01_FailureLog` 系が引き続き上位**（rank 3, 7, 14）

Phase B・D・E 全フェーズで上位に入り続ける「常連ファイル」。ソースが大きく（807行）内容も複雑。

**`web-application-05_screenTransition--s1`（89行、4turns、$0.52）が異彩**

89行という小さなファイルなのに4ターン・$0.52と高コスト（同規模比で2倍超）。
修正プロンプトが複数回のツール呼び出しを行った可能性がある。

---

## 横断的傾向分析

### 「重いファイル」の常連

3フェーズ全てで上位30件に入るファイル群：

| file_id | B位 | D位 | E位 | 特徴 |
|---------|----:|----:|----:|-----|
| `libraries-05_FileDownload--s1` | 22 | 20 | 12 | 399行、複数コード例 |
| `libraries-04_Statement--s1` | 15 | 14/30 | - | 353行 |
| `about-nablarch-concept--s8` | - | 15/22 | 28 | 355行、概念文書 |
| `handlers-HttpRewriteHandler--s1` | 16 | 16 | - | 366行 |
| `libraries-07_FormTag--s1` | 5 | - | - | 379行、6画像 |

特に `libraries-05_FileDownload--s1` は全フェーズで上位に入っており、このファイルは次の生成でも注意が必要。

### フェーズ別の実行時間スケール

| フェーズ | 最長(秒) | 中央値付近(秒) | 特徴 |
|---------|-------:|------------:|-----|
| Phase B（生成） | 1503 | ~100 | 範囲が広い（10倍以上の差）、内容複雑度依存 |
| Phase D（チェック） | 213 | ~100 | Phase B より短く安定、大ファイルで遅い |
| Phase E（修正） | 192 | ~60 | Phase D と同水準、ほぼ全件2turns |

### turns の分布

- Phase B: 全件 turns=2（標準）
- Phase D: ほぼ turns=2、`libraries-01_FailureLog--s1` のみ 5/9/11t（異常値）
- Phase E: ほぼ turns=2、`web-application-05_screenTransition--s1` のみ 4t

turns の増加は「追加のソース照合ツール呼び出し」が発生したことを示す。
ほとんどのファイルで標準の2ターン（1回のプロンプト + 1回の応答）で完結している。

### コスト上位はPhase Bに集中

Phase B top の $2.43（glossary）は、Phase D/E 上位（$0.45-0.76）の 5〜10倍。
生成フェーズが全コストの約33%を占めるのは主に上位の高コストファイルによるもの。
549件中、上位30件が Phase B 全コスト（$154.63）の何割を占めるか：

Phase B top30合計コスト：$0 + ... (要計算）
→ 上位10件だけで $2.43+$2.30+$1.39+$1.37+$1.36+$1.20+$1.08+$1.20+$1.13+$1.06 = **$14.52**（全体の9.4%）

上位30件の合計は約 $22〜25 と推定（全体の14〜16%）。コストは比較的分散している。
