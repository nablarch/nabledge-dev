### Answer

Nablarchのウェブアプリケーションにおけるエラー処理の仕組みは、主に **HttpErrorHandler** と **HttpResponseHandler** の2つのハンドラが連携して動作します。

---

## エラーハンドリングの全体構造

### 1. HttpErrorHandler — 例外の種類に応じたログ出力とレスポンス生成

後続ハンドラ（アクションクラスなど）で発生した例外を捕捉し、種類に応じて以下のように処理します。

| 例外/エラー | ログレベル | HTTPステータス | 備考 |
|---|---|---|---|
| `NoMoreHandlerException` | INFO | 404 | 処理すべきアクションが存在しない。証跡ログとして記録 |
| `HttpErrorResponse` | ログなし | レスポンス内容による | バリデーション等の業務例外。ログ不要 |
| `HttpErrorResponse`（原因が`ApplicationException`） | ログなし | レスポンス内容による | エラーメッセージをリクエストスコープ（キー名`errors`）にセットし、Viewで参照可能にする |
| `Result.Error` | 設定による（FATAL） | ステータスコードによる | `writeFailureLogPattern`の正規表現がステータスコードにマッチした場合のみFATAL出力 |
| `StackOverflowError` | FATAL | 500 | データや実装バグに起因する可能性があるため障害扱い |
| 上記以外の例外/エラー | FATAL | 500 | 予期しない例外はすべて障害扱い |

`ApplicationException`のエラーメッセージをViewに渡す際のキー名はコンポーネント設定で変更可能です。

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- デフォルト "errors" を "messages" に変更する例 -->
  <property name="errorMessageRequestAttributeName" value="messages" />
</component>
```

---

### 2. HttpResponseHandler — エラー画面のフォワード

HttpErrorHandlerが生成したエラーレスポンス（404や500など）を受け取り、対応するエラー画面（JSPなど）にサーブレットフォワードします。

ただし、このハンドラ自身の処理中に以下が発生した場合は、フォワードも不可能と判断し、**固定のHTMLをステータス500で返します**（設定変更不可）。

- サーブレットフォワード時に`ServletException`が発生
- `RuntimeException`またはそのサブクラス
- `Error`またはそのサブクラス

この固定HTMLが返るのは極めてレアなケースです。どんな状況でもこのレスポンスを出してはいけないシステムでは、本ハンドラを参考に独自ハンドラの作成が推奨されます。

---

### 3. ログレベルの体系

フレームワーク全体のログ出力方針は以下の通りです。

| ログレベル | 用途 |
|---|---|
| FATAL/ERROR | 障害ログ。障害監視の対象。原則1件の障害につき1件出力 |
| WARN | 障害に連鎖して発生した例外（例：業務処理とトランザクション終了処理の両方で例外発生した場合の後者） |
| INFO | URLパラメータ改竄エラーや認可チェックエラーなど、アプリケーション実行状況に関するエラー |
| DEBUG | アプリケーション開発時のデバッグ情報 |
| TRACE | フレームワーク開発時のデバッグ情報 |

---

### 4. 処理フローのまとめ

```
リクエスト
  ↓
HttpErrorHandler（例外をキャッチしログ出力 + エラーレスポンス生成）
  ↓
HttpResponseHandler（エラー画面へフォワード or 固定HTML返却）
  ↓
エラー画面（JSP等）表示
```

エラー画面でのメッセージ表示は、`ApplicationException`の場合はリクエストスコープの`errors`（または設定したキー名）からエラーメッセージを取得して描画します。