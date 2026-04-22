# 機能詳細

## Nablarchの初期化

ウェブアプリケーションのNablarchの初期化 を参照。

## 入力値のチェック

* 入力値のチェック

## データベースアクセス

* データベースアクセス

## 排他制御

* ユニバーサルDAO

* universal_dao_jpa_optimistic_lock
* universal_dao_jpa_pessimistic_lock


> **Important:** 排他制御 機能は、クライアント(taglib)との連動が前提であるため、 HTTPメッセージングでは使用できない。

## URIとアクションクラスのマッピング

* HTTPリクエストディスパッチハンドラ

> **Tip:** HTTPメッセージングでは ルーティングアダプタ を使用できない。 HTTPメッセージングは、MOMメッセージング が提供する extdoc:`MessagingAction<nablarch.fw.messaging.action.MessagingAction>` でアクションクラスを作成するため、URIに応じてアクションクラスのメソッドを呼び分ける想定がないため。

## 国際化対応

静的リソースの多言語化対応については以下を参照。

* メッセージの多言語化
* コード名称の多言語化

## 認証

認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。

## 認可チェック

* permission_check

## エラー時に返却するレスポンス

* HTTPメッセージングエラー制御ハンドラ
