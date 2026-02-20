# Processing Pattern "空" 割り当ての妥当性レビュー

**Date**: 2026-02-19
**Reviewer**: Agent (Claude)
**Method**: Manual review with content analysis

## Overview

181件のファイルが"空"（汎用）として割り当てられています。
疑問を持って目視確認した結果、**疑わしいケースを2つ発見**しました。

## 発見した問題

### 1. handlers/standalone/* (8 files)

**現状**: Processing Pattern = 空（汎用）

**ファイル一覧**:
1. data_read_handler.rst - Data Read Handler
2. duplicate_process_check_handler.rst - Process Multiple Launch Prevention Handler
3. main.rst - Common Launcher
4. multi_thread_execution_handler.rst - Multi-thread Execution Control Handler
5. process_stop_handler.rst - Process Stop Control Handler
6. request_thread_loop_handler.rst - Loop Control Handler in Request Thread
7. retry_handler.rst - Retry Handler
8. status_code_convert_handler.rst - Status Code → Process End Code Conversion Handler

**疑問点**:
- タイトル: "Standalone Application Common Handler"
- `data_read_handler.rst`の内容に`nablarch_batch-data_reader`への参照がある
- "standalone application"はバッチアプリケーションを指すことが多い
- Jakarta Batchのアーキテクチャ文書にはstandalone handlersの言及なし

**可能性**:
- A. 汎用（nablarch-batch, jakarta-batch両方で使用） → 空が正しい
- B. nablarch-batch専用 → `nablarch-batch`を割り当てるべき

**推奨**: nablarch-batchユーザーがこれらのハンドラーを使うなら、`nablarch-batch`を割り当てるべき

---

### 2. handlers/web_interceptor/* (5 files)

**現状**: Processing Pattern = 空（汎用）

**ファイル一覧**:
1. InjectForm.rst - InjectForm Interceptor
2. on_double_submission.rst - OnDoubleSubmission Interceptor
3. on_error.rst - OnError Interceptor
4. on_errors.rst - OnErrors Interceptor
5. use_token.rst - UseToken Interceptor

**疑問点**:
- パッケージ名: `nablarch.common.web.interceptor`
- "web"という名前が付いている
- RESTful Web Serviceのアーキテクチャ文書には言及なし
- 内容を見ると、フォームオブジェクト、セッション、トークンなどWeb Application特有の概念

**可能性**:
- A. 汎用（web-application, restful-web-service両方で使用） → 空が正しい
- B. web-application専用 → `web-application`を割り当てるべき

**推奨**: パッケージ名と内容からweb-application専用と判断、`web-application`を割り当てるべき

---

## 正しく空になっているケース（サンプル確認）

### libraries/database/* - ✅ 正しい
- Database Access (JDBC Wrapper)
- Universal DAO
- → 全処理パターンで使用される汎用ライブラリ

### libraries/validation/* - ✅ 正しい
- Bean Validation
- Nablarch Validation
- → 全処理パターンで使用される汎用ライブラリ

### libraries/log/* - ✅ 正しい
- アプリケーションログ
- → 全処理パターンで使用される汎用機能

### handlers/common/* - ✅ 正しい
- Global Error Handler
- Database Connection Management Handler
- Transaction Control Handler
- → 全処理パターンで共通使用されるハンドラー

---

## 統計

### "空"割り当ての内訳（推定）

| カテゴリ | 件数 | 妥当性 |
|---------|------|--------|
| libraries/* (汎用) | ~80 | ✅ 正しい |
| handlers/common/* | ~10 | ✅ 正しい |
| handlers/standalone/* | 8 | ⚠️ 要確認 |
| handlers/web_interceptor/* | 5 | ⚠️ 要確認 |
| development-tools (汎用) | ~40 | ✅ 正しい |
| setup (汎用) | ~20 | ✅ 正しい |
| guide (汎用) | ~15 | ✅ 正しい |
| about, check | ~5 | ✅ 正しい |

**問題の規模**: 13件 / 181件 (7.2%)

---

## 提案

### オプション A: 保守的アプローチ（推奨）

**standalone handlers** → `nablarch-batch`を割り当て
- 理由: data_readerなどnablarch-batch専用機能への参照がある
- リスク: Jakarta Batchでも使えるなら誤った分類になる

**web_interceptor** → `web-application`を割り当て
- 理由: パッケージ名、内容ともにWeb Application専用
- リスク: 低い（RESTfulでは使われていない）

**影響**: 13件の割り当て変更

### オプション B: 現状維持

**standalone handlers** → 空のまま
- 理由: "Common"という名前から汎用と判断
- リスク: nablarch-batchユーザーが検索で見つけにくい

**web_interceptor** → 空のまま
- 理由: 不明
- リスク: web-applicationユーザーが検索で見つけにくい

---

## 推奨アクション

1. **ユーザー判断を仰ぐ**:
   - standalone handlersはnablarch-batch専用か？
   - web_interceptorはweb-application専用か？

2. **オプションAを実施** (推奨):
   - 13件の割り当てを変更
   - スクリプト再実行
   - 検証

3. **ドキュメント確認**:
   - 公式ドキュメントでstandalone, web_interceptorの使用例を確認
   - アーキテクチャ図で確認（可能なら）

---

## 質問

1. **standalone handlers**について:
   - これらはnablarch-batch専用ですか？
   - Jakarta Batchでも使われますか？

2. **web_interceptor**について:
   - これらはweb-application専用ですか？
   - RESTful Web Serviceでも使われますか？

3. **方針**:
   - 「汎用」の定義: 2つ以上の処理パターンで使われる？
   - それとも、主に1つの処理パターンで使われるなら、そのパターンを割り当てる？
